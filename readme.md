# qwantImageToGcode
With a given keyword, fetch image from qwant and generate a gcode.
It takes randomly one of the first five result of search "coloriage *keyword*"

# Utilisation
```python
  python imageToGcode.py keyword
```
Edit /lib/python3.7/site-packages/pygcode/gcodes.py 
Line
```
class GCodeStartSpindleCW(GCodeStartSpindle):
    """M3: Start Spindle Clockwise"""
    #param_letters = set('S')  # S is it's own gcode, makes no sense to be here
    word_key = Word('M', 3)
```
Become
```
class GCodeStartSpindleCW(GCodeStartSpindle):
    """M3: Start Spindle Clockwise"""
    param_letters = set('S')  # S is it's own gcode, makes no sense to be here
    word_key = Word('M', 3)
```
Result in ./output.gcode
