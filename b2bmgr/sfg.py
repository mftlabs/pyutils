#!/usr/bin/python
import os
import sys
import subprocess
from datetime import datetime
import tarfile
import shutil
import logging
import argparse

class sfg:
    def __init__(self, now, args):
        self.now = now
        self.args = args
        self.action = args.action.lower()
        self.swtype = args.swtype
        self.installation_dir = args.installdir
        self.backupdir = args.backupdir
        self.imcldir = args.imcldir
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
        subprocess.call(["amf", "stop", "sfg"])

    def is_directory_empty(self,directory_path):
        return len(os.listdir(directory_path)) == 0

    def create_tar_archive(self, source_folder, destination_file, exclude_folders=None):
        
        fileslist = []
        with tarfile.open(destination_file, "w:gz") as tar:
            for root, dirs, files in os.walk(source_folder):
                # Exclude top-level directories specified in exclude_dirs
                if root == source_folder and exclude_folders:
                    dirs[:] = [d for d in dirs if d not in exclude_folders]
                
                nofiles = True
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in fileslist:
                        tar.add(file_path, arcname=os.path.relpath(file_path, source_folder))
                        fileslist.append(file_path)
                        nofiles = False

                # Add all directories to the tar archive, including empty ones
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if self.is_directory_empty(dir_path):
                        tar.add(dir_path, arcname=os.path.relpath(dir_path, source_folder))

    def backup(self):
        properties_folder = os.path.join(self.installation_dir, "properties")
        files_to_backup = [
            "cdinterop-spoe-auth.properties",
            "cdinterop-spoe-policy.properties",
            "cdinterop-spoe-policy.properties.in"
        ]
        backupfiles = [
            "cdinterop-spoe-auth_{}.properties".format(self.now),
            "cdinterop-spoe-policy_{}.properties".format(self.now),
            "cdinterop-spoe-policy_{}.properties.in".format(self.now)
        ]
        for file_name in files_to_backup:
            logging.info("backup of {} is getting created in {} as {}".format(os.path.join(properties_folder, file_name), self.backupdir, backupfiles[files_to_backup.index(file_name)]))
            shutil.copy2(os.path.join(properties_folder, file_name), os.path.join(self.backupdir, backupfiles[files_to_backup.index(file_name)]))

        home_dir = self.homedir
        home_dir_formatted = home_dir.replace('/','_')
        
        if self.installation_dir:
            logging.info("backup of {} is getting created in {} as {}_opt_B2B_sys_{}.tar.gz".format(self.installation_dir, self.backupdir, self.hostname, self.now))
            self.create_tar_archive(self.installation_dir, "{}/{}_opt_B2B_sys_{}.tar.gz".format(self.backupdir, self.hostname, self.now), exclude_folders=['logs','backups'])
        else:
            logging.info("No installdir provided, aborting...")
            print("No installdir provided, aborting...")
            sys.exit(1)

        if self.appdatadir:
            logging.info("backup of {} is getting created in {} as {}_opt_B2B_appData_{}.sys.tar.gz".format(self.appdatadir, self.backupdir, self.hostname, self.now))
            self.create_tar_archive(self.appdatadir, "{}/{}_opt_B2B_appData_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now))
        else:
            logging.info("No appdatadir provided, aborting...")
            print("No appdatadir provided, aborting...")
            sys.exit(2)
        
        if self.ibmimsharedpath:
            logging.info("backup of {} is getting created in {} as {}_opt_B2B_IBMIMShared_{}.sys.tar.gz".format(self.ibmimsharedpath, self.backupdir, self.hostname, self.now))
            self.create_tar_archive(self.ibmimsharedpath, "{}/{}_opt_B2B_IBMIMShared_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now))
        else:
            logging.info("No ibmimsharedpath provided, aborting...")
            print("No ibmimsharedpath provided, aborting...")
            sys.exit(3)

        if self.IBM:
            logging.info("Backup of {} is getting created in {} as {}_opt_B2B_IBM_{}.sys.tar.gz".format(self.IBM, self.backupdir, self.hostname, self.now))
            self.create_tar_archive(self.IBM, "{}/{}_opt_B2B_IBM_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now))
        else:
            logging.info("No IBM provided, proceeding further without backup of IBM")

        if self.ibm:
            logging.info("Backup of {} is getting created in {} as {}_opt_B2B_ibm_{}.sys.tar.gz".format(self.ibm, self.backupdir, self.hostname, self.now))
            self.create_tar_archive(self.ibm, "{}/{}_opt_B2B_ibm_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now))
        else:
            logging.info("No ibm provided, proceeding further without backup of ibm")

        if "etc" in os.listdir(home_dir):    
            logging.info("Backup of {} is getting created in {} as {}_{}_etc_{}.sys.tar.gz".format(os.path.join(home_dir, "etc"), self.backupdir, self.hostname, home_dir_formatted, self.now))
            self.create_tar_archive(os.path.join(home_dir, "etc"), "{}/{}_{}_etc_{}.sys.tar.gz".format(self.backupdir, self.hostname, home_dir_formatted, self.now))
        else:
            logging.info("etc not present in {}, proceeding further without backup of etc".format(home_dir))
        
        if "var" in os.listdir(home_dir):
            logging.info("Backup of {} is getting created in {} as {}_{}_var_{}.sys.tar.gz".format(os.path.join(home_dir, "var"), self.backupdir, self.hostname, home_dir_formatted, self.now))
            self.create_tar_archive(os.path.join(home_dir, "var"), "{}/{}_{}_var_{}.sys.tar.gz".format(self.backupdir, self.hostname, home_dir_formatted, self.now))
        else:
            logging.info("var not present in {}, proceeding further without backup of var".format(home_dir))

    def upgrade(self):
        sandbox_config = os.path.join(self.installation_dir, "properties", "sandbox.cfg")
        with open(sandbox_config, "r") as file:
            lines = file.readlines()
            
        with open(sandbox_config, "w") as file:
            for line in lines:
                if "JCE_DIST_FILE" not in line:  
                    file.write(line)
                else:
                    logging.info("Removed {} from {}".format("JCE_DIST_FILE", sandbox_config))
                    continue

        subprocess.call([
            self.imcldir+"/imcl", 
            "-input", self.responsefilepath,
            "-dataLocation", self.appdatadir,
            "-log", self.log,
            "-acceptLicense"
        ])
        os.chdir( os.path.join(self.installation_dir, "bin"))
        subprocess.call([
            "./startCluster.sh", "1", "false"
        ])
        
        subprocess.call([
            "./InstallService.sh", self.jar
        ])

    def restore_with_cleanup_timestamp(self):
        properties_folder = os.path.join(self.installation_dir, "properties")
        if self.action == run:
+            files_to_restore = [
+                "cdinterop-spoe-auth_{}.properties".format(self.now),
+                "cdinterop-spoe-policy_{}.properties".format(self.now),
+                "cdinterop-spoe-policy_{}.properties.in".format(self.now)
+            ]
+        else:
+            files_to_restore = [
+                "cdinterop-spoe-auth_{}.properties".format(self.backuptime),
+                "cdinterop-spoe-policy_{}.properties".format(self.backuptime),
+                "cdinterop-spoe-policy_{}.properties.in".format(self.backuptime)
+            ]
        for file_name in files_to_restore:
            pos1 = file_name.find('_')
            pos2 = file_name.find('.',pos1)
            source_file_name = file_name[:pos1] + file_name[pos2:]
            logging.info("Restoring {} to {} as {}".format(os.path.join(self.backupdir, file_name), properties_folder, source_file_name))
            shutil.copy2(os.path.join(self.backupdir, file_name), os.path.join(properties_folder, source_file_name))

        subprocess.call(["sh", self.uiupdatescript])

    def start(self):
        subprocess.call(["amf", "start", "sfg"])
