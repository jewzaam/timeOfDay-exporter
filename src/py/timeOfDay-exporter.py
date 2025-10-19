import argparse
from types import LambdaType
import time
import requests
import json
import yaml
import traceback
import datetime

import metrics_utility

DEBUG=True

def debug(message):
    if DEBUG:
        print("DEBUG: {}".format(message))

def do_timeOfDay(config):
    lat = config['location']['latitude']
    long = config['location']['longitude']

    # create labels common to all metrics
    global_labels={
        "latitude": lat,
        "longitude": long,
    }

    while True:
        # https://api.sunrise-sunset.org/json?lat=35.605350&lng=-78.793549&formatted=0
        response = requests.get("https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0".format(lat,long), verify=False)

        if response.status_code != 200 or response.text is None or response.text == '':
            metrics_utility.inc("timeOfDay_error_total")
        else:
            data = json.loads(response.text)

            try:
                begin_day=0
                begin_night=0
                if 'results' in data:
                    for key in data['results']:
                        value = str(data['results'][key])
                        if "+" not in value:
                            continue
                        # convert UTC string date to seconds since epoch
                        # example: 2021-08-13T01:42:21+00:00
                        utc_time = datetime.datetime.strptime(value.split("+")[0], "%Y-%m-%dT%H:%M:%S")
                        epoch_time = (utc_time - datetime.datetime(1970, 1, 1)).total_seconds()

                        metrics_utility.set("timeOfDay_{}".format(key), epoch_time, global_labels)

                        if key == 'astronomical_twilight_end':
                            begin_night = epoch_time
                        elif key == 'astronomical_twilight_begin':
                            begin_day = epoch_time

                # easier to fabricate is_day and is_night in python
                now=time.time()
                if begin_day<now:
                    begin_day += 24*60*60
                elif begin_day>now and begin_night>now:
                    begin_night -= 24*60*60
                metrics_utility.set("timeOfDay_begin_day",begin_day,global_labels)
                metrics_utility.set("timeOfDay_begin_night",begin_night,global_labels)

                metrics_utility.inc("timeOfDay_success_total", global_labels)
            except Exception as e:
                # well something went bad
                print(repr(e))
                traceback.print_exc()
                metrics_utility.inc("timeOfDay_error_total", global_labels)

        # sleep for the configured time
        time.sleep(config['refresh_delay_seconds'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export logs as prometheus metrics.")
    parser.add_argument("--port", type=int, help="port to expose metrics on")
    parser.add_argument("--config", type=str, help="configuraiton file")
    
    args = parser.parse_args()
    
    # Start up the server to expose the metrics.
    metrics_utility.metrics(args.port)

    config = {}
    with open(args.config, 'r') as f:
        config = yaml.load(f)
    
    do_timeOfDay(config)
