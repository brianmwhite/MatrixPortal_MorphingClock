import time

import adafruit_ds3231
import board
from adafruit_matrixportal.network import Network


network = Network(status_neopixel=board.NEOPIXEL, debug=False)  # type: ignore
ds3231 = adafruit_ds3231.DS3231(board.I2C())

TIME_SERVICE_FORMAT = "%Y-%m-%d %H:%M:%S.%L %j %u %z %Z"
LOCATION = "America/New_York"

network.connect()

def looptime():
    while True:
        printtime()
        time.sleep(1)


def printtime():
    now = ds3231.datetime
    print(
        "{:4}/{:02}/{:02}  {:02}:{:02}:{:02}".format(
            now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec,
        )
    )


def synctime(print_time=True):
    # call a local api to get the latest time as a json object, parse it into a struct_time and set the RTC
    JSON_URL = "http://192.168.7.97:5015/time"
    response = network._wifi.requests.get(JSON_URL, timeout=10)
    json = response.json()
    time_as_struct = time.struct_time((json["year"]
                                        , json["month"]
                                        , json["day"]
                                        , json["hour"]
                                        , json["minute"]
                                        , json["second"] + 1
                                        , 0, -1, -1))
    ds3231.datetime = time_as_struct
    if print_time:
        looptime()


def synctimeaio(print_time=True):
    # NOTE: time is set but with a couple second delay
    # modified from adafruit_portalbase.network
    # SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
    # SPDX-FileCopyrightText: Copyright (c)
    #   2020 Melissa LeBlanc-Williams for Adafruit Industries
    # SPDX-License-Identifier: MIT

    time_reply = network.get_strftime(TIME_SERVICE_FORMAT, LOCATION)
    print(time_reply)
    if time_reply:
        times = time_reply.split(" ")
        the_date = times[0]
        the_time = times[1]
        # year_day = int(times[2])
        # week_day = int(times[3])
        # is_dst = None  # no way to know yet
        year, month, mday = [int(x) for x in the_date.split("-")]
        the_time = the_time.split(".")[0]
        hours, minutes, seconds = [int(x) for x in the_time.split(":")]
        # now = time.struct_time(
        #     (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
        # )
        # print(now)
        ds3231.datetime = time.struct_time(
            (year, month, mday, hours, minutes, seconds, 0, -1, -1)
        )
        if print_time:
            looptime()


def settime(hour: int, min: int, sec: int):
    time_struct = ds3231.datetime
    setdatetime(
        time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday, hour, min, sec
    )


def setdatetime(year: int, month: int, day: int, hour: int, min: int, sec: int):
    print(
        "Ready to set RTC to: {:4}/{:02}/{:02}  {:02}:{:02}:{:02}".format(
            year, month, day, hour, min, sec
        )
    )
    _ = input("Press ENTER to set.")

    ds3231.datetime = time.struct_time((year, month, day, hour, min, sec, 0, -1, -1))

    looptime()


if __name__ == "__main__":
    printtime()
