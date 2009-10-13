from imaplib import IMAP4
import logging

class IMAPFail(Exception):
    pass

class Mappet(object):
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.log = logging.getLogger('Mappet')
        self._cnx = None

    def _connect(self):
        """Internal command to force creation of new autenticated connection"""
        self.log.info('Connecting to %s as %s'%(self.server, self.username))
        self._cnx = IMAP4(self.server)
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
            raise IMAPFail('Mailbox not found (%s)'%mailbox)

    def cnx(self):
        """Ensure a fresh connection"""
        if self._cnx is None:
            self._connect()

    def _search(self, message_spec):
        """Do a search and return a list of message numbers"""
        status, data = self._cnx.search('UTF-8', message_spec)
        if status != 'OK':
            self.log.warn('SEARCH FAIL: [%s] %s'%(status, data))
            raise IMAPFail('Mailbox not found (%s)'%mbox)
        return data[0].split(' ')

    def count(self, mailbox, message_spec='ALL'):
        self.cnx()
        self._select(mailbox)
        message_list = self._search(message_spec)
        return len(message_list)