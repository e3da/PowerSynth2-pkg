@echo off

::Set default variables

if "%PYVers%"=="" set PYVers=3.10
if "%MatlabRoot%"=="" set "MatlabRoot=%programfiles%\MATLAB\R2022b"

if "%gitorigin%"=="" set gitorigin=https://github.com/e3da/PowerSynth2-
if "%gitbranch%"=="" set gitbranch=main
if "%gitoption%"=="" set "gitoption=--depth 1"

if "%pipoption%"=="" set "pipoption=--upgrade"

if "%CONDA_PREFIX%"=="" set "CONDA_PREFIX=%~dp0..\..\.."
if "%PREFIX%"=="" (set "PREFIX=%CONDA_PREFIX%")
if not exist "%PREFIX%\scripts\pip.exe" goto ErrConda

::Try to get matlab version

::for /f "usebackq tokens=*" %%F in (`matlab -h`) do set line=%%F
::if "%line%"=="" (set mlvers=9.13) else (set mlvers=%line:~9,4%)

if not exist "%MatlabRoot%\VersionInfo.xml" for /f %%d in ('dir /b "%programfiles%\MATLAB"') do set "MatlabRoot=%programfiles%\MATLAB\%%d"
if not exist "%MatlabRoot%\VersionInfo.xml" goto ErrMatlab

echo "INFO: Install to PREFIX=%PREFIX% with python %PYVers% and MatlabRoot=%MatlabRoot%"
for /f "delims=" %%l in ('findstr /c:"<version>" "%MatlabRoot%\VersionInfo.xml"') do set line=%%l
if "%line%"=="" (goto ErrMatlab) else (set "mlvers=%line:~11,4%")

echo "INFO: Install Additional Packages"
for %%p in ("matlabengine==%mlvers%") do "%PREFIX%\scripts\pip" install %pipoption% "%%p.*" -t "%PREFIX%\lib\site-packages"

for %%p in ("jmetalpy~=1.6.0") do "%PREFIX%\scripts\pip" install %pipoption% "%%p" --no-deps -t "%PREFIX%\lib\site-packages"

if exist "%PREFIX%\pkg" (
	rmdir /s /q "%PREFIX%\lib\site-packages\core" "%PREFIX%\pkg" "%PREFIX%\lib\site-packages\gui"
)

echo "INFO: Download %gitbranch% source code from %gitorigin%*"

git clone -c advice.detachedHead=false -b %gitbranch% %gitoption% "%gitorigin%core" "%PREFIX%\lib\site-packages\core"
git clone -c advice.detachedHead=false -b %gitbranch% %gitoption% "%gitorigin%pkg" "%PREFIX%\pkg"
git clone -c advice.detachedHead=false -b %gitbranch% %gitoption% "%gitorigin%gui" "%PREFIX%\lib\site-packages\gui"

::No Longer Needed since v2.1
::mkdir "%PREFIX%\bin"
::copy "%PREFIX%\pkg\bin\PowerSynth2.py" "%PREFIX%\bin\"

echo "INFO: Creating executable and shortcuts"

for %%f in ("%PREFIX%\pkg\misc\win\PowerSynth2.exe" "%PREFIX%\pkg\misc\win\PowerSynth2*.lnk") do copy /y "%%f" "%PREFIX%\"

echo "INFO: Post installation completed."
timeout /t 2 /nobreak > NUL
exit /b 0

:ErrConda
echo "ERROR: %PREFIX% is not a Conda environment. Post installation failed."
timeout /t 10
exit /b 10

:ErrMatlab
echo "ERROR: Matlab is not found at %MatlabRoot%. Post installation failed."
timeout /t 10
exit /b 99
