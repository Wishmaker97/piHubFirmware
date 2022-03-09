import subprocess
import sys
import os
import time

subprocess.check_call([sys.executable, '-m', 'pip', 'install','python-crontab'])

import datetime
from crontab import CronTab

if __name__ == "__main__":

    print("Initialization Script started ...")

    
    # STEP ZERO - setup directories

    print("[STEP 0] - SETUP Logfile directories")
    print("\t'-->[0.1] - SETUP logfiles")
    os.system("mkdir logfiles")

    print("\t'-->[0.2] - SETUP logfiles")
    os.system("mkdir logfiles/remote_requests")

    print("\t'-->[0.3] - SETUP logfiles")
    os.system("mkdir logfiles/service_worker")

    print("\t'-->[0.4] - SETUP logfiles")
    os.system("mkdir logfiles/scheduler")


    # STEP ONE - VIRTUAL ENVIRONMENT !!

    print("[STEP 1] - SETUP VIRTUAL ENVIRONMENT FOR PYTHON")

    print("\t'-->[1.1] - Install Virtual Environment")
    os.system("sudo apt-get install python3-venv")

    print("\t'-->[1.2] - Create Virtual Environment")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])

    print("\t'-->[1.3] - ACTIVATE Virtual Environment")
    os.system("source /venv/bin/activate")

    list_files = subprocess.run(["ls", "-la"])
    print("The exit code was: %d" % list_files.returncode)

    print("\t'-->[1.4] - install requirements.txt file")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\t'-->[1.5] - show current directory")
    os.system("pwd")

    time.sleep(5)

    # STEP TWO - Make Shell and service scripts Scripts !!

    print("[STEP 2] - Shell Scripts")

    print("\t'-->[2.1] - create remote_request.sh script")
    with open ('/usr/local/sbin/remote_request.sh', 'w') as rsh:
        rsh.write('''\
        #!/bin/bash
        userName=$SUDO_USER
        source "/home/$userName/server/pi-hub/venv/bin/activate"
        cd /home/$userName/server/pi-hub/
        python remote_request.py
        ''')
    
    print("\t'-->[2.2] - create scheduler.sh script")
    with open ('/usr/local/sbin/scheduler.sh', 'w') as rsh:
        rsh.write('''\
        #!/bin/bash
        userName=$SUDO_USER
        source "/home/$userName/server/pi-hub/venv/bin/activate"
        cd /home/$userName/server/pi-hub/
        python scheduler.py
        ''')

    print("\t'-->[2.3] - create service_worker.sh script")
    with open ('/usr/local/sbin/service_worker.sh', 'w') as rsh:
        rsh.write('''\
        #!/bin/bash
        userName=$SUDO_USER
        source "/home/$userName/server/pi-hub/venv/bin/activate"
        cd /home/$userName/server/pi-hub/
        python service_worker.py
        ''')

    print("\t'-->[2.4] - check for all Shell scripts")
    list_files = subprocess.run(["ls", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    print("\t'-->[2.5] - create systemd service file remote_request.service")    
    with open ('/etc/systemd/system/remote_request.service', 'w') as rsh:
        rsh.write('''\
        [Unit]
        Description=MQTT Remote access Server

        [Service]
        Restart=always
        ExecStartPre=/bin/sleep 10
        ExecStart=/usr/local/sbin/remote_request.sh
        PIDFile=/var/run/remote_request.pid

        [Install]
        WantedBy=multi-user.target    
        ''')
    
    print("\t'-->[2.6] - check for all service scripts")
    list_files = subprocess.run(["ls", "/etc/systemd/system"])
    print("The exit code was: %d" % list_files.returncode)

    time.sleep(5)

    print("[STEP 2] - Shell Scripts")
    list_files = subprocess.run(["ls", "-la", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    # STEP THREE - ADDING PERMISSIONS !!
    print("\t'-->[3.1] - make scheduler.sh executable")
    os.system("chmod u+x /usr/local/sbin/scheduler.sh")

    print("\t'-->[3.2] - make remote_request.sh executable")
    os.system("chmod u+x /usr/local/sbin/remote_request.sh")

    print("\t'-->[3.3] - make service_worker.sh executable")
    os.system("chmod u+x /usr/local/sbin/service_worker.sh")

    print("\t'-->[3.4] - check if .sh files are executable")
    list_files = subprocess.run(["ls", "-la", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    print("\t'-->[3.5] - make .py executable")
    os.system("chmod u+x remote_request.py")

    print("\t'-->[3.6] - start linux service for remote_request.py")
    os.system("systemctl start remote_request.service")

    print("\t'-->[3.7] - automate start on reboot linux service for remote_request.py")
    os.system("systemctl enable remote_request.service")
    

    # cron=CronTab(user=True)
    # cron.new(command=F"bash /usr/local/sbin/scheduler.sh", comment=F"CRON JOB ADDED @{datetime.datetime.utcnow()} (UTC)").setall("* * * * *")
    # cron.write()
    



