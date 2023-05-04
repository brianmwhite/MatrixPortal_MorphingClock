import time

import adafruit_ds3231
import board
from adafruit_matrixportal.network import Network


class Timesetter:

    LOCAL_API_TIME_JSON_URL = "http://192.168.7.97:5015/time"
    TIME_SERVICE_FORMAT = "%Y-%m-%d %H:%M:%S.%L %j %u %z %Z"
    LOCATION = "America/New_York"

    def __init__(self, ds3231=None, print_time=False):
        if ds3231 is None:
            self.ds3231 = adafruit_ds3231.DS3231(board.I2C())
        else:
            self.ds3231 = ds3231

        self.print_time = print_time


    def looptime(self):
        while True:
            self.printtime()
            time.sleep(1)


    def printtime(self):
        now = self.ds3231.datetime
        print(
            "{:4}/{:02}/{:02}  {:02}:{:02}:{:02}".format(
                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec,
            )
        )


    def synctime(self, network=None):
        if network is None:
            self.network = Network(status_neopixel=board.NEOPIXEL, debug=False)  # type: ignore
        else:
            self.network = network
        
        if not self.network.is_connected:
            self.network.connect()

        response = self.network._wifi.requests.get(self.LOCAL_API_TIME_JSON_URL, timeout=10)
        json = response.json()
        time_as_struct = time.struct_time((json["year"]
                                            , json["month"]
                                            , json["day"]
                                            , json["hour"]
                                            , json["minute"]
                                            , json["second"] + 1
                                            , 0, -1, -1))
        self.ds3231.datetime = time_as_struct
        
        if self.print_time:
            self.looptime()


    def synctimeaio(self):
        # NOTE: time is set but with a couple second delay
        # modified from adafruit_portalbase.network
        # SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
        # SPDX-FileCopyrightText: Copyright (c)
        #   2020 Melissa LeBlanc-Williams for Adafruit Industries
        # SPDX-License-Identifier: MIT

        time_reply = self.network.get_strftime(self.TIME_SERVICE_FORMAT, self.LOCATION)
        print(time_reply)
        if time_reply:
            times = time_reply.split(" ")
            the_date = times[0]
            the_time = times[1]
            year, month, mday = [int(x) for x in the_date.split("-")]
            the_time = the_time.split(".")[0]
            hours, minutes, seconds = [int(x) for x in the_time.split(":")]
            self.ds3231.datetime = time.struct_time(
                (year, month, mday, hours, minutes, seconds, 0, -1, -1)
            )
            if self.print_time:
                self.looptime()


    def settime(self, hour: int, min: int, sec: int):
        time_struct = self.ds3231.datetime
        self.setdatetime(
            time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday, hour, min, sec
        )


    def setdatetime(self, year: int, month: int, day: int, hour: int, min: int, sec: int):
        print(
            "Ready to set RTC to: {:4}/{:02}/{:02}  {:02}:{:02}:{:02}".format(
                year, month, day, hour, min, sec
            )
        )
        _ = input("Press ENTER to set.")

        self.ds3231.datetime = time.struct_time((year, month, day, hour, min, sec, 0, -1, -1))

        if self.print_time:
            self.looptime()
