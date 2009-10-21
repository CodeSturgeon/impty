# IMAP4 Power Toy

## Overview
This a command line tool 'impty' based on a wrapper to make the python standard library module imaplib.

## Functionality
Implemented

- Mailbox listing
- Counting messages in a mailbox, optional matching criteria
- Date based message selection criteria
- Simple copy (within an account)

Planned

- Deleting
- Delete after copy (move)
- Copy between accounts
- Message set specification
- Message set from selection criteria

## Usage
Most usage can be found through the builtin help 'impty -h'.  
You **MUST** have a config file '~/.impty_conf'.

### Configuration file
INI style, implemented with ConfigParser.

    [accountname]
    server = imap.server.addr
    name = your_imap_username
    passwd = your_imap_password

### Mailbox specification
Commands like copy and count require mailboxs to be specified in the following format...

    acc_name:mailbox_path

Examples...

    impty copy main:inbox main:Archive.inbox
    impty count personal:Groups.Family.Sister
