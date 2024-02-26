import os
import subprocess
from datetime import datetime
import tarfile
import sys
import argparse
import shutil
import logging

class SoftwareUpgrade:
    def __init__(self):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        log_filename = 'upgrade_sw_{}.log'.format(timestamp)
        logging.basicConfig(filename=log_filename, filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self, args):
        swtype = args.swtype
        installation_dir = args.installdir
        softwarepath = args.softwarepath
        backupdir = args.backupdir
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        logging.info('Starting Upgrade of {} at:{}'.format(swtype, timestamp))
        logging.info('Software to Upgrade:{}'.format(swtype))
        logging.info('Software Path:{}'.format(softwarepath))
        logging.info('Backup Directory:{}'.format(backupdir))
        logging.info('Installation Directory:{}'.format(installation_dir))

        self.verify_version(installation_dir, swtype)
        self.stop_engine(installation_dir, swtype)
        self.tar_gz_folders(installation_dir, swtype, backupdir)
        self.upgrade_software(installation_dir, softwarepath, backupdir, swtype)
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

    def upgrade_software(self, installation_dir, softwarepath, backupdir, swtype):
        filename = os.path.basename(softwarepath)
        swdirectory = os.path.dirname(softwarepath)
        stdout_logfile = "{}_upgrade_out.log".format(swtype)
        stderr_logfile = "{}_upgrade_err.log".format(swtype)
        os.chdir(swdirectory)
        try:
            with open(os.path.join(backupdir, stdout_logfile), 'w') as stdout_file, open(os.path.join(backupdir, stderr_logfile), 'w') as stderr_file:
                command = './{}'.format(filename)
                process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=stdout_file, stderr=stderr_file)
                input_values = "\n1\n{}\nY\nC\n\n\n\n".format(installation_dir) if swtype != "rps" else "{}\nY\n1\n\n\n\n".format(installation_dir)
                process.communicate(input=input_values)
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
        output, error_output = self.execute_command(command, cwd)
        logging.info('Output:\n{}'.format(output))
        logging.info('Error if any:\n{}'.format(error_output))

    def verify_version(self, installation_dir, swtype):
        cwd = os.path.join(installation_dir, "conf") if swtype in ['ssp', 'sspcm', 'seas'] else installation_dir
        command = 'cat version.xml'
        output, error_output = self.execute_command(command, cwd)
        logging.info('Current Version of {}'.format(swtype))
        logging.info(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automation of Software Upgrade")
    parser.add_argument("-swtype", "-t", type=str, help="Name of Application")
    parser.add_argument("-installdir", "-i", type=str, help="Installation Path")
    parser.add_argument("-softwarepath", "-s", type=str, help="Software Path")
    parser.add_argument("-backupdir", "-b", type=str, help="Backup Path")
    parser.add_argument("-verbose", "-v", action="store_true", help="Verbose")
    args = parser.parse_args()
    swupgrade = SoftwareUpgrade()
    swupgrade.run(args)
