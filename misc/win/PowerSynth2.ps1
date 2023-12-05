#To create exe through ps2exe:
#ps2exe H:\git\PowerSynth\pkg\misc\win\PowerSynth2.ps1 H:\git\PowerSynth\pkg\misc\win\PowerSynth2.exe -iconFile H:\git\PowerSynth\pkg\PowerSynth2.ico -title "PowerSynth2" -description "https://e3da.csce.uark.edu/release/PowerSynth"

Write-Host -NoNewLine "Usage: "

if ($PSScriptRoot) {
	#running as script
	cd $PSScriptRoot\..\..\..\
	Write-Host -NoNewLine "python.exe pkg\bin\PowerSynth2.py" 
} else {
	#running as exe
	Write-Host -NoNewLine "PowerSynth2.exe"
}

Write-Host " [macrofile: if not given, starts GUI, otherwise starts CLI. If the macrofile does not exist, creates it interactively.]"

$CurrentDirectory = (get-location).path
Write-Host "INFO: Starting PowerSynth2 from $CurrentDirectory"

.\python.exe ".\pkg\bin\PowerSynth2.py" $args

if (! $?) { 
	Write-Host "Press anykey to continue" -ForegroundColor Yellow
    $host.ui.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

