from ConfigParser import ConfigParser
from cmdln import Cmdln, option, SubCmdOptionParser
from optparse import make_option, OptionGroup
import sys

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

    @option("", "--year", type='int', action="store", dest='funky')
    def do_count(self, mbox_spec, opts, *mboxs):
        """${cmd_name}
        Count number of messages in a mailbox
        
        ${cmd_usage}
        ${cmd_option_list}"""

        print locals()
        print self.do_count.optparser

def main():
    ptui = PowerToyUI()
    sys.exit(ptui.main())

if __name__ == '__main__':
    main()
