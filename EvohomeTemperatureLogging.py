# Load required libraries
import requests
import json
import datetime
from datetime import datetime
import time
import configparser
from evohomeclient2 import EvohomeClient
import csv

def log(USERNAME, PASSWORD, period=900):
    #initialisation
    initialisation = 1
    try:
        client = EvohomeClient(USERNAME, PASSWORD)
    except ValueError:
        try:
            client = EvohomeClient(USERNAME, PASSWORD, debug=True)
        except ValueError:
            print("Error when connecting to internet, please try again")

    # Infinite loop every X minutes, send temperatures to csv
    while True:
    # Get current time and save values to csv
        try:
            client = EvohomeClient(USERNAME, PASSWORD)
            room_data = list(client.temperatures())
        except:
            try:
                client.login()
                client = EvohomeClient(USERNAME, PASSWORD, debug=True)
                room_data = list(client.temperatures())
            except ValueError:
                print("Error when connecting to internet, please try again")
        # measurements = list()
        for room in room_data:
            if initialisation == 1:
                labels = list(room.keys())
                labels.append('time')
                d = datetime.now().strftime('%Y%m%d  %H%M%S ')
                filename = d + 'temperature.csv'
                with open(filename, 'w') as f:
                    writer = csv.DictWriter(f, fieldnames=labels)
                    writer.writeheader()
                initialisation = 0
            # print(device)
            t = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            room['time'] = t
        try:
            with open(filename, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=labels)
                for room in room_data:
                    writer.writerow(room)
        except IOError:
            print("I/O error")

        print("Going to sleep for"+str(period))
        time.sleep(period)

    return None

def main():
    #config
    Config = configparser.ConfigParser()
    Config.read("config.ini")

    # stream_ids_array = []
    # for name, value in Config.items('Rooms'):
    #     stream_ids_array.append(value)

    # Set your login details in the 2 fields below
    USERNAME = Config.get('Evohome', 'Username')
    PASSWORD = Config.get('Evohome', 'Password')

    try:
        log(USERNAME, PASSWORD)
    except:
        print("Lets wait and restart..")
        time.sleep(300)
        log(USERNAME, PASSWORD)
    return None

if __name__ == "__main__":
    main()