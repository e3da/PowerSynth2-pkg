#!/bin/bash -e

Dir=$(dirname "$0")

for file in $Dir/*/macro_script.txt
do
	PowerSynth2 $file
done
