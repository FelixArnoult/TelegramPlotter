# TelegramPlotter
Telegram bot search image on qwant with a given keyword. (Google not supported yet)

Convert image into a list of line and then into gcodes

Send it to a [printer](https://www.thingiverse.com/thing:1517211)

## Dependancies
```python
pip install pygcode
pip install scikit-image
pip install Pillow
pip install numpy
```

Edit /lib/python3.7/site-packages/pygcode/gcodes.py

```
class GCodeStartSpindleCW(GCodeStartSpindle):
    """M3: Start Spindle Clockwise"""
    #param_letters = set('S')  # S is it's own gcode, makes no sense to be here
    word_key = Word('M', 3)
```
Becomes
```
class GCodeStartSpindleCW(GCodeStartSpindle):
    """M3: Start Spindle Clockwise"""
    param_letters = set('S')  # S is it's own gcode, makes no sense to be here
    word_key = Word('M', 3)
```

Environnement variables :

* DRAWING_BOT_STREAM -> [file](https://github.com/grbl/grbl/blob/master/doc/script/stream.py) to send command to the bot which is working with python2, you should use python3. To convert it : [2to3](https://docs.python.org/2/library/2to3.html)

* TELEGRAM_TOKEN -> Telegram bot token

Following package must be installed:

* [convert](https://imagemagick.org/)
* [potrace](http://potrace.sourceforge.net/)
* [selenium](https://selenium-python.readthedocs.io/installation.html) with the firefox dirver

# Utilisation
```bash
  cd telegram && python3 v2.py
```

You may need to change the usb port to which the printer is connected: v2.py > class DrawingTelegram > self.usbPlotter

# TODO
* Support google image search
* Make sure streamer.py ends correctly
