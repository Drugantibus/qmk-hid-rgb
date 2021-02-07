# qmk-hid-rgb

This repo contains a PoC of using qmk's raw HID feature to control RGB on a keyboard. `hid_rgb.py` defines the primitives, and `alt_notification.py` is a simple CLI implementation. I've also included `dbus_intercept.py`, which is a more realistic implementation that automatically sends an RGB notification whenever I receive a Telegram message, using `dbus`.

## Environment

### Host

This was developed on a Linux system, using a Drop ALT keyboard. Modifying it to work on your OS/keyboard should be pretty straightforward. First change the `vid`, `pid`, `usage_page`, and `usage_id` variables in `__init__` to match your keyboard's, if it's not an ALT. You can find the first two in its `config.h`, while the HID params *should* be `0xFF60` and `0x61` respectively, although I had to override them in my `config.h` because Drop doesn't like to do things the standard way. You may also need to change the hardcoded message length in `pad_message()` if your board uses a 32 byte `RAW_EPSIZE`. Please refer to [the docs](https://docs.qmk.fm/using-qmk/software-features/feature_rawhid) and [my keymap](https://github.com/Drugantibus/qmk_firmware/tree/master/keyboards/massdrop/alt/keymaps/drugo) for more info. Then, follow the instructions [here](https://pypi.org/project/hid/) to configure the `hid` module to work on your OS.

### Keyboard

Now, you need to configure the raw HID feature on your board. You can refer to my keymap directory linked above, but the basic steps are:

* Enable the feature by adding `RAW_ENABLE = yes` in your `rules.mk`
* It may be necessary to `#define RAW_USAGE_PAGE/ID = <value>` in your `config.h`. You must do this on Drop boards, I'm not sure about others.
* Implement `raw_hid_receive()` in your `keymap.c`. I suggest copy-pasting my implementation and then changing it to your needs.

## Usage

After importing the Alt class and creating an object, here are the functions available:

`get_state()`: Reads the current RGB mode (aka LED_FLAGS)

`set_state(state)`: Sets the RGB mode

`next_animation()`: Goes to the next RGB animation

`send_notification(mode, color, duration)`: Sets the specified color (in form of a 3 byte array) on part of the keyboard based on mode, then resets the previous state after `duration` seconds (defaults to 1).

`set_color(color)`: Similar to `send_notification`, but doesn't restore the previous state. No mode selection for now

`set_single_led(index, color)`: Sets a single led to the given color. (0-indexed)

`set_zone(index, color)`: Sets a zone to the given color, defined in my keymap as rows and sections of the underglow.

Every function that has the `color` argument also has a `_rgb(..., r, g, b)` that accepts color as 3 0-255 ints, and a `_color(..., name)` that accepts a human-readable color defined in `name2bytes`.

 Please note that you should manually call `close()` on your instance at the end of your program, these functions leave the connection open on purpose.

## Contributing
Any pull request, feature request, question, issue etc. is more than welcome! Don't hesitate to request a feature or modification you'd like (keeping in mind that this is not intended to be an OpenRGB style project... At least for now ;) )

## TODO
- [ ] Add HSV support
- [ ] Generalize more to make support for other keyboards easier
- [ ] Restructuring of code?
- [ ] You tell me ;)  