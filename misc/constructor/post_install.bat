@echo off

::Set default variables

if "%pyvers%"=="" set pyvers=3.10
if "%MatlabRoot%"=="" set "MatlabRoot=%programfiles%\MATLAB\R2022b"

if "%gitorigin%"=="" set gitorigin=https://github.com/e3da/PowerSynth2-
if "%gitbranch%"=="" set gitbranch=main
if "%gitoption%"=="" set "gitoption=--depth 1"

if "%pipoption%"=="" set "pipoption=--upgrade"

if "%CONDA_PREFIX%"=="" set "CONDA_PREFIX=%UserProfile%\PowerSynth2"
if "%PREFIX%"=="" (set "PREFIX=%CONDA_PREFIX%")

::Try to get matlab version

::for /f "usebackq tokens=*" %%F in (`matlab -h`) do set line=%%F
::if "%line%"=="" (set mlvers=9.13) else (set mlvers=%line:~9,4%)

if not exist "%MatlabRoot%\VersionInfo.xml" for /f %%d in ('dir /b "%programfiles%\MATLAB"') do set "MatlabRoot=%programfiles%\MATLAB\%%d"
if not exist "%MatlabRoot%\VersionInfo.xml" goto ErrMatlab

for /f "delims=" %%l in ('findstr /c:"<version>" "%MatlabRoot%\VersionInfo.xml"') do set line=%%l
if "%line%"=="" (goto ErrMatlab) else (set "mlvers=%line:~11,4%")

echo "INFO: Install to PREFIX=%PREFIX% with MatlabRoot=%MatlabRoot%"

pip install %pipoption% "matlabengine==%mlvers%.*" -t "%PREFIX%\lib\site-packages"

echo "INFO: Download %gitbranch% source code from %gitorigin%*"

git clone -b %gitbranch% %gitoption% "%gitorigin%core" "%PREFIX%\lib\site-packages\core"
git clone -b %gitbranch% %gitoption% "%gitorigin%pkg" "%PREFIX%\pkg"
git clone -b %gitbranch% %gitoption% "%gitorigin%gui" "%PREFIX%\lib\site-packages\gui"

echo "INFO: Install Additional Packages"

::robocopy "%PREFIX%\pkg\lib\jmetal" "%PREFIX%\lib\site-packages\jmetal" /e
pip install jmetalpy~=1.6.0 %pipoption% --no-deps -t "%PREFIX%\lib\site-packages"

::No Longer Needed since v2.1
::mkdir "%PREFIX%\bin"
::copy "%PREFIX%\pkg\bin\PowerSynth2.py" "%PREFIX%\bin\"

echo "INFO: Creating executable and shortcuts"

for %%f in ("%PREFIX%\pkg\misc\win\PowerSynth2.exe" "%PREFIX%\pkg\misc\win\PowerSynth2*.lnk") do copy /y "%%f" "%PREFIX%\"

exit /b 0

:ErrMatlab
echo "ERROR: Matlab is not found at %MatlabRoot%. Post installation failed. "
pause
exit /b 99
