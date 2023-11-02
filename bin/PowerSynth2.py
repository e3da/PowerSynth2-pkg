#!/usr/bin/env python
# This is the main exe for PowerSynth2

import sys
from core.PSCore import PSEnv

if __name__ == "__main__":  
    print(f"----------------------PowerSynth 2 v{PSEnv.PSVers}:", end="")
    if len(sys.argv)<2:
        from gui.PS2GUI import PS2GUI
        print(" GUI version------------------")
        PS2GUI().run()
    else:
        from core.PS2CLI import PS2CLI
        print(" CLI version------------------")
        PS2CLI(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else "").run()

