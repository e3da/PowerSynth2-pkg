#!/bin/tcsh

set pyvers=3.10
set mlrel=2022b
set psvers=2.0

set gitorigin=ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/
set gitbranch="PS2"
set gitoption=""

ml dist/anaconda
ml e3da/ialrazi/RC5

#conda env remove -y -n PowerSynth$psvers
conda create -y -n PowerSynth$psvers python=$pyvers

conda activate PowerSynth$psvers

#base pacakges for backend
conda install -y -c anaconda networkx joblib seaborn numpy Cython pandas scikit-learn scipy plotly
conda install -y -c conda-forge deap numba matplotlib-base pydoe2 pyside2 pykrige psutil

#for older matlab
#$CONDA_PREFIX/bin/python /e3da/dev/sdk/linux/matlab/R$mlrel/extern/engines/python/Ysetup.py install --prefix=$CONDA_PREFIX

#after 2022b
set mlvers=`sed -n 's/^.*<version>\([0-9]\+\.[0-9]\+\).*$/\1/p' /e3da/dev/sdk/linux/matlab/R$mlrel/VersionInfo.xml`
setenv LD_LIBRARY_PATH /e3da/dev/sdk/linux/matlab/R$mlrel/bin/glnxa64/:${LD_LIBRARY_PATH}
pip install install matlabengine=="$mlvers.*" -t $CONDA_PREFIX/lib/python$pyvers/site-packages/

git clone -b $gitbranch $gitoption ${gitorigin}core $CONDA_PREFIX/lib/python$pyvers/site-packages/core
git clone -b $gitbranch $gitoption ${gitorigin}pkg $CONDA_PREFIX/pkg
git clone -b $gitbranch $gitoption ${gitorigin}gui $CONDA_PREFIX/lib/python$pyvers/site-packages/gui

ln -sf ../pkg/bin/PowerSynth2.py $CONDA_PREFIX/bin/PowerSynth2

#testing
ml e3da/ialrazi/RC5

cp -r $e3da_ialrazi/PowerSynth2.0/pkg/work/Sample_Designs .

#run with macrofile for CLI, without it for GUI
PowerSynth2 Sample_Designs/2D_Case_5/macro_script.txt
