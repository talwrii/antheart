# heart-target

Various utilities related to heart rate. Early development

# Prior work

Adapted from https://www.johannesbader.ch/2014/06/track-your-heartrate-on-raspberry-pi-with-ant/ . This saved a lot of time.

# Basic usage

```
pip install --user git+https://github.com/baderj/python-ant.git#egg=ant # Requires tweaked pytohn-ant
python setup.py develop --user
antheart target 90 # Keep your heart rate near 90, warn if it differs largely
```

# Bugs

I've managed to get this to temporarily break my ant+ interface before (Resource busy)
This was fixed by unplugging my dongle and plugging in again. Bad luck if you don't have a dongle... 
because you'll probably have to restart your computer...
