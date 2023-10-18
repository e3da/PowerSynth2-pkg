#!/bin/tcsh

set pyvers=3.10
set mlrel=2022b
set psvers=2.0

#set gitorigin=ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/
set gitorigin=git@github.com:e3da/PowerSynth2-
set gitbranch="main"
set gitoption=""

ml dist/miniconda
ml e3da/ialrazi/2.0

#conda env remove -y -n PowerSynth$psvers
conda create -y -n PowerSynth$psvers python=$pyvers

conda activate PowerSynth$psvers

#May need new solver
#conda install conda-libmamba-solver

#anaconda   conda-forge
conda install -y networkx joblib seaborn numpy Cython pandas scikit-learn scipy plotly matplotlib-base   deap numba pydoe2 pyside2 pykrige psutil

#for older matlab
#$CONDA_PREFIX/bin/python /e3da/dev/sdk/linux/matlab/R$mlrel/extern/engines/python/Ysetup.py install --prefix=$CONDA_PREFIX

#after 2022b
set mlvers=`sed -n 's/^.*<version>\([0-9]\+\.[0-9]\+\).*$/\1/p' /e3da/dev/sdk/linux/matlab/R$mlrel/VersionInfo.xml`
setenv LD_LIBRARY_PATH /e3da/dev/sdk/linux/matlab/R$mlrel/bin/glnxa64/:${LD_LIBRARY_PATH}
pip install matlabengine=="$mlvers.*" -t $CONDA_PREFIX/lib/python$pyvers/site-packages/

#need unshallow for full history
git clone --depth 1 -b $gitbranch $gitoption ${gitorigin}core $CONDA_PREFIX/lib/python$pyvers/site-packages/core
git clone --depth 1 -b $gitbranch $gitoption ${gitorigin}pkg $CONDA_PREFIX/pkg
git clone --depth 1 -b $gitbranch $gitoption ${gitorigin}gui $CONDA_PREFIX/lib/python$pyvers/site-packages/gui

ln -sf ../pkg/bin/PowerSynth2.py $CONDA_PREFIX/bin/PowerSynth2

#used for Pack Env
sed -i 's#/e3da/dev/sdk/linux/matlab/#/usr/local/MATLAB/#' $CONDA_PREFIX/lib/python$pyvers/site-packages/matlab/engine/_arch.txt
conda activate base
conda pack -p $e3da_ialrazi/PowerSynth$psvers -f -o ~/Downloads/PowerSynth$psvers.tgz --ignore-missing-files
chmod 644 ~/Downloads/PowerSynth$psvers.tgz 
conda activate PowerSynth$psvers
sed -i 's#/usr/local/MATLAB/#/e3da/dev/sdk/linux/matlab/#' $CONDA_PREFIX/lib/python$pyvers/site-packages/matlab/engine/_arch.txt


#for running
ml e3da/ialrazi/2.0

cp -r $e3da_ialrazi/PowerSynth2.0/pkg/work/Sample_Designs .

#run with macrofile for CLI, without it for GUI
PowerSynth2 Sample_Designs/2D_Case_5/macro_script.txt
