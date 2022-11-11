# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect
from Digit import Digit

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish

display.show(group)

# Make a background color fill
bg_sprite = displayio.TileGrid(bitmap, x=0, y=0, pixel_shader=color)
group.append(bg_sprite)
##########################################################################

digit = Digit(d=group, value=0, xo=0, yo=0, color=color[1])

digit.drawPixel(11, 11, color[1])
digit.drawLine(0, 0, 10, 10, color[3])
digit.drawLine(12, 12, 22, 22, color[3])
digit.drawFillRect(13, 17, 5, 5, color[1])

# Loop forever so you can enjoy your image
while True:
    pass
