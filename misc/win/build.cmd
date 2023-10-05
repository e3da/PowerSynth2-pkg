set pyvers=3.10
set psvers=2.0
set mlvers=9.13

set gitorigin=ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/

#conda env remove -y -n PowerSynth%psvers%
conda create -y -n PowerSynth%psvers% python=%pyvers%

conda activate PowerSynth%psvers%

###

#base pacakges for backend
conda install -y -c anaconda networkx joblib seaborn numpy Cython pandas scikit-learn scipy plotly
conda install -y -c conda-forge deap numba matplotlib-base pydoe2 pyside2 pykrige psutil


#after 2022b
pip install "matlabengine==%mlvers%.*"
####

git clone -b PS2 %gitorigin%core %CONDA_PREFIX%\lib\site-packages\core
git clone -b PS2 %gitorigin%pkg %CONDA_PREFIX%\pkg
git clone -b PS2 %gitorigin%gui %CONDA_PREFIX%\lib\site-packages\gui

mkdir %CONDA_PREFIX%\bin
copy %CONDA_PREFIX%\pkg\bin\PowerSynth2.py %CONDA_PREFIX%\bin\
copy %CONDA_PREFIX%\pkg\misc\win\PowerSynth2*.lnk  %CONDA_PREFIX%\

#Pack Env
conda activate base
conda pack -n PowerSynth%psvers% -o %USERPROFILE%\Desktop\PowerSynth%psvers%.zip


#source /c/ProgramData/Anaconda3/etc/profile.d/conda.sh
#conda activate PowerSynth2.0

#python $CONDA_PREFIX/bin/PowerSynth2-CLI.py $CONDA_PREFIX/pkg/work/Sample_Designs/2D_Case_5/macro_script.txt



