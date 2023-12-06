#!/bin/tcsh
#script used to build pacakge on E3DA server

set pyvers=3.10
set mlrel=2022b
set PSVers=dev

setenv gitorigin ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/
setenv gitbranch dev
setenv gitoption ""

ml dist/miniconda
ml e3da/ialrazi/$PSVers

#conda env remove -y -n PowerSynth2
conda create -y -n PowerSynth2 python=$pyvers

#May need new solver
#conda install -n base conda-libmamba-solver

conda activate PowerSynth2

#Install from channels: -c anaconda -c conda-forge
setenv CONDA_SOLVER libmamba
conda install -y networkx joblib seaborn numpy pandas scipy matplotlib-base   deap numba pydoe2 pykrige psutil pyside6=6.5

#post install script require matlab >2022b
setenv MatlabRoot "/e3da/dev/sdk/linux/matlab/R$mlrel"
set thisdir=$HOME/P/PS2/constructor
$thisdir/post_install.sh

####used for building Installer####
conda activate base
constructor "$thisdir" --output-dir "$HOME"

####Used for Testing on E3DA Server####
ml e3da/ialrazi/$PSVers

cp -r $e3da_ialrazi/PowerSynth2/pkg/work/Sample_Designs .

#run with macrofile for CLI, without it for GUI
PowerSynth2 Sample_Designs/2D_Case_5/macro_script.txt