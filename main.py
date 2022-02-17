from crontab import CronTab


tab = CronTab(tab="""* * * * * python ./outgoing_traffic.py""")
for result in tab.run_scheduler():
    print ("This was printed to stdout by the process.")