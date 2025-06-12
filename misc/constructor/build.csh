#!/bin/tcsh
#script used to build pacakge on E3DA server

set pyvers=3.10
set mlrel=2022b
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
conda create -y --override-channels -c main -n PowerSynth2 python=$pyvers networkx joblib seaborn numpy=2.1 pandas scipy matplotlib-base psutil numba

conda activate PowerSynth2

conda install -y --override-channels -c conda-forge pyside6=6.5 deap pydoe2 pykrige

#Allow interactive shell 
if($?prompt) setenv MatlabRoot "/e3da/dev/sdk/linux/matlab/R$mlrel" && set thisdir=$HOME/git/PowerSynth/pkg/misc/constructor
if(! $?prompt) set thisdir=`dirname $0`

#post install script require matlab >2022b
$thisdir/post_install.sh

####used for building Installer####
conda activate base
constructor "$thisdir" --output-dir "$HOME"

####Used for Testing on E3DA Server####
ml e3da/ialrazi/$PSVers

cp -r $e3da_ialrazi/PowerSynth2/pkg/work/Sample_Designs .

#run with macrofile for CLI, without it for GUI
PowerSynth2 Sample_Designs/2D_Case_5/macro_script.txt
