import os
import json
import datetime
import os.path
import time
import shlex

interV = 15  # Script repeat interval in seconds
print(f"Welcome to SMS Forwarder")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# Defining function for forwarding sms


def smsforward(looping=False):
    global looper  # refferencing main looper varibale

    lastSMS = datetime.datetime.now()
    tmpFile = "tmpLastTime.txt"
    cfgFile = "config.txt"

    # Checking existance of configuration file
    if not os.path.exists(cfgFile):
        # file not found. creating a new configuration file
        cfile = open(cfgFile, "a")
        mnumbers = input(f"{bcolors.BOLD}Please enter mobile number(s) separated by comma (',') : {bcolors.ENDC}")
        mnumber_s = mnumbers.split(",")
        cfile.write(mnumbers)
        cfile.close()
    else:
            # configuration file is already there. reading configurations
        rst = "1"
        if not looping:
            print(f"""{bcolors.BOLD}Old configuration file found! What do You want to do?{bcolors.ENDC}
                {bcolors.OKGREEN}1) Continue with old settings{bcolors.ENDC}
                {bcolors.WARNING}2) Remove old settings and start afresh{bcolors.ENDC}""")
            # rst = input("Please enter your choice number: ")
            rst = "1"
        if rst == "1":
            print(f"{bcolors.OKGREEN}Starting with old settings...........{bcolors.ENDC}")
            cfile = open(cfgFile, "r")
            cdata = cfile.read().splitlines()
            mnumber_s = cdata[0].split(",")
        elif rst == "2":
            print(f"{bcolors.WARNING}Removing old Configuration files..........{bcolors.ENDC}")
            os.remove(cfgFile)
            os.remove(tmpFile)
            print(f"{bcolors.WARNING}Old configuration files removed. Please enter new settings{bcolors.ENDC}")
            smsforward()

    # Chcking last saved forward time
    if not os.path.exists(tmpFile):
        # Saved time time not found. Setting up and saving current time as last forwar dime
        print("Last time not found. Setting it to current Date-Time")
        tfile = open(tmpFile, "w")
        tfile.write(str(lastSMS))
        tfile.close()
    else:
        # Saved last sms forward time found. loading form that
        tfile = open(tmpFile, "r")
        lastSMS = datetime.datetime.fromisoformat(tfile.read())
        tfile.close()

    print(f"Last SMS forwarded on {lastSMS}")
    jdata = os.popen("termux-sms-list -l 50").read()  # Reading latest 50 SMSs using termux-api
    jd = json.loads(jdata)  # storing JSON output
    print(f"Reading {len(jd)} latest SMSs")

    for j in jd:
        if datetime.datetime.fromisoformat(j['received']) > lastSMS:  # Comparing SMS timing
            if j['type'] == "inbox":  # Checking if the SMS is in inbox
                    for m in mnumber_s:
                        print(f"Forwarding SMS to: {m}")
                        sms_body = shlex.quote(j['body'])   # Properly escape special characters in the SMS body
                        resp = os.popen(f"termux-sms-send -n {m} {sms_body}")  # forwarding sms to predefined mobile number(s)
                        tfile = open(tmpFile, "w")
                        tfile.write(j['received'])
                        tfile.close()


# calling sms forward function for the first time
smsforward()
# The following loop will repeat the script exexcution
while True:
    time.sleep(interV)
    smsforward(looping=True)
