from queue import Empty
from crontab import CronTab
from dotenv import load_dotenv
import datetime
import os


class CronJobManager:
    def __init__(self):
        self.cron = CronTab(user=True)
    
    def checkIfScheduleIsDifferent(self, new_schedule_string):
        if len(self.cron)==0:
            return True
        for job in self.cron:
            if "Scheduled report" in str(job) and new_schedule_string not in str(job):
                return True            
        return False
    
    def removeExistingJobs(self):
        for job in self.cron:
            if job != None and "Scheduled report" in str(job):
                self.cron.remove(job)
                self.cron.write()
    
    def addNewJob(self, new_schedule_string):
        load_dotenv()
        self.cron.new(command=F"bash /usr/local/sbin/service_worker.sh", comment=F"Scheduled report {datetime.datetime.now()}").setall(new_schedule_string)
        self.cron.write()
