# PowerSynth 2 Release Series Package Repository
## Repository Overview
This is the pkg repository for PowerSynth 2. Refer to the [PowerSynth2-core](https://github.com/e3da/PowerSynth2-core) and other related repos for the latest source code. 
This repository contains additional data files, materials, pre-build models, test cases, and manuals used to prepare the release package. 

## PowerSynth 2 Installation Instructions
PowerSynth 2 can be run from the source code directly. It is developed natively on Linux and then ported onto Windows. However, users need to configure environments and install all dependencies. For user convenience, we provide a self-contained package on [PowerSynth Release Website](https://e3da.csce.uark.edu/release/PowerSynth/) to run it out-of-the-box.

PowerSynth 2 requires Matlab to run [ParaPower](https://github.com/USArmyResearchLab/ParaPower) thermal model. The supported version is Python 3.10 and Matlab 2022b to use our provided package. Other versions may work, provided the user follows the installation instructions. 
See [MathWorks](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html) for details. 

For Windows:
Unpack the provided tarball to C:\PowerSynth2.0\. You will need to install Matlab 2022b to its default location.
If the installed Matlab version is different, you will need to right-click pkg/misc/win/InstallMatlabEngine.ps1 and select 'run with PowerShell' to update the matlab engine. 

Three provided shortcuts are available to use. PowerSynth2-GUI starts the GUI version, PowerSynth2-CLI starts the PowerShell for CLI version. PowerSynth2-INT starts the CLI interactive version to create a macro file. 

A bundled PowerSynth2-CLI-Test2D5 shortcut automatically runs the Sample_Designs/2D_Case_5 for testing purposes. To change it to run a different macro script, you can change the shortcut property.

For Linux:
Unpack the provided tarball, and then set the path to include the bin folder. The main command is PowerSynth2.

For first time runing, or if the installed matlab version is different, you need to use (the bundled) pip to install Matlab engine:
pip install install matlabengine -t $PowerSynthRoot/lib/python3.10/site-packages/

For testing, a included bash script pkg/work/Sample_Designs/TestAll.sh will test all provided test cases. 

## PowerSynth 2 Usage Information
To start the GUI, use PowerSynth2 without any arguments. To use CLI, type PowerSynth2 followed by the macro script. If the file exists, it runs the macroscript, otherwise, it creates the macro script interactively. 
Make sure the work folder (the folder contains the macroscript) is writable before running. 

The pkg/work/Sample_Designs folder contains a series of design examples. They are example designs from our published papers, which will be a good starting point to learn about PowerSynth. You can copy the provided folder and start playing around. 

# PowerSynth 2 Project Overview
PowerSynth 2 started as a research project to introduce the VLSI electronics design automation algorithms for power electronic applications. It is developed originally by the [E3DA Lab](https://e3da.csce.uark.edu/) as a POETS project and then jointly by [MSCAD Lab](https://mscad.uark.edu/), at University of Arkansas. 

PowerSynth 2 was first developed as an enhanced layout engine for PowerSynth 1 to handle design constraints in complicated layouts with efficiency improvements. The new layout engine is first previewed in PowerSynth v1.3, and then became the sole engine in v1.9. In addition, new 3D layout algorithms, electrical/thermal models, and optimization algorithms are introduced in v2.0.

The PowerSynth 2 project is co-directed by [Prof. Yarui Peng](https://engineering.uark.edu/directory/index/uid/yrpeng/name/Yarui+Peng/) and [Prof. Alan Mantooth](https://engineering.uark.edu/directory/index/uid/mantooth/name/Alan+Mantooth/). The research project is mainly supported by NSF through POETS ERC, and ARL through a series of grants. 

The main developers of this release series include Imam Al Razi, Quang Le, and Tristan Evans. The initial GUI is mainly developed by Joshua Mitchener as an REU project. The codebase also received contributions from many collaborators, graduates, and undergrads.

The main features, algorithms, and experiments of PowerSynth 2 are summarized in the following papers:

* v2.0: Imam Al Razi, Quang Le, Tristan Evans, H. Alan Mantooth, and Yarui Peng, ["PowerSynth 2: Physical Design Automation for High-Density 3D Multi-Chip Power Modules"](https://doi.org/10.1109/TPEL.2022.3227300), IEEE Transactions on Power Electronics, vol. 38, no. 4, pp. 4698-4713, April 2023.

There are many other ongoing research projects to enhance its capabilities. But the feature may or may not be included in the release version yet. Several papers describing the models, simulation, and optimization results include:

* Imam Al Razi, Quang Le, H. Alan Mantooth, and Yarui Peng, "Hierarchical Layout Synthesis and Optimization Framework for High-Density Power Module Design Automation", in Proc. International Conference on Computer-Aided Design, pp. 1-8, Nov 2021.
* Quang Le, Imam Al Razi, Tristan Evans, Shilpi Mukherjee, Yarui Peng, and H. Alan Mantooth, "Fast and Accurate Parasitic Extraction in Multichip Power Module Design Automation Considering Eddy-Current Losses", IEEE Journal of Emerging and Selected Topics in Power Electronics, 2023
* Imam Al Razi, Whit Vinson, David Huitink, and Yarui Peng, "Electromigration-Aware Reliability Optimization of MCPM Layouts Using PowerSynth", in Proc. IEEE Energy Conversion Congress and Exposition, pp. 1-8, Oct 2022.

PowerSynth 2 is still under active development, and we are actively recruiting new students to join our team. Given the nature of the research, our priority is to explore new design methodologies and knowledge on Electronic Design Automation for Power Electronics. Our current work includes extending PowerSynth from power module to converter designs with reliability optimizations. For more details about the PowerSynth project and software download, please refer to the [PowerSynth Release Website](https://e3da.csce.uark.edu/release/PowerSynth/) with publications, demos, and presentations. 

We welcome contributions and collaborations from the community by providing patches and reporting issues. If you find our research projects helpful, please attribute this work in your publications and presentations as appropriate.
