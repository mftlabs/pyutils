#!/usr/bin/python
import os
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
        log_filename = os.path.join(self.backupdir, 'b2bmgr_{}_{}_{}.log'.format(self.swtype, self.action, self.now))
        logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # def run(self, args):
    #     installation_dir = args.installdir
    #     backupdir = args.backupdir
    #     self.stop()
    #     self.backup(installation_dir, backupdir)
    #     self.upgrade(installation_dir, backupdir)
    #     self.start()

        # logging.info('Starting Upgrade of {} at:{}'.format(swtype, now))
        # logging.info('Backup Directory:{}'.format(backupdir))
        # logging.info('Installation Directory:{}'.format(installation_dir))

        # self.stop_sfg()
        # self.backup(installation_dir, backupdir)
        # self.upgrade(installation_dir, backupdir)
        # self.restore(installation_dir, backupdir)
        # self.start_sfg()

    def stop(self):
        subprocess.call(["amf", "stop", "sfg"])

    def is_directory_empty(self,directory_path):
        return len(os.listdir(directory_path)) == 0

    def create_tar_archive(self, source_folder, destination_file, exclude_folders=None):
        fileslist = []
        dirslist = []
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
            shutil.copy2(os.path.join(properties_folder, file_name), os.path.join(self.backupdir, backupfiles[files_to_backup.index(file_name)]))

        home_dir = self.homedir
        home_dir_formatted = home_dir.replace('/','_')
        
        self.create_tar_archive(self.installation_dir, "{}/{}_opt_B2B_sys_{}.tar.gz".format(self.backupdir, self.hostname, self.now), exclude_folders=['logs','backups']),
        self.create_tar_archive(self.appdatadir, "{}/{}_opt_B2B_appData_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now)),
        self.create_tar_archive(self.ibmimsharedpath, "{}/{}_opt_B2B_IBMIMShared_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now)),
        
        self.create_tar_archive(self.IBM, "{}/{}_opt_B2B_IBM_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now)),
        self.create_tar_archive(self.ibm, "{}/{}_opt_B2B_ibm_{}.sys.tar.gz".format(self.backupdir, self.hostname, self.now)),

        self.create_tar_archive(os.path.join(home_dir, "etc"), "{}/{}_{}_etc_{}.sys.tar.gz".format(self.backupdir, self.hostname, home_dir_formatted, self.now)),
        self.create_tar_archive(os.path.join(home_dir, "var"), "{}/{}_{}_var_{}.sys.tar.gz".format(self.backupdir, self.hostname, home_dir_formatted, self.now))

    def upgrade(self):
        sandbox_config = os.path.join(self.installation_dir, "properties", "sandbox.cfg")
        with open(sandbox_config, "r") as file:
            lines = file.readlines()
            
        with open(sandbox_config, "w") as file:
            for line in lines:
                if "JCE_DIST_FILE" not in line:  
                    file.write(line)
                else:
                    continue

        subprocess.call([
            
            self.imdir+"/imcl", 
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
        files_to_restore = [
            "cdinterop-spoe-auth_{}.properties".format(self.backuptime),
            "cdinterop-spoe-policy_{}.properties".format(self.backuptime),
            "cdinterop-spoe-policy_{}.properties.in".format(self.backuptime)
        ]
        for file_name in files_to_restore:
            pos1 = file_name.find('_')
            pos2 = file_name.find('.',pos1)
            source_file_name = file_name[:pos1] + file_name[pos2:]
            shutil.copy2(os.path.join(self.backupdir, file_name), os.path.join(properties_folder, source_file_name))

        subprocess.call(["sh", self.uiupdatescript])

    def start(self):
        subprocess.call(["amf", "start", "sfg"])
