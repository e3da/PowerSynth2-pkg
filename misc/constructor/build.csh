#!/bin/tcsh
#script used to build pacakge on E3DA server

setenv PYVers 3.10
setenv PSVers 2.2

setenv gitbranch "v$PSVers"
setenv gitoption ""

#for dev only
#setenv PSVers dev
if ("$PSVers" !~ [1-9]*) setenv gitbranch "$PSVers"

#setenv gitorigin ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/

ml dist/miniconda
ml e3da/ialrazi/$PSVers

#conda env remove -y -n PowerSynth2
conda create -y --override-channels -c main -n PowerSynth2 python=$PYVers networkx joblib seaborn numpy=2.1 pandas scipy matplotlib-base psutil numba

conda activate PowerSynth2

conda install -y --override-channels -c conda-forge pyside6=6.5 deap pydoe2 pykrige

#Allow interactive shell 
if($?prompt) setenv MatlabRoot `ls /e3da/dev/sdk/linux/matlab/R202[2-9]*/ -1d |& tail -1` && set ThisDir=$HOME/git/PowerSynth/pkg/misc/constructor
if(! $?prompt) set ThisDir=`dirname $0`

#post install script require matlab >2022b
$ThisDir/post_install.sh

#for e3da lab
if($?prompt) sed -i "s#/usr/local/MATLAB/[^/]\+/#$MatlabRoot/#" $e3da_ialrazi/PowerSynth2/lib/python$PYVers/site-packages/matlab/engine/_arch.txt

####used for building Installer####
conda activate base
constructor "$ThisDir" --output-dir "$HOME"

####Used for Testing on E3DA Server####
ml e3da/ialrazi/$PSVers

cp -r $e3da_ialrazi/PowerSynth2/pkg/work/Sample_Designs .

#run with macrofile for CLI, without it for GUI
PowerSynth2 Sample_Designs/2D_Case_5/macro_script.txt
