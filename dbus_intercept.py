#!/home/drugo/.pyenv/shims/python

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from hid_rgb import Alt

def msg_cb(bus, msg):
    args = msg.get_args_list()
    # print("Notification from '%s'" % args[0])
    # print("Summary: %s" % args[3])
    # print("Body: %s" % args[4])
    if args[0] == 'Telegram Desktop':
        alt = Alt()
        if "Cami" in args[3]: #"summary" is contact name
            alt.send_notification_color('full', 'aqua')
        else:
            alt.send_notification_color('under', 'aqua')
        alt.close()

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    string = "interface='org.freedesktop.Notifications',member='Notify', eavesdrop='true'"
    bus.add_match_string(string)
    bus.add_message_filter(msg_cb)

    mainloop = GLib.MainLoop()
    mainloop.run()
    