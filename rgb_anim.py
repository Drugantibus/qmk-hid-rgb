from hid_rgb import Alt
from time import sleep

def go_around(color):
    for i in range(67, 105):
        alt.set_single_led_color(i, color)
        sleep(0.025)
    sleep(1)
    alt.set_state()

def ripple(color):
    a = 74
    for i in range(8):
        alt.set_single_led_color(a + i, color)
        alt.set_single_led_color(a - i, color)
        sleep(0.035)
    # sleep(1)
    # alt.set_state()

def rainbow():
    for led in range(105):
        alt.set_single_led_hsv(led, led*3.5, 100, 100)
        sleep(0.025)

def bottom_rainbow():
    for led in range(67, 105):
        alt.set_single_led_hsv(led, led*5, 100, 100)
        sleep(0.025)


alt = Alt()
ripple('white')
# sleep(0.175)
ripple('aqua')
# sleep(0.5)
ripple('orange')
# bottom_rainbow()
# sleep(2)
alt.set_state()