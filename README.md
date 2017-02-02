# heart-target

A feedback system to help you keep your heart rate within a target range.

# Basic usage

```
python setup.py develop --user
antheart target 90 # aim for a heart rate of 90
```

# Prior work

Adapted from https://www.johannesbader.ch/2014/06/track-your-heartrate-on-raspberry-pi-with-ant/ . This saved a lot of time.

# Bugs

I've managed to get this to temporarily break my ant+ interface before (Resource busy)
This was fixed by unplugging my dongle and plugging in again. Bad luck if you don't have a dongle... 
because you'll probably have to restart your computer...
