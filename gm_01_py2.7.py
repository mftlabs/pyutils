#!/usr/bin/python
import os
import subprocess
from datetime import datetime
import time
import shutil
import logging
import argparse
import tarfile

class GMSoftwareUpgrade:
    def __init__(self,args):
        self.now = datetime.now().strftime("%Y%m%d%H%M%S")
        self.backupdir = args.backupdir
        self.action = (args.action).lower()
        self.backuptime = args.backuptime
        self.imdir = args.imdir
        self.responsefilepath = args.responsefilepath
        self.appdatadir = args.appdatadir
        self.ibmimsharedpath = args.ibmimsharedpath
        self.installation_dir = args.installdir
        self.log = args.log
        swtype = "gm"
        log_filename = os.path.join(self.backupdir, 'upgrade_sw_{}_{}.log'.format(swtype, self.now))
        logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self):
        swtype = "gm"

        if self.action == 'stop':
            logging.info('Stopping GM')
            self.stop_gm()
        elif self.action == 'backup':
            logging.info('Backup Directory:{}'.format(self.backupdir))
            self.backup()
        elif self.action == 'upgrade':
            logging.info('Starting Upgrade of {} at:{}'.format(swtype, self.now))
            self.upgrade()
        elif self.action == 'restore':
            logging.info('Restoring files from {} to {}/properties at:{}'.format(self.backupdir, self.installation_dir, self.now))
            self.restore()
        elif self.action == 'start':
            logging.info('Starting GM')
            self.start_gm()
        else:
            print("Missing/Invalid action parameter. Please verify!")


    def stop_gm(self):
        subprocess.call(["amf", "stop", "gm"])
        

    def tar_and_copy_folder(self, source_folder, destination_folder, tar_filename):
        with tarfile.open('{}'.format(os.path.join(destination_folder,tar_filename+'.tar.gz')), "w:gz") as tar:
            tar.add(source_folder, arcname=".")

        

    def backup(self):
        reaper_conf_dir = os.path.join(self.installation_dir, "apache-cassandra", "reaper", "conf")
        
        shutil.copy2(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.now))) # Use timestamp in backup file name

        
        netstat_output = subprocess.check_output("netstat -an | grep 2181 | grep TIME_WAIT | wc -l", shell=True)
        netstat_output = netstat_output.decode('utf-8')

        while netstat_output != "0\n":
            zerocountflag = False
            time.sleep(5)
            netstat_output = subprocess.check_output("netstat -an | grep 2181 | grep TIME_WAIT | wc -l", shell=True)
            netstat_output = netstat_output.decode('utf-8')
        
        if netstat_output == "0\n":
            zerocountflag = True

        if zerocountflag:
            for directory in ["ZOO", "CAS"]:
                self.tar_and_copy_folder(os.path.join(self.installation_dir, directory), self.backupdir, '{}_{}'.format(directory, self.now))
                
            self.tar_and_copy_folder(self.appdatadir, self.backupdir, '{}_{}'.format("appData", self.now))
            
            self.tar_and_copy_folder(os.path.join(self.ibmimsharedpath,"IBMIMShared"), self.backupdir, '{}_{}'.format("IBMIMShared", self.now))  
            
            self.tar_and_copy_folder(self.installation_dir, self.backupdir, '{}_{}'.format("gm", self.now))

    def upgrade(self):
        
        os.chdir(self.imdir)

        subprocess.call(["./imcl", "listInstalledPackages", "-verbose"])
        
        subprocess.call([
            "./imcl",
            "-input", self.responsefilepath,
            "-dataLocation", self.appdatadir,
            "-log", self.log, 
            "-acceptLicense"
        ])
        
        subprocess.call(["./imcl", "listInstalledPackages", "-verbose"])
        

    def restore(self):
        reaper_conf_dir = os.path.join(self.installation_dir, "apache-cassandra", "reaper", "conf")
        
        shutil.copy2(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), os.path.join(reaper_conf_dir, "cassandra-reaper.yaml_{}_patchfile.bkp".format(self.now)))  
        
        shutil.copy2(os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.backuptime)), os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"))
        

    def start_gm(self):
        subprocess.call(["amf", "start", "gm"])
        

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Automation of Software Upgrade for GM")
    parser.add_argument("-installdir", "-i", type=str, help="Installation Path")
    parser.add_argument("-backupdir", "-b", type=str, help="Backup Path")
    parser.add_argument("-action","-a", type=str,help="Type of action")
    parser.add_argument("-imdir", "-im", type=str, help="Backup Path")
    parser.add_argument("-responsefilepath", "-r", type=str, help="Response File Path")
    parser.add_argument("-appdatadir", "-d", type=str, help="App Data Path")
    parser.add_argument("-ibmimsharedpath", type=str, help="IBMIMSHARED Path")
    parser.add_argument("-backuptime", help="Time of backup for restoring backup files")
    parser.add_argument("-log", type=str, help="Log Path")
    args = parser.parse_args()
    swupgrade = GMSoftwareUpgrade(args)
    swupgrade.run()