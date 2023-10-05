$mlvers=(matlab -help | findstr "Version" | % {$_ -replace '^.*Version: (\d+)\.(\d+).*','$1.$2.*'})

if (!$mlvers) {	
	Read-Host -Prompt "ERROR: No matlab installation found. Press any key to exit"
	exit
}

Write-Host "Installing Matlab v$mlvers"

& $PSScriptRoot\..\..\..\python.exe -m pip install "matlabengine==$mlvers"

if ($LastExitCode -eq 0) {
	Read-Host -Prompt "INFO: Installation Success. Press any key to exit"
} else {
	Read-Host -Prompt @"
ERROR: Installation Failed. Only Python 3.8+ and Matlab 2022b+ are supported. 
Refer to https://www.mathworks.com/support/requirements/python-compatibility.html
Press any key to exit
"@
}
