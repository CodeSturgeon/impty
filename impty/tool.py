from cmdln import Cmdln, option, SubCmdOptionParser
from optparse import make_option, OptionGroup
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
import sys
from impty import Mappet, IMAPFail
import logging

def option_group(opts_group):
    """Decorator to add option_group support to Cmdln.
    
    Based as closely as possible on cmdln.option"""
    def decorate(f):
        if not hasattr(f, "optparser"):
            f.optparser = SubCmdOptionParser()
        f.optparser.add_options(opts_group)
        return f
    return decorate

def options(opts_list):
    """Decorator to add options support to Cmdln.
    
    Based as closely as possible on cmdln.option"""
    def decorate(f):
        if not hasattr(f, "optparser"):
            f.optparser = SubCmdOptionParser()
        f.optparser.add_options(opts_list)
        return f
    return decorate

class PowerToyUI(Cmdln):

    def cfg(self):
        self.log = logging.getLogger('UI')
        self.cfg = ConfigParser()
        self.cfg.read('/Users/fish/.impty_conf')

    @option("", "--year", type='int', action="store", dest='funky')
    def do_count(self, sub_cmd, opts, *mboxs):
        """${cmd_name}
        Count number of messages in a mailbox
        
        ${cmd_usage}
        ${cmd_option_list}"""
        self.cfg()
        for mbx in mboxs:
            account, mbox = mbx.split(':')
            try:
                server = self.cfg.get(account,'server')
            except NoSectionError:
                print 'No config for account: %s'%account
            except NoOptionError:
                print 'No server configured for account %s'%account
            try:
                username = self.cfg.get(account,'user')
            except NoOptionError:
                print 'No username configured for account %s'%account
            try:
                password = self.cfg.get(account,'passwd')
            except NoOptionError:
                print 'No password configured for account %s'%account
            try:
                m = Mappet(server, username, password)
                count = m.count(mbox)
            except IMAPFail, e:
                print e
            else:
                print mbx, count
        #print sub_cmd, mboxs

def main():
    logging.basicConfig(level=logging.DEBUG)
    ptui = PowerToyUI()
    sys.exit(ptui.main())

if __name__ == '__main__':
    main()
