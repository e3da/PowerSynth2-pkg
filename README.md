# PowerSynth 2 Release Series Top Repository
## Repository Overview
This is the pkg repository for PowerSynth 2. Refer to the [PowerSynth2-src](https://github.com/e3da/PowerSynth2-src) for latest source code. 
This repository contains additional data files, materials, test cases, and manuals used to prepare the release package. 

##PowerSynth 2 Installation Instructions
PowerSynth 2 can be run from source code directly. It is developed natively on Linux and then ported on to Windows. However, users need to configure environments and install all dependencies. For user convenience, we provide a self-contained pacakge on the release website to run it out-of-the-box.

PowerSynth 2 requires matlab to run ParaPower thermal model, the supported version is python 3.10 and matlab 2022b to use the provided package. 
See [MathWorks](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html) for details. 

For Windows:
Unpack the provided zip to C:\PowerSynth2.0. You will need to install matlab 2022b to its default location.
If the installed matlab version is different, you will need to right click pkg/misc/win/InstallMatlabEngine.ps1 and select 'run with PowerShell' to update the matlab engine. 

Three provided shortlinks are available to use. PowerSynth2-GUI starts the GUI version, PowerSynth-CLI starts the CLI version. PowerSynth2-INT starts the CLI interacive version to create a macro file. PowerSynth2-CLI starts the PowerShell for CLI version. 

A bundled PowerSynth2-CLI-Test2D5 shortcut automatically runs the Sample_Designs/2D_Case_5 for testing purpose. To change it to run a different macrofile, you can change the shortcut property.

For Linux:
Unpack the zip, and then set the path to include the bin folder. The main command is PowerSynth2.

If the installed matlab version is different, you need to use (the bundled) pip to install matlab engine:
pip install install matlabengine -t $PowerSynthRoot/lib/python3.10/site-packages/

For testing, a included bash script pkg/work/Sample_Designs/TestAll.sh will test all provided test cases. 

##PowerSynth 2 Usage Information
To start the GUI, use PowerSynth2 without any arguments. To use CLI, type PowerSynth2 followed by the macro script. If the file exists, it runs the macroscript, otherwise, it creates the macrofile interactively. 
Make sure the work folder (the folder contains the macroscript) is writable before running. 

The pkg/work folder contains a series of design examples. They are example designs from our published papers, which will be a good starting point to learn about PowerSynth.You can copy the provided pkg/work/Sample_Design folder and start playing around. 

# PowerSynth 2 Project Overview
PowerSynth 2 is stared as a resarch project to introduce the VLSI electronics design automation algorithms for power electronic applications. It is originally developed as an alternative layout engine for PowerSynth 1 to handle design constraints in complicated layouts. It is developed originally by the [E3DA Lab](https://e3da.csce.uark.edu/) as a POETS research project and then jointly by [MSCAD Lab](https://mscad.uark.edu/), at University of Arkansas. The PowerSynth 2 project is co-directed by [Prof. Yarui Peng](https://engineering.uark.edu/directory/index/uid/yrpeng/name/Yarui+Peng/) and [Prof. Alan Mantooth](https://engineering.uark.edu/directory/index/uid/mantooth/name/Alan+Mantooth/). The Powersynth 2 research project is mainly supported by NSF through POETS ERC, and ARL through a seires of grants. 

The main developers of this release series include Imam Al Razi, Quang Le, and Tristan Evans. The intial GUI is mainly developed by Joshua Mitchener as an REU project. The codebase also received contributions from many collaborators, graduates, and undergrads.

The main features, algorithms, and experiments of PowerSynth 2 are summarized in the following papers:

* v2.0: Imam Al Razi, Quang Le, Tristan Evans, H. Alan Mantooth, and Yarui Peng, ["PowerSynth 2: Physical Design Automation for High-Density 3D Multi-Chip Power Modules"](https://doi.org/10.1109/TPEL.2022.3227300), IEEE Transactions on Power Electronics, vol. 38, no. 4, pp. 4698-4713, April 2023.

Other papers describing the models, simulation, and optimization results include:

* Quang Le, Imam Al Razi, Tristan Evans, Shilpi Mukherjee, Yarui Peng, and H. Alan Mantooth, "Fast and Accurate Parasitic Extraction in Multichip Power Module Design Automation Considering Eddy-Current Losses", IEEE Journal of Emerging and Selected Topics in Power Electronics, 2023

* Imam Al Razi, Whit Vinson, David Huitink, and Yarui Peng, "Electromigration-Aware Reliability Optimization of MCPM Layouts Using PowerSynth", in Proc. IEEE Energy Conversion Congress and Exposition, pp. 1-8, Oct 2022.

PowerSynth 2 is still under active development. This design tool will be extended from power module to converter. For more details about the PowerSynth project and software download, please refer to the [PowerSynth Release Website](https://e3da.csce.uark.edu/release/PowerSynth/) with publications and presentations. PowerSynth 2 is still under active.  We welcome contributions and collaborations from communities by providing patches and reporting issues. If you find our research projects helpful, please attribute this work in your publications and presentations as appropriate in return for the free usage of the tool. 

