import time

import adafruit_ds3231
import board
from adafruit_matrixportal.network import Network

network = Network(status_neopixel=board.NEOPIXEL, debug=False)  # type: ignore
ds3231 = adafruit_ds3231.DS3231(board.I2C())


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


printtime()
