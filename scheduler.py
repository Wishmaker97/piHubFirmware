from queue import Empty
from crontab import CronTab
from dotenv import load_dotenv
import os
import requests
from requests.exceptions import HTTPError
from uuid import getnode as get_mac
from CronJobManager import CronJobManager


if __name__ == "__main__":
    load_dotenv() 

    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
    access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

    print(access_url)

    try:        
        response = requests.get(access_url)
        config_json = response.json()

        api_update_scheduler_string = config_json['update_scheduler_cronjob']
        
        job_worker = CronJobManager()

        if job_worker.checkIfScheduleIsDifferent(api_update_scheduler_string):            
            print("removing existing jobs")
            job_worker.removeExistingJobs()

            print("adding new job")
            job_worker.addNewJob(api_update_scheduler_string)
        
        else:
            print("dont need to update schedule reporter")

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
