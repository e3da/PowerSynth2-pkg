#!/bin/sh
#post conda installation script for pip install and clone git codes

#search for matlab >2022b
MatlabSearch=`ls /usr/local/MATLAB/R202[3-9]*/VersionInfo.xml -1 2>/dev/null | tail -1` 

#default variables
: "${PYVers:=3.10}" "${MatlabRoot:=/usr/local/MATLAB/R2022b}"
: "${gitorigin:=https://github.com/e3da/PowerSynth2-}" "${gitbranch:=main}" "${gitoption:=--depth 1}"
: "${pipoption:=--upgrade}"

#default install path is current conda environment or home folder
ThisDir=$(dirname -- "$0")
: "${CONDA_PREFIX:=$ThisDir/../../..}" "${PREFIX:=$CONDA_PREFIX}"

if [ ! -f "$PREFIX/bin/pip" ]; then
	echo "ERROR: $PREFIX is not a Conda environment. Post installation failed."
	sleep 2
	exit 10
fi

if [ ! -f "$MatlabRoot/VersionInfo.xml" ]; then
	if [ -f "$MatlabSearch" ]; then
		MatlabRoot=`dirname "$MatlabSearch"`
	else
		echo "ERROR: Matlab is not found at $MatlabRoot. Post installation failed."
		sleep 2
		exit 99
	fi
fi

echo "INFO: Install to PREFIX=$PREFIX with python $PYVers and MatlabRoot=$MatlabRoot"

mlvers=`sed -n 's/^.*<version>\([0-9]\+\.[0-9]\+\).*$/\1/p' $MatlabRoot/VersionInfo.xml`
export LD_LIBRARY_PATH="$MatlabRoot/bin/glnxa64/:$LD_LIBRARY_PATH"

#pip install additional packages not in anaconda
echo "INFO: Install Additional Packages"
for pkg in "matlabengine==$mlvers"
do
	"$PREFIX/bin/pip" install "$pkg.*" $pipoption -t "$PREFIX/lib/python$PYVers/site-packages"
done

for pkg in "jmetalpy~=1.6.0"
do
	"$PREFIX/bin/pip" install "$pkg" $pipoption --no-deps -t "$PREFIX/lib/python$PYVers/site-packages"
done

if [ -d "$PREFIX/pkg" ]; then 
	rm -rf "$PREFIX/lib/python$PYVers/site-packages/core" "$PREFIX/pkg" "$PREFIX/lib/python$PYVers/site-packages/gui"
fi

echo "INFO: Download $gitbranch source code from ${gitorigin}*"

git clone -c advice.detachedHead=false -b $gitbranch $gitoption ${gitorigin}core "$PREFIX/lib/python$PYVers/site-packages/core"
git clone -c advice.detachedHead=false -b $gitbranch $gitoption ${gitorigin}pkg "$PREFIX/pkg"
git clone -c advice.detachedHead=false -b $gitbranch $gitoption ${gitorigin}gui "$PREFIX/lib/python$PYVers/site-packages/gui"

echo "INFO: Creating executable and shortcuts"

ln -sf ../pkg/bin/PowerSynth2.py $PREFIX/bin/PowerSynth2

echo "INFO: Post installation completed."
