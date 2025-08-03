# digit morphing code ported from https://www.instructables.com/Morphing-Digital-Clock/
# https://github.com/hwiguna/HariFun_166_Morphing_Clock

# some code started from
# https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Metro_Matrix_Clock/code.py
# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import adafruit_ds3231 # type: ignore
import adafruit_esp32spi.adafruit_esp32spi_socket as socket # type: ignore
import adafruit_minimqtt.adafruit_minimqtt as MQTT # type: ignore
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
from adafruit_matrixportal.network import Network # type: ignore

from Digit import Digit

DEBUG = False
PHOTOCELL_THRESHOLD = 450
BRIGHTNESS_INTERVAL_SECONDS = 1
TEMPERATURE_INTERVAL_SECONDS = 60
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


displayio.release_displays()
ds3231 = adafruit_ds3231.DS3231(board.I2C())
rtc.set_time_source(ds3231)

temp_sensor = adafruit_sht4x.SHT4x(board.I2C())
photocell = analogio.AnalogIn(board.A0)

# --- Display setup ---
matrix = Matrix(bit_depth=4)
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# Network connection state
network_connected = False
last_connection_attempt = None
CONNECTION_RETRY_INTERVAL_SECONDS = 30

# Try initial connection, but don't crash if it fails
try:
    network.connect()
    network_connected = True
    print("Network connected successfully")
except Exception as error:
    print(f"Initial network connection failed: {error}")
    network_connected = False

prevEpoch = 0
prevDate = None
prevhh = 0
prevmm = 0
prevss = 0

last_temp_check = None
last_brightness_check = None

# DARKEST_COLOR = 255
# BRIGHTEST_COLOR = 16711680
DARKEST_COLOR = 255
BRIGHTEST_COLOR = 16711680


PHOTOCELL_MAX_VALUE = 5000
PHOTOCELL_MIN_VALUE = 0

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
    # given the photocell range from PHOTOCELL_MIN_VALUE to PHOTOCELL_MAX_VALUE
    # calculate the color based on the gradient palette
    # position 0 in the gradient should correspond to the photocell max value
    # the last value in the gradient should correspond to the photocell min value
    # the gradient palette is stored in the variable GRADIENT_PALETTE and is
    # currently 100 values long but could be longer or shorter
    # there will always be at least 2 values in the gradient palette

# round the photocell value to the nearest ten so the values will all be whole numbers that are evenly divisible by 10
    # photocell_value = round(photocell_value, -1)

    # percent = photocell_value / (PHOTOCELL_MAX_VALUE - PHOTOCELL_MIN_VALUE)
    # position = round(percent * len(GRADIENT_PALETTE))
    
    # if position > len(GRADIENT_PALETTE):
    #     position = len(GRADIENT_PALETTE) - 1
    # elif position < 0:
    #     position = 0
    # else:
    #     position = position - 1
    color = GRADIENT_PALETTE[-1]

    if photocell_value < 500:
        color = GRADIENT_PALETTE[0]
    
    return color
    

group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 3)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(3)  # Create a color palette
# color[0] = 0x000000  # black background
# color[1] = 0x0000FF  # blue
# color[2] = 0x3F1651  # dark blue/purple

# Make a background color fill
bg_sprite = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(bg_sprite)
display.show(group)

mqtt = MQTT.MQTT(
    broker=secrets["mqtt_broker"],
    username=secrets["mqtt_username"],
    password=secrets["mqtt_password"],
    port=secrets["mqtt_port"],
    client_id="office_morphing_clock",
)

# Only set socket if network is connected
if network_connected:
    try:
        MQTT.set_socket(socket, network._wifi.esp)
    except Exception as error:
        print(f"Failed to set MQTT socket: {error}")
        network_connected = False


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

if not DEBUG:
    font = bitmap_font.load_font("/lemon.bdf")
else:
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
    fahrenheit = (celsius * 1.8) + 32
    return fahrenheit


def subscribe():
    global network_connected
    if not network_connected:
        print("Network not connected, skipping MQTT subscribe")
        return False
    
    try:
        if not mqtt.is_connected():
            print("Initial MQTT connection attempt...")
            try:
                mqtt.connect()
                print("Initial MQTT connection successful")
            except Exception as connect_error:
                print(f"Initial MQTT connection failed: {connect_error}")
                print(f"Connection error type: {type(connect_error).__name__}")
                raise connect_error
            
            try:
                mqtt.subscribe(secrets["mqtt_topic"])
                print(f"Initial MQTT subscription to {secrets['mqtt_topic']} successful")
            except Exception as subscribe_error:
                print(f"Initial MQTT subscription failed: {subscribe_error}")
                print(f"Subscription error type: {type(subscribe_error).__name__}")
                raise subscribe_error
        return True
    except MQTT.MMQTTException as mqtt_error:
        print(f"Initial MQTT specific error: {mqtt_error}")
        print(f"MQTT error type: {type(mqtt_error).__name__}")
        network_connected = False
        return False
    except RuntimeError as runtime_error:
        print(f"Initial Runtime error: {runtime_error}")
        print(f"Runtime error type: {type(runtime_error).__name__}")
        network_connected = False
        return False
    except ConnectionError as conn_error:
        print(f"Initial Connection error: {conn_error}")
        print(f"Connection error type: {type(conn_error).__name__}")
        network_connected = False
        return False
    except Exception as general_error:
        print(f"Initial unexpected error: {general_error}")
        print(f"Error type: {type(general_error).__name__}")
        network_connected = False
        return False


def try_reconnect():
    global network_connected, last_connection_attempt
    
    current_time = time.monotonic()
    if (last_connection_attempt is not None and 
        current_time < last_connection_attempt + CONNECTION_RETRY_INTERVAL_SECONDS):
        return False
    
    last_connection_attempt = current_time
    print("Attempting to reconnect to network...")
    
    try:
        print("Reconnecting to WiFi network...")
        network.connect()
        print("WiFi reconnection successful")
        
        print("Setting up MQTT socket...")
        MQTT.set_socket(socket, network._wifi.esp)
        print("MQTT socket setup successful")
        
        if subscribe():
            network_connected = True
            print("Full reconnection successful!")
            return True
        else:
            print("MQTT subscription failed during reconnection")
            return False
    except Exception as error:
        print(f"Reconnection failed: {error}")
        print(f"Reconnection error type: {type(error).__name__}")
    
    network_connected = False
    return False


# Try initial MQTT connection, but don't crash if it fails
if network_connected:
    subscribe()

while True:
    # Try to reconnect if network is down
    if not network_connected:
        try_reconnect()
    
    if (
        last_brightness_check is None
        or time.monotonic() > last_brightness_check + BRIGHTNESS_INTERVAL_SECONDS
    ):
        
        color[0] = 0x000000  # black background
        color[1] = calculate_color_based_on_photocell_value(photocell.value)
        # color[1] = GRADIENT_PALETTE[-1]
        color[2] = color[1]
        # print("color value=%d" % color[1])

        last_brightness_check = time.monotonic()


    temp_text_area.color = color[2]
    date_text_area.color = color[2]

    if (
        last_temp_check is None
        or time.monotonic() > last_temp_check + TEMPERATURE_INTERVAL_SECONDS
    ):
        currentTempInCelsius = temp_sensor.temperature
        currentHumidity = temp_sensor.relative_humidity
        currentTempInFahrenheit = convert_to_fahrenheit(currentTempInCelsius)

        # Only try MQTT if network is connected
        if network_connected:
            try:
                if not mqtt.is_connected():
                    print("MQTT not connected, attempting to connect...")
                    try:
                        mqtt.connect()
                        print("MQTT connected successfully")
                    except Exception as connect_error:
                        print(f"MQTT connection failed: {connect_error}")
                        print(f"Connection error type: {type(connect_error).__name__}")
                        raise connect_error
                    
                    try:
                        mqtt.subscribe(secrets["mqtt_topic"])
                        print(f"MQTT subscribed to topic: {secrets['mqtt_topic']}")
                    except Exception as subscribe_error:
                        print(f"MQTT subscription failed: {subscribe_error}")
                        print(f"Subscription error type: {type(subscribe_error).__name__}")
                        raise subscribe_error
                
                # Prepare the message
                message = '{"temperature": %d,"humidity": %d,"photosensor": %d}' % (
                    round(currentTempInFahrenheit),
                    round(currentHumidity),
                    round(photocell.value),
                )
                print(f"Attempting to publish message: {message}")
                
                mqtt.publish(secrets["mqtt_topic"], message)
                print("MQTT message published successfully")
                
            except MQTT.MMQTTException as mqtt_error:
                print(f"MQTT specific error: {mqtt_error}")
                print(f"MQTT error type: {type(mqtt_error).__name__}")
                network_connected = False
            except RuntimeError as runtime_error:
                print(f"Runtime error during MQTT operation: {runtime_error}")
                print(f"Runtime error type: {type(runtime_error).__name__}")
                network_connected = False
            except ConnectionError as conn_error:
                print(f"Connection error during MQTT operation: {conn_error}")
                print(f"Connection error type: {type(conn_error).__name__}")
                network_connected = False
            except Exception as general_error:
                print(f"Unexpected error during MQTT operation: {general_error}")
                print(f"Error type: {type(general_error).__name__}")
                network_connected = False
        else:
            print("Network not connected - skipping MQTT publish")

        temp_text_area.text = "%d°  %d%%" % (
            round(currentTempInFahrenheit),
            round(currentHumidity),
        )

        nowtime = time.localtime()
        printedtime = "%02d:%02d:%02d" % (
            nowtime.tm_hour,
            nowtime.tm_min,
            nowtime.tm_sec,
        )

        connection_status = "connected" if network_connected else "disconnected"
        print(
            "time=%s | temp= %d | humidity=%d | photocell=%d | network=%s"
            % (printedtime, currentTempInFahrenheit, currentHumidity, photocell.value, connection_status),
        )

        last_temp_check = time.monotonic()

    update_time()
    time.sleep(0.01)
