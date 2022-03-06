from dotenv import load_dotenv
import os
import requests
from requests.exceptions import HTTPError
from uuid import getnode as get_mac
from CronJobManager import CronJobManager
import logging.handlers as handlers
import logging
import datetime



if __name__ == "__main__":

    formatter = logging.Formatter('%(asctime)s program_name [%(process)d]: %(message)s', '%b %d %H:%M:%S')    
    log_handler = handlers.TimedRotatingFileHandler(r"logfiles\remote_request\logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    logging.info(msg=F"Start Script to send timed report @ {datetime.datetime.utcnow()} (UTC)")

    load_dotenv() 

    access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

    try:        
        ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
        response = requests.get(access_url)

        ## parse response as json object to extract configuration
        config_json = response.json()

        api_update_scheduler_string = config_json['update_scheduler_cronjob']
        
        ## initialize CronJob instance to handle update of cronjobs
        job_worker = CronJobManager()

        if job_worker.checkIfScheduleIsDifferent(api_update_scheduler_string):            
            logging.info(msg=F"Removing existing Cronjobs that schedule Cronjobs that handle 'service_worker.py' @ {datetime.datetime.utcnow()} (UTC)")
            job_worker.removeExistingJobs()

            logging.info(msg=F"Adding new Cronjob that schedule Cronjobs that handle 'service_worker.py' @ {datetime.datetime.utcnow()} (UTC)")
            job_worker.addNewJob(api_update_scheduler_string)
        
        else:
            logging.info(msg=F"No need to update Cronjob (no changes) @ {datetime.datetime.utcnow()} (UTC)")

    except HTTPError as http_err:
        logging.exception(msg=F"HTTP error occurred: {http_err} @{datetime.datetime.utcnow()}")

    except Exception as err:
        logging.exception(msg=F"Other error occurred: {err} @{datetime.datetime.utcnow()}")