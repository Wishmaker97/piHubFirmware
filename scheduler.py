from dotenv import load_dotenv
import os
import requests
from requests.exceptions import HTTPError
from uuid import getnode as get_mac
from CronJobManager import CronJobManager
import logging.handlers as handlers
import logging
import datetime
import git
import subprocess


if __name__ == "__main__":

    formatter = logging.Formatter('%(asctime)s program_name [%(process)d]: %(message)s', '%b %d %H:%M:%S')    
    log_handler = handlers.TimedRotatingFileHandler(r"logfiles/scheduler/logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    logging.info(msg=F"Start Script to send timed report @ {datetime.datetime.utcnow()} (UTC)")

    load_dotenv() 

    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
    access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

    try:        
        ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
        response = requests.get(access_url)

        ## parse response as json object to extract configuration
        config_json = response.json()

        api_update_scheduler_string = config_json['update_scheduler_cronjob']
        firmware_version = config_json['firmware_version']
        ntp_server = config_json['ntp_server']
        
        ## initialize CronJob instance to handle update of cronjobs
        job_worker = CronJobManager()

        ## update cronjob if needed
        if job_worker.checkIfScheduleIsDifferent(api_update_scheduler_string):            
            logging.info(msg=F"Removing existing Cronjobs that schedule Cronjobs that handle 'service_worker.py' @ {datetime.datetime.utcnow()} (UTC)")
            job_worker.removeExistingJobs()

            logging.info(msg=F"Adding new Cronjob that schedule Cronjobs that handle 'service_worker.py' @ {datetime.datetime.utcnow()} (UTC)")
            job_worker.addNewJob(api_update_scheduler_string)
        
        else:
            logging.info(msg=F"No need to update Cronjob (no changes) @ {datetime.datetime.utcnow()} (UTC)")

        ## update git repo if needed
        try:
            git_repo = git.Repo(search_parent_directories=True)
            current_sha = git_repo.head.object.hexsha
            print(current_sha)

            if(str(current_sha)==str(firmware_version)):
                print("hash is same as current")
            else:
                os.system(F"cd ~/server/piHubFirmware && git pull origin main {firmware_version}")
                daemon_reload = subprocess.Popen(['sudo', '-S', 'systemctl', 'daemon-reload'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}'.encode())
                print(daemon_reload)
                remote_request = subprocess.Popen(['sudo', '-S', 'systemctl', 'restart','remote_request.service'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}'.encode())
                print(remote_request)

        except Exception as err:
            logging.exception(msg=F"error occurred during git operation: {err} @{datetime.datetime.utcnow()} (UTC)")
        
        ## update ntp server
        try:
            is_server_different = False
            with open("/etc/ntp.conf", "rw+") as f:
                lines = f.readlines()
                if F"server {ntp_server}" not in lines :
                    is_server_different = True

            if(is_server_different):
                print("update ntp server")
            else:
                print("DONT update ntp server")

        except Exception as err:
            logging.exception(msg=F"error occurred during ntp update : {err} @{datetime.datetime.utcnow()} (UTC)")

    except HTTPError as http_err:
        logging.exception(msg=F"HTTP error occurred: {http_err} @{datetime.datetime.utcnow()} (UTC)")

    except Exception as err:
        logging.exception(msg=F"Other error occurred: {err} @{datetime.datetime.utcnow()} (UTC)")