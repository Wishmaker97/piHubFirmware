import subprocess
import sys
import os
import time
import datetime

import os
subprocess.check_call([sys.executable, '-m', 'pip', 'install','python-crontab'])

from crontab import CronTab

subprocess.check_call([sys.executable, '-m', 'pip', 'install','virtualenv'])

import virtualenv

if __name__ == "__main__":

    print("Initialization Script started ...")

    
    # STEP ZERO - setup directories

    print("[STEP 0] - SETUP Logfile directories")
    print("\t'-->[0.1] - SETUP logfiles")
    os.system("mkdir logfiles")

    print("\t'-->[0.2] - SETUP logfiles")
    os.system("mkdir logfiles/remote_request")

    print("\t'-->[0.3] - SETUP logfiles")
    os.system("mkdir logfiles/service_worker")

    print("\t'-->[0.4] - SETUP logfiles")
    os.system("mkdir logfiles/scheduler")


    # STEP ONE - VIRTUAL ENVIRONMENT !!

    print("[STEP 1] - SETUP VIRTUAL ENVIRONMENT FOR PYTHON")

    print("\t'-->[1.1] - Install Virtual Environment")
    os.system("sudo apt-get install python3-venv")

    print("\t'-->[1.2] - Create Virtual Environment")
    venv_dir = os.path.join(os.path.expanduser("~"), "venv")
    virtualenv.create_environment(venv_dir)

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
        data = [
            '#!/bin/bash\n',
            'source "/home/pihub/server/piHubFirmware/venv/bin/activate"\n',
            'cd /home/pihub/server/piHubFirmware/\n',
            'python remote_request.py'
        ]
        rsh.writelines(data)
    
    print("\t'-->[2.2] - create scheduler.sh script")
    with open ('/usr/local/sbin/scheduler.sh', 'w') as rsh:
        data = [
            '#!/bin/bash\n',
            'source "/home/pihub/server/piHubFirmware/venv/bin/activate"\n',
            'cd /home/pihub/server/piHubFirmware/\n',
            'python scheduler.py'
        ]
        rsh.writelines(data)

    print("\t'-->[2.3] - create service_worker.sh script")
    with open ('/usr/local/sbin/service_worker.sh', 'w') as rsh:
        data = [
            '#!/bin/bash\n',
            'source "/home/pihub/server/piHubFirmware/venv/bin/activate"\n',
            'cd /home/pihub/server/piHubFirmware/\n',
            'python service_worker.py'
        ]
        rsh.writelines(data)

    print("\t'-->[2.4] - check for all Shell scripts")
    list_files = subprocess.run(["ls", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    print("\t'-->[2.5] - create systemd service file remote_request.service") 
    with open ('/etc/systemd/system/remote_request.service', 'w') as rsh:   
        data = [
            '[Unit]\n',
            'Description=MQTT Remote access Server\n',
            '\n',
            '[Service]\n',
            'Restart=always\n',
            'ExecStartPre=/bin/sleep 10\n',
            'ExecStart=/usr/local/sbin/remote_request.sh\n',
            'PIDFile=/var/run/remote_request.pid\n',
            '\n',
            '[Install]\n',
            'WantedBy=multi-user.target'
        ]
        rsh.writelines(data)
    
    print("\t'-->[2.6] - check for all service scripts")
    list_files = subprocess.run(["ls", "/etc/systemd/system"])
    print("The exit code was: %d" % list_files.returncode)

    time.sleep(5)

    print("[STEP 3] - Shell Scripts")
    list_files = subprocess.run(["ls", "-la", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    # STEP THREE - ADDING PERMISSIONS !!
    print("\t'-->[3.1] - make scheduler.sh executable")
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','/usr/local/sbin/scheduler.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')

    print("\t'-->[3.2] - make remote_request.sh executable")
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','/usr/local/sbin/remote_request.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')

    print("\t'-->[3.3] - make service_worker.sh executable")
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','/usr/local/sbin/service_worker.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')


    print("\t'-->[3.4] - check if .sh files are executable")
    list_files = subprocess.run(["ls", "-la", "/usr/local/sbin"])
    print("The exit code was: %d" % list_files.returncode)

    print("\t'-->[3.5] - make .py executable")
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','remote_request.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','scheduler.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')
    subprocess.Popen(['sudo', '-S', 'chmod', '+rwx','service_worker.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')


    print("\t'-->[3.6] - start linux service for remote_request.py")
    subprocess.Popen(['sudo', '-S', 'systemctl', 'start','remote_request.service'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')


    print("\t'-->[3.7] - automate start on reboot linux service for remote_request.py")
    subprocess.Popen(['sudo', '-S', 'systemctl', 'enable','remote_request.service'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=f'{os.getenv("PASSWORD")}')
    

    cron=CronTab(user=True)
    cron.new(command=F"bash /usr/local/sbin/scheduler.sh", comment=F"CRON JOB ADDED @{datetime.datetime.utcnow()} (UTC)").setall("* * * * *")
    cron.write()
    



