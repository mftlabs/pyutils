#!/usr/bin/python
import os
import subprocess
from datetime import datetime
import shutil
import logging
import argparse
import tarfile

class gm:
    def __init__(self,  now, args):
        self.now = now
        self.args = args
        self.action = args.action.lower()
        self.swtype = args.swtype
        self.backupdir = args.backupdir
        self.imdir = args.imdir
        self.backuptime = args.backuptime
        self.responsefilepath = args.responsefilepath
        self.appdatadir = args.appdatadir
        self.ibmimsharedpath = args.ibmimsharedpath
        self.installation_dir = args.installdir
        self.log = args.log
        self.hostname = os.environ.get('HOSTNAME')
        self.homedir = os.environ.get('HOME')
        log_filename = os.path.join(self.backupdir, 'b2bmgr_{}_{}_{}.log'.format(self.swtype, self.action, self.now))
        logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self, args):
        installation_dir = args.installdir
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S") 
        logging.info('Starting Upgrade of {} at:{}'.format(swtype, self.now))
        logging.info('Backup Directory:{}'.format(self.backupdir))
        logging.info('Installation Directory:{}'.format(installation_dir))
        self.stop_gm()
        self.backup()
        self.upgrade()
        self.start_gm()

    def stop(self):
        subprocess.call(["amf", "stop", "gm"])

    def tar_and_copy_folder(self, source_folder, destination_folder, tar_filename):
        with tarfile.open('{}'.format(os.path.join(destination_folder,tar_filename+'.tar.gz')), "w:gz") as tar:
            tar.add(source_folder, arcname=".")

    def backup(self):
        reaper_conf_dir = os.path.join(self.installation_dir, "apache-cassandra", "reaper", "conf")
        shutil.copy2(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.now)))

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


    def restore_with_cleanup_timestamp(self):
        reaper_conf_dir = os.path.join(self.installation_dir, "apache-cassandra", "reaper", "conf")
        shutil.copy2(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), os.path.join(reaper_conf_dir, "cassandra-reaper.yaml_{}_patchfile.bkp".format(self.now)))
        
        source_file_name = os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.backuptime))

        shutil.copy2(source_file_name, os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"))

    def start(self):
        subprocess.call(["amf", "start", "gm"])

