#!/bin/sh
#post conda installation script for pip install and clone git codes

#search for matlab >2022
MatlabSearch=`ls /usr/local/MATLAB/R202[3-9]*/VersionInfo.xml -1tr 2>&1` 

#default variables
: "${pyvers:=3.10}" "${MatlabRoot:=/usr/local/MATLAB/R2022b}"
: "${gitorigin:=https://github.com/e3da/PowerSynth2-}" "${gitbranch:=main}" "${gitoption:=--depth 1}"
: "${pipoption:=--upgrade}"

#default install path is current conda environment or home folder
: "${CONDA_PREFIX:=$HOME/PowerSynth2}" "${PREFIX:=$CONDA_PREFIX}"

if [ -z "$PREFIX" ] || [ -z "$MatlabRoot" ]; then
	echo 'ERROR: $PREFIX or $MatlabRoot is empty.'
	exit
fi

if [ ! -f "$MatlabRoot/VersionInfo.xml" ]; then
	if [ -f "$MatlabSearch" ]; then
		MatlabRoot=`dirname "$MatlabSearch"`
	else
		echo "ERROR: Matlab is not found at $MatlabRoot. Post installation script failed."
		exit
	fi
fi

echo "INFO: Install to PREFIX=$PREFIX with MatlabRoot=$MatlabRoot"

mlvers=`sed -n 's/^.*<version>\([0-9]\+\.[0-9]\+\).*$/\1/p' $MatlabRoot/VersionInfo.xml`
export LD_LIBRARY_PATH="$MatlabRoot/bin/glnxa64/:$LD_LIBRARY_PATH"

#pip install additional packages not in anaconda
echo "INFO: Install Additional Packages"
for pkg in "matlabengine==$mlvers.*"
do
	pip install "$pkg" $pipoption -t "$PREFIX/lib/python$pyvers/site-packages"
done

for pkg in "jmetalpy~=1.6.0"
do
	pip install "$pkg" $pipoption --no-deps -t "$PREFIX/lib/python$pyvers/site-packages"
done

if [ -d "$PREFIX/pkg" ]; then 
	"$PREFIX/pkg/misc/utils/PullFromGithub.sh"
else
	echo "INFO: Download $gitbranch source code from ${gitorigin}*"

	git clone -b $gitbranch $gitoption ${gitorigin}core "$PREFIX/lib/python$pyvers/site-packages/core"
	git clone -b $gitbranch $gitoption ${gitorigin}pkg "$PREFIX/pkg"
	git clone -b $gitbranch $gitoption ${gitorigin}gui "$PREFIX/lib/python$pyvers/site-packages/gui"
fi

echo "INFO: Creating executable and shortcuts"

ln -sf ../pkg/bin/PowerSynth2.py $PREFIX/bin/PowerSynth2
