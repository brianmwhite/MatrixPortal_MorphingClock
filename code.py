# digit morphing code ported from https://www.instructables.com/Morphing-Digital-Clock/
# https://github.com/hwiguna/HariFun_166_Morphing_Clock

# some code started from
# https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Metro_Matrix_Clock/code.py
# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import gc  # Garbage collector for memory management

# If it still crashes (unlikely but possible):
# 1. Compile Digit.py into a .mpy (saves RAM during import).
# 2. Or, as a last resort, add import supervisor; supervisor.reload() at the very start of the file to force a clean heap on every auto-reload.

# Utility function to display memory usage at various stages
def print_memory_info(stage: str = ""):
    """Print current memory usage information with an optional stage label"""
    try:
        gc.collect()
        if stage:
            print(f"[{stage}] Memory free: {gc.mem_free()} bytes, allocated: {gc.mem_alloc()} bytes")
        else:
            print(f"Memory free: {gc.mem_free()} bytes, allocated: {gc.mem_alloc()} bytes")
    except Exception as e:
        print(f"Could not get memory info: {e}")

print_memory_info("Before importing Digit")
from Digit import Digit
print_memory_info("After importing Digit")

import adafruit_ds3231 # type: ignore
import adafruit_sht4x # type: ignore
import analogio # type: ignore
import board # type: ignore
import displayio # type: ignore
import rtc # type: ignore
import terminalio # type: ignore
from adafruit_bitmap_font import bitmap_font # type: ignore
from adafruit_datetime import datetime # type: ignore
from adafruit_display_text import label # type: ignore
from adafruit_matrixportal.matrix import Matrix # type: ignore


DEBUG = False
PHOTOCELL_THRESHOLD = 450
BRIGHTNESS_INTERVAL_SECONDS = 1
TEMPERATURE_INTERVAL_SECONDS = 60

displayio.release_displays()
ds3231 = adafruit_ds3231.DS3231(board.I2C())
rtc.set_time_source(ds3231)

temp_sensor = adafruit_sht4x.SHT4x(board.I2C())
photocell = analogio.AnalogIn(board.A0)

# --- Display setup ---
gc.collect()
print_memory_info("Before Matrix setup")
matrix = Matrix(bit_depth=4)
display = matrix.display

prevEpoch = 0
prevDate = None
prevhh = 0
prevmm = 0
prevss = 0

last_temp_check = None
last_brightness_check = None

DARKEST_COLOR = 255
BRIGHTEST_COLOR = 16711680

PHOTOCELL_MAX_VALUE = 5000
PHOTOCELL_MIN_VALUE = 0

# Hysteresis variables to prevent rapid switching
current_brightness_mode = "bright"  # Track current mode: "bright" or "dark"
BRIGHT_TO_DARK_THRESHOLD = 400     # Switch to dark when photocell < 400
DARK_TO_BRIGHT_THRESHOLD = 600     # Switch to bright when photocell > 600

# Simplified gradient palette - reduced from 100 to 10 values
GRADIENT_PALETTE = [
    1812, 1558, 1560, 1563, 1565, 1567, 1570, 1572, 1575, 1577, 1579, 1582, 1584, 
    1587, 1589, 1335, 1338, 1340, 1342, 1345, 1347, 1350, 1352, 1354, 1357, 1359, 
    1362, 1364, 1366, 1113, 1115, 1117, 1120, 1122, 1125, 1127, 1129, 1132, 1134, 
    1137, 1139, 1141, 1144, 890, 892, 895, 897, 900, 902, 904, 907, 909, 911, 914, 
    916, 919, 921, 667, 670, 672, 675, 677, 679, 682, 684, 686, 689, 691, 694, 696, 
    698, 445, 447, 450, 452, 454, 457, 459, 461, 464, 466, 469, 471, 473, 476, 222, 
    225, 227, 229, 232, 234, 236, 239, 241, 244, 246, 248, 251, 253, 255
]

def calculate_color_based_on_photocell_value(photocell_value: int):
    global current_brightness_mode
    
    # Apply hysteresis logic to prevent rapid switching
    if current_brightness_mode == "bright":
        # Currently in bright mode - only switch to dark if photocell value is clearly low
        if photocell_value < BRIGHT_TO_DARK_THRESHOLD:
            current_brightness_mode = "dark"
            color = GRADIENT_PALETTE[0]  # Dark color
        else:
            color = GRADIENT_PALETTE[-1]  # Stay bright
    else:  # current_brightness_mode == "dark"
        # Currently in dark mode - only switch to bright if photocell value is clearly high
        if photocell_value > DARK_TO_BRIGHT_THRESHOLD:
            current_brightness_mode = "bright"
            color = GRADIENT_PALETTE[-1]  # Bright color
        else:
            color = GRADIENT_PALETTE[0]  # Stay dark
    
    return color
    

group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 3)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(3)  # Create a color palette

# Make a background color fill
bg_sprite = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(bg_sprite)
display.show(group)
gc.collect()  # Clean up memory after display setup

def set_color_bright():
    global color
    color[0] = 0x000000  # black background
    color[1] = BRIGHTEST_COLOR
    color[2] = BRIGHTEST_COLOR


def set_color_dark():
    global color
    color[0] = 0x000000  # black background
    color[1] = DARKEST_COLOR
    color[2] = DARKEST_COLOR
    


set_color_bright()

##########################################################################

# Use built-in font to avoid memory issues with large BDF file
try:
    # Try to load the custom font if memory allows
    font = bitmap_font.load_font("/lemon.bdf")
    print("Loaded custom font successfully")
except MemoryError:
    print("Memory error loading custom font, using built-in font")
    font = terminalio.FONT
except Exception as e:
    print(f"Error loading custom font: {e}, using built-in font")
    font = terminalio.FONT

date_text_area = label.Label(font, text="", color=color[2])
date_text_area.x = 6
date_text_area.y = 19
group.append(date_text_area)

temp_text_area = label.Label(font, text="", color=color[2])
temp_text_area.x = 11
temp_text_area.y = 28
group.append(temp_text_area)

digit0 = Digit(d=group, b=bitmap, value=0, xo=63 - 1 - 9 * 1, yo=32 - 15 - 1, color=1)
digit1 = Digit(d=group, b=bitmap, value=0, xo=63 - 1 - 9 * 2, yo=32 - 15 - 1, color=1)
digit2 = Digit(d=group, b=bitmap, value=0, xo=63 - 4 - 9 * 3, yo=32 - 15 - 1, color=1)
digit3 = Digit(d=group, b=bitmap, value=0, xo=63 - 4 - 9 * 4, yo=32 - 15 - 1, color=1)
digit4 = Digit(d=group, b=bitmap, value=0, xo=63 - 7 - 9 * 5, yo=32 - 15 - 1, color=1)
digit5 = Digit(d=group, b=bitmap, value=0, xo=63 - 7 - 9 * 6, yo=32 - 15 - 1, color=1)

digit1.DrawColon(1)
digit3.DrawColon(1)

# Draw the initial time once so digits appear immediately (definition is below)

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
        # if hh > 12:
        #     hh = hh - 12
        mm = timeObject.tm_min
        ss = timeObject.tm_sec

        if prevEpoch == 0:  # If we didn't have a previous time. Just draw it.
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

            if (
                currentDate.month != prevDate.month
                or currentDate.day != prevDate.day
                or currentDate.year != prevDate.year
            ):
                print(
                    "changing date to "
                    + format_datetime(prevDate)
                    + " from "
                    + format_datetime(currentDate)
                )
                date_text_area.text = currentDate.ctime()[:10]

        prevEpoch = epoch
        prevDate = currentDate


def format_datetime(datetime_object: datetime):
    return datetime_object.isoformat()[:10]


def convert_to_fahrenheit(celsius: float):
    return (celsius * 1.8) + 32


# Perform an initial draw now that update_time exists
update_time()


# Main loop with prioritized operations
while True:
    # PRIORITY 1: Always update time first - this should never be blocked
    update_time()
    
    # PRIORITY 2: Update brightness (every 1 second)
    if (last_brightness_check is None or 
        time.monotonic() > last_brightness_check + BRIGHTNESS_INTERVAL_SECONDS):
        
        color[0] = 0x000000  # black background
        color[1] = calculate_color_based_on_photocell_value(photocell.value)
        color[2] = color[1]
        
        temp_text_area.color = color[2]
        date_text_area.color = color[2]
        
        last_brightness_check = time.monotonic()

    # PRIORITY 3: Read temperature sensor and update display (every 60 seconds)
    if (last_temp_check is None or 
        time.monotonic() > last_temp_check + TEMPERATURE_INTERVAL_SECONDS):
        
        try:
            temp_fahrenheit = convert_to_fahrenheit(temp_sensor.temperature)
            humidity = temp_sensor.relative_humidity
            
            temp_text_area.text = "%d°  %d%%" % (
                round(temp_fahrenheit),
                round(humidity),
            )
            
            nowtime = time.localtime()
            printedtime = "%02d:%02d:%02d" % (
                nowtime.tm_hour,
                nowtime.tm_min,
                nowtime.tm_sec,
            )
            
            print(
                "time=%s | temp= %d | humidity=%d | photocell=%d"
                % (printedtime, temp_fahrenheit, humidity, photocell.value),
            )
            
            last_temp_check = time.monotonic()
            
        except Exception as error:
            print(f"Temperature sensor read failed: {error}")
    
    # Short sleep to prevent excessive CPU usage while maintaining responsiveness
    time.sleep(0.01)
