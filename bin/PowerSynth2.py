#!/usr/bin/env python
# This is the main exe for PowerSynth2

import sys

from core.PS2Core import PS2Core
from gui.PS2GUI import PS2GUI

if __name__ == "__main__":  
    if len(sys.argv)<2:
        print("----------------------PowerSynth 2 v2.0: GUI version------------------")
        PS2GUI().run()
    else:
        print("----------------------PowerSynth 2 v2.0: CLI version------------------")
        PS2Core(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else "").run()

