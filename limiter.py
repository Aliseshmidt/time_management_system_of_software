import time
import os
import threading
import schedule
from datetime import datetime


hosts = r'C:\Windows\System32\drivers\etc\hosts'
# hosts = '/etc/hosts'
redirect_url = '127.0.0.1'

blocked_sites = ['www.youtube.com', 'youtube.com', 'www.vk.com', 'vk.com', 'www.okko.tv', 'okko.tv'] 

def detectTime(start_time_hour, start_time_minute, finish_time_hour, finish_time_minute):
    sth, stm, fth, ftm = start_time_hour, start_time_minute, finish_time_hour, finish_time_minute
    num_repeats = ((finish_time_hour*60*60 + finish_time_minute*60) - (start_time_hour*60*60 + start_time_minute*60))
    print(num_repeats)
    for i in range(int(num_repeats)):
        print(i)
        killlife(sth, stm, fth, ftm)
        # time.sleep(60)
        if i == int(num_repeats):
            stop()
        


def killlife():
    start_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0)
    finish_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23)
    # while True:
    if start_time < datetime.now() < finish_time:
        print('Доступ ограничен!')
        
        with open(hosts, 'r+') as file:
            src = file.read()
            
            for site in blocked_sites:
                if site in src:
                    pass
                else:
                    file.write(f'{redirect_url} {site}\n')
    else:
        with open(hosts, 'r+') as file:
            src = file.readlines()
            file.seek(0)
            
            for line in src:
                if not any(site in line for site in blocked_sites):
                    file.write(line)
            file.truncate()
        print('Доступ открыт!')
            # break

        # time.sleep(5)

# # Define the total runtime in minutes
# total_runtime = 60

# # Define the number of repeats based on the interval of 5 minutes and the total runtime
# num_repeats = int(total_runtime / 5)

# # Schedule the close_game() function to run every 5 minutes
# schedule.every(5).minutes.do()

# # Run the scheduled task for the specified number of repeats
# for _ in range(num_repeats):
#     schedule.run_pending()
#     time.sleep(60)  # Wait for 1 minute before the next iteration

# def start(start_time_hour, start_time_minute, finish_time_hour, finish_time_minute):
#     timer.start(start_time_hour, start_time_minute, finish_time_hour, finish_time_minute)
#     print('start')
        
def stop():
    # timer.cancel()
    with open(hosts, 'r+') as file:
        content=file.readlines()
        file.seek(0)
        for line in content:
            if not any(website in line for website in blocked_sites):
                file.write(line)

        file.truncate()

# timer = threading.Timer(5.0, killlife)







