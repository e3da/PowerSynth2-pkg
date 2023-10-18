::miniconda cmd prompt
set pyvers=3.10
set psvers=2.0
set mlvers=9.13

::set gitorigin=ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/
set gitorigin=git@github.com:e3da/PowerSynth2-
set gitbranch=main

::conda env remove -y -n PowerSynth%psvers%
conda create -y -n PowerSynth%psvers% python=%pyvers%

conda activate PowerSynth%psvers%

::May need new solver
::conda install conda-libmamba-solver

::anaconda   conda-forge
conda install -y networkx joblib seaborn numpy Cython pandas scikit-learn scipy plotly matplotlib-base   deap numba pydoe2 pyside2 pykrige psutil

::after 2022b
pip install "matlabengine==%mlvers%.*"

git clone --depth 1 -b %gitbranch% %gitorigin%core %CONDA_PREFIX%\lib\site-packages\core
git clone --depth 1 -b %gitbranch% %gitorigin%pkg %CONDA_PREFIX%\pkg
git clone --depth 1 -b %gitbranch% %gitorigin%gui %CONDA_PREFIX%\lib\site-packages\gui

mkdir %CONDA_PREFIX%\bin
copy %CONDA_PREFIX%\pkg\bin\PowerSynth2.py %CONDA_PREFIX%\bin\
copy %CONDA_PREFIX%\pkg\misc\win\PowerSynth2*.lnk  %CONDA_PREFIX%\

::Pack Env
conda activate base
conda pack -n PowerSynth%psvers% -f -o %USERPROFILE%\Desktop\PowerSynth%psvers%.zip

