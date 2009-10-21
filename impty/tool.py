from cmdln import Cmdln, option, SubCmdOptionParser
from optparse import make_option, OptionGroup
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
import sys
from impty import Mappet, IMAPFail
import logging
from datetime import datetime, date
from calendar import monthrange
from os.path import expanduser
import socket

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

    date_grp = {
        'title': 'Select messages by date.',
        'description': '  Used to select messages by numeric date.',
        'opts_list': [
            make_option('','--before', action="store_true"),
            make_option('','--since', action="store_true"),
            make_option('-y','--year', type='int'),
            make_option('-m','--month', type='int'),
            make_option('-d','--day', type='int'),
        ],
    }

    opts_global = [
        make_option('-t', '--timeout', default=10, type='int',
                    help='Time in seconds to wait for servers (%default)'),
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
        socket.setdefaulttimeout(opts.timeout)
        self.log = logging.getLogger('UI')
        logging.getLogger().setLevel(opts.ensure_value('log_level',
                                                        logging.WARN))
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

    def floor_opt_date(self, opts):
        now = datetime.now()
        year = opts.ensure_value('year', now.year)
        # The method ensure_value sets the value on the options object!
        # Cannot use ensure_value here! It will mess up the ceil function...
        if opts.month is None:
            month = 1
        else:
            month = opts.month
        day = opts.ensure_value('day', 1)
        return date(year,month,day).strftime('%d-%b-%Y')

    def ceil_opt_date(self, opts):
        # Only ever called if there is no day set
        now = datetime.now()
        year = opts.ensure_value('year', now.year)
        month = opts.ensure_value('month', 12)
        day = monthrange(year, month)[1]
        return date(year,month,day).strftime('%d-%b-%Y')

    def spec_from_opts(self, opts):
        if opts.year or opts.month or opts.day:
            if opts.before or opts.since:
                # Dates need to be floored for before/since
                ds = self.floor_opt_date(opts)
                if opts.since:
                    return '(SINCE %s)'%ds
                else:
                    return '(BEFORE %s)'%ds
            else:
                if opts.day is not None:
                    # If the day is set, it's a defined date and we can assume
                    # the year and month
                    now = datetime.now()
                    day = opts.ensure_value('day', now.day)
                    month = opts.ensure_value('month', now.month)
                    year = opts.ensure_value('year', now.year)
                    return '(ON %s)'%date(year,month,day).strftime('%d-%b-%Y')
                else:
                    # If the day is not set, we are dealing with a range
                    floor = self.floor_opt_date(opts)
                    ceil = self.ceil_opt_date(opts)
                    return '(SINCE %s BEFORE %s)'%(floor, ceil)

        return 'ALL'

    @options(opts_global)
    def do_list(self, sub_cmd, opts, *accs):
        """List mailboxs on an account

        ${cmd_usage}
        ${cmd_option_list}"""


    @options(opts_global)
    @option_group(**date_grp)
    def do_count(self, sub_cmd, opts, *mbxs):
        """Count number of messages in a mailbox
        
        ${cmd_usage}
        ${cmd_option_list}"""
        self.cfg(opts)
        try:
            mesg_spec = self.spec_from_opts(opts)
        except ValueError:
            sys.exit('Invalid date specified!')
        self.log.debug('mesg_spec: %s'%mesg_spec)
        for mbx in mbxs:
            try:
                account, mbox = mbx.split(':')
            except ValueError:
                print 'Invalid mailbox spec: %s'%mbx
                continue
            try:
                m = self.mappet_from_cfg(account)
                count = m.count(mbox, mesg_spec)
            except ConfigFail, e:
                print e.message
            except IMAPFail, e:
                print e.message
            else:
                print mbx, count

    @options(opts_global)
    def do_copy(self, sub_cmd, opts, src_mbx, dst_mbx):
        """Copy messages from one mailbox to another

        ${cmd_usage}
        ${cmd_option_list}"""
        self.cfg(opts)
        # Parse mbx specs
        try:
            s_acc, s_mbx = src_mbx.split(':')
        except ValueError:
            print 'Invalid source mailbox spec: %s'%dst_mbx
        try:
            d_acc, d_mbx = dst_mbx.split(':')
        except ValueError:
            print 'Invalid destination mailbox spec: %s'%dst_mbx
        if s_acc != d_acc:
            sys.exit('account to account copy not supported yet')
        # Get mbx
        try:
            mpt = self.mappet_from_cfg(s_acc)
        except IMAPFail, e:
            sys.exit(e)

        # Do copy
        try:
            mpt.copy(s_mbx,d_mbx,'1:*')
        except IMAPFail, e:
            sys.exit(e)

def main():
    logging.basicConfig(level=logging.DEBUG)
    ptui = PowerToyUI()
    sys.exit(ptui.main())

if __name__ == '__main__':
    main()
