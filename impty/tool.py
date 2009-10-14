from cmdln import Cmdln, option, SubCmdOptionParser
from optparse import make_option, OptionGroup
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
import sys
from impty import Mappet, IMAPFail
import logging
from datetime import datetime
from os.path import expanduser

def option_group(title, opts_list, description=None):
    """Decorator to add option_group support to Cmdln.
    
    Based as closely as possible on cmdln.option"""
    def decorate(f):
        if not hasattr(f, "optparser"):
            f.optparser = SubCmdOptionParser()
        opts_group = OptionGroup(f.optparser, title, description)
        opts_group.add_options(opts_list)
        f.optparser.add_option_group(opts_group)
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

class ConfigFail(Exception):
    """Custom exception for problems in the config file"""
    pass

class PowerToyUI(Cmdln):

    opts_global = [
        make_option('-c', '--config-file', default='~/.impty_conf',
                    help='Specify location of configuration file (%default)'),
        make_option('-v', '--verbose', action='store_const', dest='log_level',
                    const=logging.INFO, help = 'Verbose output (INFO)'),
        make_option('-V', '--very-verbose', action='store_const',
                    dest='log_level', const=logging.DEBUG,
                    help = 'Verbose output (DEBUG)'),
    ]

    def cfg(self, opts):
        """Global option processing and configuration, much like an __init__
        """
        self.log = logging.getLogger('UI')
        logging.getLogger().setLevel(opts.ensure_value(
                                                    'log_level',logging.WARN))
        self.cfg = ConfigParser()
        self.cfg.read(expanduser(opts.config_file))

    def mappet_from_cfg(self, account):
        """Create a Mappet object from a configured account"""
        try:
            server = self.cfg.get(account,'server')
            username = self.cfg.get(account,'user')
        except NoSectionError:
            raise ConfigFail('No config for account: %s'%account)
        except NoOptionError, e:
            raise ConfigFail('No "%s" specified for account: %s'%(e.option,
                                                                    account))

        try:
            password = self.cfg.get(account,'passwd')
        except NoOptionError:
            raise ConfigFail('No password configured for account %s'%account)

        return Mappet(server, username, password)

    @options(opts_global)
    def do_count(self, sub_cmd, opts, *mboxs):
        """${cmd_name}
        Count number of messages in a mailbox
        
        ${cmd_usage}
        ${cmd_option_list}"""
        self.cfg(opts)
        for mbx in mboxs:
            try:
                account, mbox = mbx.split(':')
            except ValueError:
                print 'Invalid mailbox spec: %s'%mbx
                continue
            try:
                m = self.mappet_from_cfg(account)
                count = m.count(mbox, 'ALL')
            except ConfigFail, e:
                print e.message
            except IMAPFail, e:
                print e.message
            else:
                print mbx, count

def main():
    logging.basicConfig(level=logging.DEBUG)
    ptui = PowerToyUI()
    sys.exit(ptui.main())

if __name__ == '__main__':
    main()
