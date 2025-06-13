# PowerSynth 2 Release Series Package Repository
## Repository Overview
This is the pkg repository for PowerSynth 2. Refer to the [PowerSynth2-core](https://github.com/e3da/PowerSynth2-core) and other related repos for the latest source code. 
This repository contains additional data files, materials, pre-build models, test cases, and manuals used to prepare the release package. 

## PowerSynth 2 Installation Instructions
This instruction is for the latest version of PowerSynth. For older versions, please refer to the README.md in the provided package. 

PowerSynth 2 can be run from the source code directly. It is developed natively on Linux and then ported onto Windows. However, users need to configure environments and install all dependencies. For user convenience, we provide a release package on [PowerSynth Release Website](https://e3da.csce.uark.edu/release/PowerSynth/) to run it out-of-the-box. 

Starting from v2.1, the package bundles local and online installers. The provided package will install python and several basic packages. Then a post-install script will automatically run and git-clone the source code from github and pip-install non-anaconda packages from pypi. This requires you to have Internet connection to github and pypi during installation. Otherwise, you will manually need to download these packages or run the post-install script yourself. See pkg/misc/constructor/post_install scripts for details. 

PowerSynth 2 requires Matlab to run [ParaPower](https://github.com/USArmyResearchLab/ParaPower) thermal model. The package uses Python3.10 and assumes Matlab 2022b or higher is installed at the default location. For non-default matlab install location, you need to manually download the install matlabengine using the bundled pip, and edit the site-packages/matlab/engine/_arch.txt file within Lib or lib/python3.10 folder after installation. 
See [MathWorks](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html) for details about compatibility. 

The following commands assume you are running under the PowerSynth2 installation folder. 

### For Windows:
Unless you know what you are doing, we suggest keeping all options unchanged for Windows installer and install for yourself. In addition, if you install PowerSynth for every user, it will require admin privilege to write to the installation folder. 
Note, if the Matlab engine python module install failed during post-install, right-click pkg/misc/win/InstallMatlabEngine.ps1 and select 'run with PowerShell' to update the matlab engine. 

After installation, the PowerSynth.exe will run the GUI version as an application. In addition, PowerShell can be started to run PowerSynth2-CLI. Another PowerSynth2-GUI shortcut is provided in case you want to run GUI within PowerShell. The PowerSynth2-NewMacro starts the CLI interactive version to create a macro file based on a template. The CLI mode is more robust and flexible and is recommended for advanced users. 

### For Linux:
Run the provided executable shell script.
Note, in case matlabengine installation fails, follow instructions from MathWorks, then reinstall the required matlabengine using bundled pip. 
```
bin/pip install matlabengine --upgrade -t PowerSynth2/lib/python3.10/site-packages/
```
To run PowerSynth, set the path to include the bin folder:
```
export PATH=`realpath bin`:$PATH
PowerSynth2
```
If you want to perform automatic tests on all provided cases (takes time):
```
pkg/work/Sample_Designs/TestAll.sh
```

## PowerSynth 2 In-place Upgrade and Development
The source code is cloned git repositories under lib/{python3.*}/site-packages/{core,gui}/ and other necessary files are located under pkg/. You can use git clone to perform an in-place upgrade. An automatic script pkg/misc/utils/PullFromGithub.sh can run in git bash to sync code with its origin on github. Therefore, you can easily contribute to the PowerSynth 2 source code by submitting a pull request. 

By default, all code tracks the main branch; however, the latest development may occur on other (public or internal) branches. Candidates for the next release will be applied first to the dev branch before being merged into main as the next stable release. For a brief changelog, refer to the release website. 

## PowerSynth 2 Usage Information
The installation folder is a self-contained conda python environment with essential packages to run PowerSynth.

To start the GUI, use PowerSynth2 command without any arguments. To use CLI, type PowerSynth2 followed by the macro script. If the file exists, it runs the macroscript, otherwise, it creates the macro script interactively. 
Make sure the work folder (the folder contains the macroscript) is writable before running. 

The pkg/work/Sample_Designs folder contains a series of design examples. They are example designs from our published papers, which will be a good starting point to learn about PowerSynth. You can copy the provided folder and start playing around. 
The pkg/man folder contains a manual at the time of release. However, it will be constantly revised and published on the release website. 


# PowerSynth 2 Project Overview
PowerSynth 2 started as a research project to introduce the VLSI electronics design automation algorithms for power electronic applications. It is developed originally by the [E3DA Lab](https://e3da.csce.uark.edu/) as a POETS project and then jointly by [MSCAD Lab](https://mscad.uark.edu/), at University of Arkansas. 

PowerSynth 2 was first developed as an enhanced layout engine for PowerSynth 1 to handle design constraints in complicated layouts with efficiency improvements. The new layout engine is first previewed in PowerSynth v1.3, and then became the sole engine in v1.9. In addition, new 3D layout algorithms, electrical/thermal models are introduced in v2.0, with improved optimization algorithms introduced in v2.1, and custom devices and power converter design support in v2.2.

The PowerSynth 2 project is co-directed by [Prof. Yarui Peng](https://engineering.uark.edu/directory/index/uid/yrpeng/name/Yarui+Peng/) and [Prof. Alan Mantooth](https://engineering.uark.edu/directory/index/uid/mantooth/name/Alan+Mantooth/). The research project is mainly supported by NSF through POETS ERC, ARL, and ARPA-E through a series of grants. 

The main developers of this release series include Mehran Sanjabiasasi, Imam Al Razi, Quang Le, and Tristan Evans. The initial GUI is mainly developed by Joshua Mitchener as an REU project. The codebase also received contributions from many collaborators, graduates, and undergrads.

The main features, algorithms, and experiments of PowerSynth 2 are summarized in the following papers:

* v2.0: Imam Al Razi, Quang Le, Tristan Evans, H. Alan Mantooth, and Yarui Peng, ["PowerSynth 2: Physical Design Automation for High-Density 3D Multi-Chip Power Modules"](https://doi.org/10.1109/TPEL.2022.3227300), IEEE Transactions on Power Electronics, vol. 38, no. 4, pp. 4698-4713, April 2023.
* v2.1: Mehran Sanjabiasasi, Imam Al Razi, H. Alan Mantooth, and Yarui Peng, ["A Comparative Study on Optimization Algorithms in PowerSynth 2"](https://e3da.csce.uark.edu/pub/doc/2023/M.Sanjabiasasi-Misc.Conf.DMC-2023.pdf), in Proc. IEEE Design Methodologies Conference, Sep 2023.
* v2.2: Mehran Sanjabiasasi, H. Alan Mantooth, and Yarui Peng, ["PowerSynth 2: Automated Power Electronics Physical Design Synthesis With Custom and Heterogeneous Components"](https://e3da.csce.uark.edu/pub/doc/2025/M.Sanjabiasasi-IEEE.OJPEL-2025.pdf), IEEE Open Journal of Power Electronics, vol. 6, pp. 899-908, 2025.

We welcome contributions and collaborations from the community by providing patches and reporting issues. If you find our research projects helpful, please attribute this work in your publications and presentations as appropriate.

## On-going Research
There are many other on-going research projects to enhance its capabilities to include reliability, cost analysis, and AI integration. We are currently working on extending PowerSynth applications beyond power modules to include power converters, data center servers, and other related devices. But the feature may or may not be included in the release version yet. Several papers describing the models, simulation, and optimization results include:

* Imam Al Razi, Quang Le, H. Alan Mantooth, and Yarui Peng, "Hierarchical Layout Synthesis and Optimization Framework for High-Density Power Module Design Automation", in Proc. International Conference on Computer-Aided Design, pp. 1-8, Nov 2021.
* Quang Le, Imam Al Razi, Tristan Evans, Shilpi Mukherjee, Yarui Peng, and H. Alan Mantooth, "Fast and Accurate Parasitic Extraction in Multichip Power Module Design Automation Considering Eddy-Current Losses", IEEE Journal of Emerging and Selected Topics in Power Electronics, 2023
* Imam Al Razi, Whit Vinson, David Huitink, and Yarui Peng, "Electromigration-Aware Reliability Optimization of MCPM Layouts Using PowerSynth", in Proc. IEEE Energy Conversion Congress and Exposition, pp. 1-8, Oct 2022.
* Tristan Evans, Yarui Peng, and H. Alan Mantooth, "VLSI-Inspired Design Automation for Scalable Power Electronics Layout Optimization", in Proc. IEEE Design Methodologies Conference, Sep 2023.

PowerSynth 2 is still under active development, and we are actively recruiting new students to join our team. Given the nature of the research, our priority is to explore new design methodologies and knowledge on Electronic Design Automation for Power Electronics. For more details about the PowerSynth project and software download, please refer to the [PowerSynth Release Website](https://e3da.csce.uark.edu/release/PowerSynth/) with publications, demos, and presentations.
