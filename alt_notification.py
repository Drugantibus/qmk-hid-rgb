#!/home/drugo/.pyenv/shims/python

import sys
from hid_rgb import Alt

alt = Alt()
args = sys.argv
if len(args) == 1:
    print("[?] No mode specified, defaulting to full.")
    args.append('full')
if len(args) == 2:
    print("[?] No color specified, defaulting to white.")
    args.append('white')
alt.send_notification_color(args[1], args[2])
alt.close()