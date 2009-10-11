from ConfigParser import ConfigParser
from opster import command, dispatch

msg_opts = [('n', 'new', False, 'Only new messages'),
            ('d', 'deleted', False, 'Only deleted messages'),
            ('', 'in-year', 0, 'Only messages from specified year')]

@command(usage='%name <mbox-spec>', options=msg_opts)
def count(mbox_spec, **opts):
    """Count number of messages in a mailbox"""
    print locals()

def main():
    dispatch()

if __name__ == '__main__':
    dispatch()
