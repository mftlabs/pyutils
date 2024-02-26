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
        logging.basicConfig(filename=f'upgrade_sw_{timestamp}.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self,args):
        swtype = args.swtype
        installation_dir = args.installdir
        softwarepath = args.softwarepath
        backupdir = args.backupdir
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f'Starting Upgrade of {swtype} at:{timestamp}')
        logging.info(f'Software to Upgrade:{swtype}')
        logging.info(f'Software Path:{softwarepath}')
        logging.info(f'Backup Directory:{backupdir}')
        logging.info(f'Installation Directory:{installation_dir}')

        logging.info("Version check before upgrade")
        self.verify_version(installation_dir,swtype)
        self.stop_engine(installation_dir,swtype)
        self.tar_gz_folders(installation_dir,swtype,backupdir)
        self.upgrade_software(installation_dir,softwarepath,backupdir,swtype)
        self.start_engine(installation_dir,swtype)
        logging.info("Version check after upgrade")
        self.verify_version(installation_dir,swtype)

    def stop_engine(self,installation_dir,swtype):
        os.chdir(installation_dir+"/bin")
        current_directory = os.getcwd()
        if swtype == "ssp":
            result = subprocess.run(["./stopEngine.sh","mode=auto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "sspcm":
            result = subprocess.run(["./stopCM.sh","mode=auto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "seas":
            result = subprocess.run(["./stopSeas.sh","mode=auto"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "rps":
            result = subprocess.run(["./stopPs.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        output = result.stdout
        error_output = result.stderr
        logging.info(f'Output:\n{output}')
        logging.info(f'Error if any:\n{error_output}')

    def tar_gz_folders(self,installation_dir,swtype,backupdir):
        print(f"Creating a software backup:{swtype.upper()}")
        logging.info(f"Creating a software backup:{swtype.upper()}")
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%y%m%d%H%M%S%f")
        os.chdir(installation_dir)
        current_directory = os.getcwd()
        tar_filename = f"bkp_{swtype}_{formatted_datetime}.tar.gz"
        with tarfile.open(backupdir+'/'+tar_filename, "w:gz") as tar:
            tar.add(installation_dir, arcname=".")
            logging.info(f"Software backup created:{swtype}")

        if swtype == "ssp":
            cpfile_from = installation_dir+f"/bin/portal/pages.properties"
            try:
                shutil.copy(cpfile_from, f"{backupdir}/pages_{formatted_datetime}.properties")
                logging.info(f"File '{cpfile_from}' copied to '{backupdir}' successfully.")
            except Exception as e:
                logging.error(f"Error copying file: {e}")

    def upgrade_software(self,installation_dir,softwarepath,backupdir,swtype):
        filename = os.path.basename(softwarepath)
        swdirectory = os.path.dirname(softwarepath)
        stdout_logfile = swtype+"_upgrade_out.log"
        stderr_logfile = swtype+"_upgrade_err.log"
        os.chdir(swdirectory)
        try:
        # Open log files for writing
            with open(backupdir+"/"+stdout_logfile, 'w') as stdout_file, open(backupdir+"/"+stderr_logfile, 'w') as stderr_file:
                process = subprocess.Popen([f'./{filename}'], stdin=subprocess.PIPE, stdout=stdout_file, stderr=stderr_file, universal_newlines=True)
                print("Upgrade Started...")
                values_to_send = ["\n","1","\n", installation_dir,"\n", "Y","C","\n","\n","\n"]
                if swtype == "rps":
                    values_to_send = [installation_dir,"\n","Y","1","\n","\n","\n"]
                input_values = '\n'.join(values_to_send)
                stdout, stderr = process.communicate(input=input_values)
                if process.returncode == 0:
                    logging.info('Upgradation Completed ')
                    print('Upgradation Completed ')
        except Exception as e:
            logging.error("Error:", e)

    def start_engine(self,installation_dir,swtype):
        os.chdir(installation_dir+"/bin")
        if swtype == "ssp":
            result = subprocess.run(["./startEngine.sh"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "sspcm":
            result = subprocess.run(["./startCM.sh"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "seas":
            result = subprocess.run(["./startSeas.sh"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        elif swtype == "rps":
            os.chdir(installation_dir)
            result = subprocess.run(["./startupPs.sh"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #logging.info(f"Status: {out}")
        output = result.stdout
        error_output = result.stderr
        logging.info(f'Output:\n{output}')
        logging.info(f'Error if any:\n{error_output}')

    def verify_version(self,installation_dir,swtype):
        if swtype == 'ssp' or swtype == 'sspcm' or swtype == 'seas':
            os.chdir(installation_dir+"/conf")
        elif swtype == "rps":
                os.chdir(installation_dir)
        try:
            result = subprocess.run(['cat', "version.xml"], capture_output=True, text=True, check=True)
            logging.info(f'Current Version of {swtype}')
            logging.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error("Error:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automation of Software Upgrade")
    parser.add_argument("-swtype",  "-t",type=str, help="Name of Application")
    parser.add_argument("-installdir", "-i", type=str, help="Installation Path")
    parser.add_argument("-softwarepath","-s", type=str, help="Software Path")
    parser.add_argument("-backupdir", "-b", type=str, help="Backup Path")
    parser.add_argument("-verbose", "-v", action="store_true", help="Verbose")
    args = parser.parse_args()
    swupgrade = SoftwareUpgrade()
    swupgrade.run(args)
