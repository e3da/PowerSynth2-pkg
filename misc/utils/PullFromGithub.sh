#!/bin/sh
#pull changes from powersynth github

ThisDir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

PSRoot=`realpath $ThisDir/../../..`

: "${PREFIX:=$PSRoot}"

if [ $# -eq 0 ]; then
	arg="pull"
fi

cd "$PREFIX/pkg"
echo "INFO: Updating" `pwd`
git fetch && git $arg "$@"

test -d "$PREFIX/lib/site-packages" && cd "$PREFIX/lib/site-packages" || cd "$PREFIX/lib/python3."??/site-packages

cd "core"
echo "INFO: Updating" `pwd`
git fetch && git $arg "$@"


cd "../gui"
echo "INFO: Updating" `pwd`
git fetch && git $arg "$@"