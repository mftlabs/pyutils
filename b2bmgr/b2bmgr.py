#!/usr/bin/python
import argparse
import os
from datetime import datetime



class B2BManager(object):
    def __init__(self, args):
        self.args = args
        self.now = datetime.now().strftime("%Y%m%d%H%M%S")
        self.action = args.action.lower()
        self.installdir = args.installdir
        self.backupdir = args.backupdir
        self.imdir = args.imdir
        self.responsefilepath = args.responsefilepath
        self.appdatadir = args.appdatadir
        self.ibmimsharedpath = args.ibmimsharedpath
        self.IBM = args.IBM
        self.ibm = args.ibm
        self.uiupdatescript = args.uiupdatescript
        self.jar = args.jar
        self.log = args.log
        self.backuptime = args.backuptime
        self.hostname = os.environ.get('HOSTNAME')
        self.homedir = os.environ.get('HOME')
        self.swtype = args.swtype

    def run(self):
        app = None
        module = __import__(self.swtype, fromlist=[self.swtype])
        klass = getattr(module, self.swtype)
        app = klass(self.now, self.args)
        if app and self.action:
            if self.action == 'start':
                app.start()
            elif self.action == 'stop':
                app.stop()
            elif self.action == 'backup':
                app.backup()
            elif self.action == 'upgrade':
                app.upgrade()
            elif self.action == 'restore':
                app.restore_with_cleanup_timestamp()
            elif self.action == 'run':
                app.run(self.args)
            else:
                print("Invalid action. Please verify!")
                return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a script to automate the B2B upgrade process.')
    parser.add_argument('-action', help='Action to be performed')
    parser.add_argument('-swtype', help='Action to be performed')
    
    parser.add_argument('-installdir', help='The installation directory of the B2B product')
    parser.add_argument('-backupdir', help='The directory where the backup files are located')
    parser.add_argument('-imdir', help='The path to the Installation Manager')
    parser.add_argument('-responsefilepath', help='The path to the response file')
    parser.add_argument('-appdatadir', help='The path to the appData directory')
    parser.add_argument("-ibmimsharedpath", type=str, help="IBMIMSHARED Path")
    parser.add_argument("-IBM", type=str, help="IBM Path")
    parser.add_argument("-ibm", type=str, help="ibm Path")
    parser.add_argument("-uiupdatescript", help="SFG UI Update Script")
    parser.add_argument('-backuptime', help='Time of backup for restoring backup files')
    parser.add_argument('-log', help='The path to the log file')
    parser.add_argument('-jar',  help='The path to the jar file')
    
    print("B2B Manager started.")
    args = parser.parse_args()
    b2bmgr = B2BManager(args)
    if b2bmgr.swtype and b2bmgr.action:
        print('Running Service: {} with Action: {}'.format(b2bmgr.swtype.upper(), b2bmgr.action))
        b2bmgr.run()
    else:
        print('Invalid Service or Action. Please verify!')
    print("B2B Manager stopped.")