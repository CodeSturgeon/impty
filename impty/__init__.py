from imaplib import IMAP4
import logging
import socket

class IMAPFail(Exception):
    pass

class IMAPMailboxNotFound(IMAPFail):
    pass

class Mappet(object):
    """Exception throwing abstraction wrapper for imaplib's IMAP4 class.

    All _name methods assume a _refresh has been run before they are called"""
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.log = logging.getLogger('Mappet')
        self._cnx = None

    def _connect(self):
        """Internal command to force creation of new autenticated connection"""
        self.log.info('Connecting to %s as %s'%(self.server, self.username))
        try:
            self._cnx = IMAP4(self.server)
        except socket.timeout:
            raise IMAPFail('Server could not be contacted: %s'%self.server)
        status, data = self._cnx.login(self.username, self.password)
        if status != 'OK':
            self.log.warn('LOGIN FAIL: [%s] %s'%(status, data))
            raise IMAPFail('Login failure for %s@%s'%(self.username,
                                                        self.server))

    def _select(self, mailbox):
        """Select a mailbox - assumes current connection"""
        status, data = self._cnx.select(mailbox)
        if status != 'OK':
            self.log.warn('SELECT FAIL: [%s] %s'%(status, data))
            raise IMAPMailboxNotFound('Mailbox not found (%s)'%mailbox)

    def _refresh(self):
        """Ensure a fresh connection"""
        if self._cnx is None:
            self._connect()
            return
        # Check for stale connection
        try:
            self._cnx.noop()
        except (m.error, m.abort):
            self._connect()

    def _search(self, message_spec):
        """Do a search and return a list of message numbers"""
        status, data = self._cnx.search('UTF-8', message_spec)
        if status != 'OK':
            self.log.warn('SEARCH FAIL: [%s] %s'%(status, data))
            raise IMAPFail('Search failed (%s)'%data[0])
        if data[0] == '':
            return []
        return data[0].split(' ')

    def _copy(self, to_box, message_spec):
        """IMAP copy - expects fresh selected connection"""
        status, data = self._cnx.copy(message_spec, to_box)
        if status != 'OK':
            raise IMAPFail('Copy failed (%s)'%data[0])

    def count(self, mailbox, message_spec='ALL'):
        """High level count method"""
        self._refresh()
        self._select(mailbox)
        message_list = self._search(message_spec)
        return len(message_list)

    def copy(self, from_box, to_box, message_spec='ALL')
        """High level copy command"""
        self._refresh()
        # Select the _to_ box to make sure it is there
        self._select(to_box)
        self._select(from_box)
        self._copy(to_box, message_spec)
