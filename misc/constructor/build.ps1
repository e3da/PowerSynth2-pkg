#miniconda powershell prompt

$Env:PYVers="3.10"

$Env:PSVers="2.2"

$Env:gitbranch="v$Env:PSVers"
$Env:gitoption=""

#for dev branch only
#$Env:PSVers="dev"
if (!("$Env:PSVers" -like "[1-9]*")) { $Env:gitbranch="$Env:PSVers" }

#$Env:gitorigin="ssh://peng-srv2.csce.uark.edu/data/project/PowerSynth/git/"

#conda env remove -y -n PowerSynth2-$Env:PSVers
conda create -y --override-channels -c main -n PowerSynth2-$Env:PSVers python=$Env:PYVers networkx joblib seaborn numpy=2.1 pandas scipy matplotlib-base psutil numba

conda activate PowerSynth2-$Env:PSVers

conda install -y --override-channels -c conda-forge pyside6=6.5 deap pydoe2 pykrige

#Allow interactive shell 
if ($PSScriptRoot) {
	$ThisDir=$PSScriptRoot
} else {
	$ThisDir="H:\git\PowerSynth\pkg\misc\constructor"
}

#post install script require matlab >2022b	
Start-Process -FilePath "$ThisDir\post_install.bat" -Wait -NoNewWindow

#Build installer
conda activate base
constructor "$ThisDir" --output-dir "$HOME"
