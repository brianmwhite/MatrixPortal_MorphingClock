# digit morphing code ported from https://www.instructables.com/Morphing-Digital-Clock/
# https://github.com/hwiguna/HariFun_166_Morphing_Clock

# some code started from https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Metro_Matrix_Clock/code.py
# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import adafruit_ds3231
import board
import displayio
import rtc
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_datetime import datetime
from adafruit_display_text import label
from adafruit_matrixportal.graphics import Graphics
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network

from Digit import Digit

DEBUG = False


displayio.release_displays()
ds3231 = adafruit_ds3231.DS3231(board.I2C())
rtc.set_time_source(ds3231)

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

prevEpoch = 0
prevDate = None
prevhh = 0
prevmm = 0
prevss = 0

group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(3)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0x0000FF  # blue
color[2] = 0x3F1651  # dark blue/purple

# Make a background color fill
bg_sprite = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(bg_sprite)
display.show(group)

##########################################################################

if not DEBUG:
    date_font = bitmap_font.load_font("/lemon.bdf")
else:
    date_font = terminalio.FONT

date_text_area = label.Label(date_font, text="", color=color[2])
date_text_area.x = 6
date_text_area.y = 21

group.append(date_text_area)


digit0 = Digit(d=group, b=bitmap, value=0, xo=63 - 1 - 9 * 1, yo=32 - 15 - 3, color=1)
digit1 = Digit(d=group, b=bitmap, value=0, xo=63 - 1 - 9 * 2, yo=32 - 15 - 3, color=1)
digit2 = Digit(d=group, b=bitmap, value=0, xo=63 - 4 - 9 * 3, yo=32 - 15 - 3, color=1)
digit3 = Digit(d=group, b=bitmap, value=0, xo=63 - 4 - 9 * 4, yo=32 - 15 - 3, color=1)
digit4 = Digit(d=group, b=bitmap, value=0, xo=63 - 7 - 9 * 5, yo=32 - 15 - 3, color=1)
digit5 = Digit(d=group, b=bitmap, value=0, xo=63 - 7 - 9 * 6, yo=32 - 15 - 3, color=1)

digit1.DrawColon(color[1])
digit3.DrawColon(color[1])


def update_time():
    timeObject = time.localtime()
    epoch = time.mktime(timeObject)
    currentDate = datetime.fromtimestamp(epoch)

    global prevDate
    global prevEpoch
    global prevhh
    global prevmm
    global prevss

    if epoch != prevEpoch:
        hh = timeObject.tm_hour
        if hh > 12:
            hh = hh - 12
        mm = timeObject.tm_min
        ss = timeObject.tm_sec
        if (
            prevEpoch == 0
        ):  # // If we didn't have a previous time. Just draw it without morphing.
            digit0.Draw(int(ss % 10))
            digit1.Draw(int(ss / 10))
            digit2.Draw(int(mm % 10))
            digit3.Draw(int(mm / 10))
            digit4.Draw(int(hh % 10))
            digit5.Draw(int(hh / 10))

            date_text_area.text = currentDate.ctime()[:10]
        else:
            if ss != prevss:
                s0 = int(ss % 10)
                s1 = int(ss / 10)
                if s0 != digit0.Value():
                    digit0.Morph(s0)
                if s1 != digit1.Value():
                    digit1.Morph(s1)
                prevss = ss

            if mm != prevmm:
                m0 = int(mm % 10)
                m1 = int(mm / 10)
                if m0 != digit2.Value():
                    digit2.Morph(m0)
                if m1 != digit3.Value():
                    digit3.Morph(m1)
                prevmm = mm

            if hh != prevhh:
                h0 = int(hh % 10)
                h1 = int(hh / 10)
                if h0 != digit4.Value():
                    digit4.Morph(h0)
                if h1 != digit5.Value():
                    digit5.Morph(h1)
                prevhh = hh

            if currentDate != prevDate:
                print("changing date to")
                print(currentDate)
                date_text_area.text = currentDate.ctime()[:10]

        prevEpoch = epoch
        prevDate = currentDate


last_check = None

while True:
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            timeObject = time.localtime()
            if timeObject.tm_hour == 2 and timeObject.tm_min > 0:
                pass
                # network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time()
    time.sleep(0.01)
