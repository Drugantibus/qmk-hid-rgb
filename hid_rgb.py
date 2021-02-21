
"""
Possible message format:
    0x01: Sets the LED state
        0x01: All LEDs on
        0x02: Keylight only
        0x03: Underglow only
        0x04: All LEDs off
        0x05: Go to next RGB animation
    0x02: Notifications
        0x01: Set the "bottom" (user-facing) part of the underglow to a specific color
            0xXX: Red value
            0xXX: Green value
            0xXX: Blue value
            (hereafter (colors))
        0x02: Set the whole keyboard to a color
            (colors)
        0x03: Set the whole underglow to a color
            (colors)
    0x03: Get the current LED state
        No parameters, returns (sends) a value as in the 0x01 section
    0x04: Control single or group of LEDs
        0x01: Change a single LED's color
            0xXX: LED number
            (colors)
        0x02: Change a group of LEDs
            0x01-0x05: nth row
                (colors)
            0x06: Bottom underglow
                (colors)
            0x07: Right underglow
                (colors)
            0x08: Top underglow
                (colors)
            0x09: Left underglow
                (colors)
"""

import math
import hid
from time import sleep

# NOTE: Change the 64 here if your board uses 32-byte RAW_EPSIZE
def pad_message(payload):
    return payload + b'\x00' * (64 - len(payload))

def tobyte(data):
    if type(data) is bytes:
        return data
    else:
        return (data).to_bytes(1, 'big')

def tobytes(data):
    out = b''
    for num in data:
        out += tobyte(num)
    return out

def hsv_to_rgb(h, s, v):
    h /= 360
    s /= 100
    v /= 100
    i = math.floor(h*6)
    f = h*6 - i
    p = v * (1-s)
    q = v * (1-f*s)
    t = v * (1-(1-f)*s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i%6)]

    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    return r, g, b


class Alt:

    device = None
    name2bytes = {
                        # R    G    B
        'red'   : bytes([255,   0,   0]),
        'green' : bytes([0  , 255,   0]),
        'blue'  : bytes([0  ,   0, 255]),
        'aqua'  : bytes([0  , 200,  50]),
        'orange': bytes([255,  50,   0]),
        'white' : bytes([255, 255, 255]),
    }

    # Change the values here if not using an ALT
    def __init__(self):
        vid = int.from_bytes(b'\x04\xD8', 'big')
        pid = int.from_bytes(b'\xEE\xD3', 'big')
        usage_page = int.from_bytes(b'\xFF\x31', 'big')
        usage_id = int.from_bytes(b'\x62', 'big')

        devices = hid.enumerate()
        for device in devices:
            if device['vendor_id'] == vid and device['product_id'] == pid and device['usage_page'] == usage_page and device['usage'] == usage_id:
                self.device = hid.Device(path=device['path'])
                break
        if self.device is None:
            print("[!!] Keyboard not found, quitting.")
            exit(1)

    def close(self):
        self.device.close()

    def send(self, data):
        self.device.write(pad_message(data))

    def get_state(self):
        self.send(tobyte(3))
        state = self.device.read(1) # 1=all, 2=key, 3=under, 4=none
        return state

    def set_state(self, state = b'\x01'):
        data = tobytes([1, state])
        self.send(data)

    def next_animation(self):
        data = tobytes([1, 5])
        self.send(data)

    # Color is a 3-byte array
    def send_notification(self, mode, color, duration = 1):
        if mode not in ['full', 'bottom', 'under']: 
            print("[?] Invalid notification mode, valid options are full, bottom and under.\n[*] Defaulting to full...")
            mode = 'full'
        previous_state = self.get_state()
        if mode == 'bottom':
            data = tobytes([2, 1, color])
        elif mode == 'full':
            data = tobytes([2, 2, color])
        elif mode == 'under':
            data = tobytes([2, 3, color])
        self.send(data)
        sleep(duration)
        self.set_state(previous_state)
        # !!! caller should close the connection

    def send_notification_rgb(self, mode, r, g, b, duration = 1):
        try:
            self.send_notification(mode, tobytes([r, g, b]), duration)
        except ValueError:
            print("[!] RGB values must be 0-255.\n[*] Defaulting to white.")
            self.send_notification(mode, tobytes([255, 255, 255]), duration)

    def send_notification_hsv(self, mode, h, s, v, duration = 1):
        if 0<=s<= 100 and 0<=v<=100:
            r, g, b = hsv_to_rgb(h, s, v)
            self.send_notification_rgb(mode, r, g, b, duration)
        else:
            print("[!] s and v values must be 0-100")

    def send_notification_color(self, mode, name, duration = 1):
        if name not in self.name2bytes:
            print("[?] Unrecognized name. Valid options are:")
            for color in self.name2bytes.keys(): print(f"[-] {color}")
            print("[*] Defaulting to white...")
            name = 'white'
        color = self.name2bytes.get(name)
        self.send_notification(mode, color, duration)

    def set_color(self, mode, color):
        if mode == 'bottom':
            data = tobytes([2, 1, color])
        elif mode == 'full':
            data = tobytes([2, 2, color])
        elif mode == 'under':
            data = tobytes([2, 3, color])
        self.send(data)

    def set_color_rgb(self, mode, r, g, b):
        try:
            self.set_color(mode, tobytes([r, g, b]))
        except ValueError:
            print("[!] RGB values must be 0-255.\n[*] Defaulting to white.")
            self.set_color(tobytes([255, 255, 255]))
        
    def set_color_hsv(self, mode, h, s, v):
        if 0<=s<= 100 and 0<=v<=100:
            r, g, b = hsv_to_rgb(h, s, v)
            self.set_color_rgb(mode, r, g, b)
        else:
            print("[!] s and v values must be 0-100")

    def set_color_name(self, mode, name):
        if name not in self.name2bytes:
            print("[?] Unrecognized name. Valid options are:")
            for color in self.name2bytes.keys(): print(f"[-] {color}")
            print("[*] Defaulting to white...")
            name = 'white'
        color = self.name2bytes.get(name)
        self.set_color(mode, color)

    def set_single_led(self, index, color):
        data = tobytes([4, 1, index, color])
        self.send(data)
    
    def set_single_led_rgb(self, index, r, g, b):
        try:
            self.set_single_led(index, tobytes([r, g, b]))
        except ValueError:
            print("[!] RGB values must be 0-255.\n[*] Defaulting to white.")
            self.set_single_led(index, tobytes([255, 255, 255]))

    def set_single_led_hsv(self, index, h, s, v):
        if 0<=s<= 100 and 0<=v<=100:
            r, g, b = hsv_to_rgb(h, s, v)
            self.set_single_led_rgb(index, r, g, b)
        else:
            print("[!] s and v values must be 0-100")

    def set_single_led_color(self, index, name):
        if name not in self.name2bytes:
            print("[?] Unrecognized name. Valid options are:")
            for color in self.name2bytes.keys(): print(f"[-] {color}")
            print("[*] Defaulting to white...")
            name = 'white'
        color = self.name2bytes.get(name)
        self.set_single_led(index, color)

    def set_zone(self, index, color):
        data = tobytes([4, 2, index, color])
        self.send(data)

    def set_zone_rgb(self, index, r, g, b):
        try:
            self.set_zone(index, tobytes([r, g, b]))
        except ValueError:
            print("[!] RGB values must be 0-255.\n[*] Defaulting to white.")
            self.set_zone(index, tobytes([255, 255, 255]))

    def set_zone_hsv(self, index, h, s, v):
        if 0<=s<= 100 and 0<=v<=100:
            r, g, b = hsv_to_rgb(h, s, v)
            self.set_zone_rgb(index, r, g, b)
        else:
            print("[!] s and v values must be 0-100")

    def set_zone_color(self, index, name):
        if name not in self.name2bytes:
            print("[?] Unrecognized name. Valid options are:")
            for color in self.name2bytes.keys(): print(f"[-] {color}")
            print("[*] Defaulting to white...")
            name = 'white'
        color = self.name2bytes.get(name)
        self.set_zone(index, color)

class Animation:

    keyboard = None

    def __init__(self):
        self.keyboard = Alt()

    def go_around(self, color):
        for i in range(67, 105):
            self.keyboard.set_single_led_color(i, color)
            sleep(0.05)
        # sleep(1)
        # self.keyboard.set_state()

    def ripple(self, color):
        a = 74
        for i in range(8):
            self.keyboard.set_single_led_color(a + i, color)
            self.keyboard.set_single_led_color(a - i, color)
            sleep(0.025)
        # sleep(1)
        # self.keyboard.set_state()