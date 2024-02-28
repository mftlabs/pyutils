#!/usr/bin/python
import os
import subprocess
from datetime import datetime
import tarfile
import sys
import argparse
import shutil
import logging

class SoftwareUpgrade:
    def __init__(self,args):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        backupdir = args.backupdir
        swtype = args.swtype
        log_filename = backupdir+'/upgrade_sw_{}_{}.log'.format(swtype,timestamp)
        logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self, args):
        swtype = args.swtype
        installation_dir = args.installdir
        softwarepath = args.softwarepath
        backupdir = args.backupdir
        alternate_tempfolder = args.alternate_tempfolder
        if swtype == "sspcm":
            os.environ['IATEMPDIR'] = alternate_tempfolder
            os.environ['TEMPDIR'] = alternate_tempfolder
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        logging.info('Starting Upgrade of {} at:{}'.format(swtype, timestamp))
        logging.info('Software to Upgrade:{}'.format(swtype))
        logging.info('Software Path:{}'.format(softwarepath))
        logging.info('Backup Directory:{}'.format(backupdir))
        logging.info('Installation Directory:{}'.format(installation_dir))

        self.verify_version(installation_dir, swtype)
        self.stop_engine(installation_dir, swtype)
        pid = self.get_pid(installation_dir,backupdir)
        if pid != None:
            logging.info('Doing hardstop on {} pid: {}'.format(swtype,pid))
            try:
                killprocess = subprocess.Popen(["kill", "-9", str(pid)], stdout=subprocess.PIPE)
                out, _ = killprocess.communicate()
                logging.info('Process with PID {} killed successfully.'.format(pid))
            except:
                logging.info('Error: Unable to kill process with PID {}.'.format(pid))
        self.tar_gz_folders(installation_dir, swtype, backupdir)
        self.upgrade_software(installation_dir, softwarepath, backupdir, swtype)
        if swtype == "ssp":
            self.copy_properties_file(installation_dir, swtype, backupdir)
        if swtype == "sspcm":
            self.modify_cmconfig(installation_dir)
        self.start_engine(installation_dir, swtype)
        logging.info("Version check after upgrade")
        self.verify_version(installation_dir, swtype)

    def execute_command(self, command, cwd=None):
        if cwd:
            os.chdir(cwd)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error_output = process.communicate()
        return output, error_output

    def stop_engine(self, installation_dir, swtype):
        cwd = os.path.join(installation_dir, "bin")
        if swtype == "ssp":
            command = "./stopEngine.sh mode=auto"
        elif swtype == "sspcm":
            command = "./stopCM.sh mode=auto"
        elif swtype == "seas":
            command = "./stopSeas.sh mode=auto"
        elif swtype == "rps":
            cwd = installation_dir
            command = "./stopPs.sh"
        output, error_output = self.execute_command(command, cwd)
        logging.info('Output:\n{}'.format(output))
        logging.info('Error if any:\n{}'.format(error_output))

    def tar_gz_folders(self, installation_dir, swtype, backupdir):
        logging.info("Creating a software backup:{}".format(swtype.upper()))
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%y%m%d%H%M%S%f")
        tar_filename = "bkp_{}_{}.tar.gz".format(swtype, formatted_datetime)
        with tarfile.open(os.path.join(backupdir, tar_filename), "w:gz") as tar:
            tar.add(installation_dir, arcname=".")
            logging.info("Software backup created:{}".format(swtype))
        if swtype == "ssp":
            cpfile_from = installation_dir+"/bin/portal/pages.properties"
            try:
                shutil.copy(cpfile_from, '{}/pages.properties'.format(backupdir))
                logging.info('File {} copied to {} successfully.'.format(cpfile_from,backupdir))
            except Exception as e:
                logging.error('Error copying file: {}'.format(e))

    def upgrade_software(self, installation_dir, softwarepath, backupdir, swtype):
        filename = os.path.basename(softwarepath)
        swdirectory = os.path.dirname(softwarepath)
        stdout_logfile = "{}_upgrade_out.log".format(swtype)
        stderr_logfile = "{}_upgrade_err.log".format(swtype)
        os.chdir(swdirectory)
        try:
            #with open(os.path.join(backupdir, stdout_logfile), 'w') as stdout_file, open(os.path.join(backupdir, stderr_logfile), 'w') as stderr_file:
            command = './{}'.format(filename)
            process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            input_values = "\n1\n{}\nY\nC\n\n\n\n".format(installation_dir) if swtype != "rps" else "\n{}\nY\n1\n\n\n".format(installation_dir)
            output, error_output = process.communicate(input=input_values)
            logging.info('Output for sw upgradation :\n{}'.format(output))
            logging.info('Error if any:\n{}'.format(error_output))
            if process.returncode == 0:
                logging.info('Upgradation Completed ')
        except Exception as e:
            logging.error("Error: {}".format(e))

    def start_engine(self, installation_dir, swtype):
        cwd = os.path.join(installation_dir, "bin")
        if swtype == "ssp":
            command = "./startEngine.sh"
        elif swtype == "sspcm":
            command = "./startCM.sh"
        elif swtype == "seas":
            command = "./startSeas.sh"
        elif swtype == "rps":
            cwd = installation_dir
            command = "./startupPs.sh"
        os.chdir(cwd)
        process = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
        output, error_output = process.communicate()
        logging.info('Output for start engine:\n{}'.format(output))
        logging.info('Error if any:\n{}'.format(error_output))

    def copy_properties_file(self,installation_dir, swtype, backupdir):
        cpfile_from = backupdir+"/pages.properties"
        try:
            shutil.copy(cpfile_from, '{}/bin/portal/pages.properties'.format(installation_dir))
            logging.info('File {} copied to {} successfully.'.format(cpfile_from,installation_dir+"/bin/portal"))
        except Exception as e:
            logging.error('Error copying file: {}'.format(e))

    def check_file_exists(self,file_path):
        return os.path.exists(file_path)

    def modify_cmconfig(self,installation_dir):
        file_path = installation_dir+"/conf/cmconfig.properties" 
        content = []
        lines=None
        with open(file_path,'r') as file:
            lines = file.readlines()
            for line in lines:
                content.append(line.strip())
        keys = ["cm.bypass.host.header.check=true","skip.local.hostnames.lookup=true"]        
        for key in keys:
            content.append(key)
        with open(file_path,'w') as file:
            for line in content:
                file.write(line)
                file.write('\n')    
        
         


    def verify_version(self, installation_dir, swtype):
        cwd = os.path.join(installation_dir, "conf") if swtype in ['ssp', 'sspcm', 'seas'] else installation_dir
        command = 'cat version.xml'
        output, error_output = self.execute_command(command, cwd)
        logging.info('Current Version of {}'.format(swtype))
        logging.info(output)

    def get_pid(self,process_name,backupdir):
        # Run the ps -ef | grep command
        command = "ps -ef | grep {}".format(process_name)
        ps_output = subprocess.check_output(command, shell=True).decode("utf-8")

        ps_lines = ps_output.split('\n')
        for line in ps_lines:
            if process_name in line and backupdir not in line and '--color=auto' not in line and 'grep' not in line:
                # Split the line by whitespace and get the PID (second column)
                pid = line.split()[1]
                return pid

        # If the process is not found, return None
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automation of Software Upgrade")
    parser.add_argument("-swtype", "-t", type=str, help="Name of Application")
    parser.add_argument("-installdir", "-i", type=str, help="Installation Path")
    parser.add_argument("-softwarepath", "-s", type=str, help="Software Path")
    parser.add_argument("-backupdir", "-b", type=str, help="Backup Path")
    parser.add_argument("-alternate_tempfolder", "-f", type=str, help="Alternate Temp Folder")
    parser.add_argument("-verbose", "-v", action="store_true", help="Verbose")

    args = parser.parse_args()
    swupgrade = SoftwareUpgrade(args)
    swupgrade.run(args)

