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
        self.imcldir = args.imcldir
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
        logging.info('Starting Upgrade of {} at:{}'.format(self.swtype, self.now))
        logging.info('Installation Directory:{}'.format(self.installation_dir))
        logging.info('Backup Directory:{}'.format(self.backupdir))
        

        logging.info("About to stop {}".format(self.swtype))
        self.stop()
        logging.info("Completed {} stop".format(self.swtype))
        
        logging.info("About to start backup process of {}".format(self.swtype))
        self.backup()
        logging.info("Completed {} backup process".format(self.swtype))
        
        logging.info("About to start upgrade process of {}".format(self.swtype))
        self.upgrade()
        logging.info("Completed {} upgrade process".format(self.swtype))
        
        logging.info("About to start restore process of {}".format(self.swtype))
        self.restore_with_cleanup_timestamp()
        logging.info("Completed {} restore process".format(self.swtype))
        
        logging.info("About to start {}".format(self.swtype))
        self.start()
        logging.info("Completed {} start".format(self.swtype))

    def stop(self):
        subprocess.call(["amf", "stop", "gm"])

    def tar_and_copy_folder(self, source_folder, destination_folder, tar_filename):
        with tarfile.open('{}'.format(os.path.join(destination_folder,tar_filename+'.tar.gz')), "w:gz") as tar:
            tar.add(source_folder, arcname=".")

    def backup(self):
        reaper_conf_dir = os.path.join(self.installation_dir, "apache-cassandra", "reaper", "conf")

        logging.info("Backup of {} is getting created in {} as {}".format(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.now)))
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
                logging.info("Backup of {} is getting created in {} as {}".format(os.path.join(self.installation_dir, directory), self.backupdir, '{}_{}'.format(directory, self.now)))
                self.tar_and_copy_folder(os.path.join(self.installation_dir, directory), self.backupdir, '{}_{}'.format(directory, self.now))

            logging.info("Backup of {} is getting created in {} as {}".format(self.appdatadir, self.backupdir, '{}_{}'.format("appData", self.now)))    
            self.tar_and_copy_folder(self.appdatadir, self.backupdir, '{}_{}'.format("appData", self.now))
            
            logging.info("Backup of {} is getting created in {} as {}".format(self.ibmimsharedpath, self.backupdir, '{}_{}'.format("IBMIMShared", self.now)))
            self.tar_and_copy_folder(self.ibmimsharedpath, self.backupdir, '{}_{}'.format("IBMIMShared", self.now))  
            
            logging.info("Backup of {} is getting created in {} as {}".format(self.installation_dir, self.backupdir, '{}_{}'.format("gm", self.now)))
            self.tar_and_copy_folder(self.installation_dir, self.backupdir, '{}_{}'.format("gm", self.now))
            
    def upgrade(self):
        os.chdir(self.imcldir)
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

        logging.info("Backup of {} is getting created in {} as patchfile {}".format(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), reaper_conf_dir, "cassandra-reaper.yaml_{}_patchfile.bkp".format(self.now)))
        shutil.copy2(os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"), os.path.join(reaper_conf_dir, "cassandra-reaper.yaml_{}_patchfile.bkp".format(self.now)))
        
        if self.action == run:
+            source_file_name = os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.now))
+        
+        else:
+            source_file_name = os.path.join(self.backupdir, "cassandra-reaper.yaml_{}.bkp".format(self.backuptime))

        logging.info("Restoring {} to {} as {}".format(source_file_name, reaper_conf_dir, "cassandra-reaper.yaml"))
        shutil.copy2(source_file_name, os.path.join(reaper_conf_dir, "cassandra-reaper.yaml"))

    def start(self):
        subprocess.call(["amf", "start", "gm"])

