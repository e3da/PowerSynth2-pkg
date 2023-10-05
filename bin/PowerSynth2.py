#!/usr/bin/env python
# This is the main exe for PowerSynth2

import sys

if __name__ == "__main__":  
    if len(sys.argv)<2:
        from gui.PS2GUI import PS2GUI
        print("----------------------PowerSynth 2 v2.0: GUI version------------------")
        PS2GUI().run()
    else:
        from core.PS2CLI import PS2CLI
        print("----------------------PowerSynth 2 v2.0: CLI version------------------")
        PS2CLI(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else "").run()

