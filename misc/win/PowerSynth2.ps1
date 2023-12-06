#To create exe through ps2exe:  for GUI only: -noConsole -noOutput 
#ps2exe pkg\misc\win\PowerSynth2.ps1 pkg\misc\win\PowerSynth2.exe -iconFile pkg\PowerSynth2.ico -title "PowerSynth2" -description "https://e3da.csce.uark.edu/release/PowerSynth"
param([switch] $help )	

if ($PSScriptRoot) {
	
	if ($help)
	{
		Write-Host -NoNewLine "Usage [Run from PSRoot]: .\python.exe pkg\bin\PowerSynth2.py"
		Write-Host " [macrofile: if not given, starts GUI, otherwise starts CLI. If the macrofile does not exist, creates it interactively.]"
		Exit
	}
	
	#change to PSRoot
	cd $PSScriptRoot\..\..\..
}

$PSRoot = (get-location).path
Write-Host "INFO: Starting PowerSynth2 from $PSRoot"

.\python.exe ".\pkg\bin\PowerSynth2.py" $args
