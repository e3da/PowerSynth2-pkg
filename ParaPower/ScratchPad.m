% Scratch Pad for input debugging
clear all
% Load JSON data from PowerSynth run
psjson = fileread('0_PowerSynth_MD_JSON.json');
psdata = jsondecode(psjson);

% Start adding things to make it work with FormModel
psdata.Version = 'V2.0';

matlib_old = load('PackMats_Update.mat');
% psdata.MatLib = matlib;
% psdata.MatList
% These don't work. Need to make material instances (PPMat and PPMatSolid)
% and add them to the PPMatLib then attach this to the model input class.

% This didn't quite work either...
% psdata.MatLib = matlib.MatLib;
% psdata.MatLib.MatList;

mlib = PPMatLib;

% Get selected items from old MatLib
mat_index = [1 2 3 4 8 9 15];
% Testing: cycle through materials in old lib and add them as new materials
% in the new PPMatLib strucure.
for i = 1:length(mat_index)
    % disp(matlib_old.MatLib.Material(mat_index(i)));
    ind = mat_index(i);
    name = matlib_old.MatLib.Material(ind);
    cte = matlib_old.MatLib.cte(ind);
    E = matlib_old.MatLib.e(ind);
    nu = matlib_old.MatLib.nu(ind);
    k = matlib_old.MatLib.k(ind);
    rho = matlib_old.MatLib.rho(ind);
    cp = matlib_old.MatLib.cp(ind);
    
    new_matl = PPMatSolid('cte', cte, 'E', E, 'nu', nu, 'k', k, 'rho', rho, 'cp', cp);
    % disp(name);
    new_matl.Name = char(name);
    mlib.AddMatl(new_matl);
   
end
% Append the new MatLib to the PS data.
psdata.MatLib = mlib;

% Run through the materials in the imported psdata and then change any NaNs
% to SiC... don't know why that's the case.
% Also changing the material names of the PS data for now to match the
% MatLib.

substrate_index = 0;
for i = 1:numel(psdata.Features)
    % Compare material names (to be removed later).
    psdata.Features(i).Matl = NameLookUp(psdata.Features(i).Matl);
    % Convert PowerSynth coordinate pairs from text to MATLAB doubles then
    % convert units from microns to meters.
    psdata.Features(i).x = List2Mat(psdata.Features(i).x)*1e-6;
    psdata.Features(i).y = List2Mat(psdata.Features(i).y)*1e-6;
    psdata.Features(i).z = List2Mat(psdata.Features(i).z)*1e-6;
    
    %Need the substrate to be named 'substrate' to use stres...
    %if strcmp(psdata.Features(i).name, 'Substrate_Isolation')
    %    substrate_index = i;
    %end
end    

% Now try to use FormModel
PSMI = FormModel(psdata);


% Try to run thermal analysis
% GlobalTime = 0:10:100;
GlobalTime = [0];
PSMI.GlobalTime = GlobalTime;
InitTime=[];
StepsToEstimate=0;
ComputeTime=[];
% InitTime = GlobalTime(1);
% ComputeTime = GlobalTime(2:end);
% StepsToEstimate = 2;

S1=scPPT('MI',PSMI); %Initialize object
setup(S1,[]);
tic
[Tprnt, T_in, MeltFrac,MeltFrac_in]=S1([InitTime ComputeTime(1:min(StepsToEstimate,length(ComputeTime)))]);  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
EstTime=toc;
disp('Max Temp: ');
disp(max(Tprnt(:)));

%PSMI.FeatureDescr(19) = {'substrate'};
% Try to put everything in the results object
Results(1)=PPResults(now, PSMI, 1,'Thermal');
Results(1)=Results(1).setState('Thermal',Tprnt);
% Good, but may need to set results better...

% Attempt to call stres function
% oops StressModel = dir('./Stress_Models/Stress_MinerV1.m');

% Rename the substrate feature
Results.Model.FeatureDescr(19) = {'substrate'};

addpath('./Stress_Models/');
stress_results = StressV1(Results(1));
Results(1)=Results(1).addState('Stress',stress_results);
Results.getState('Stress');

% MainPath=mfilename('fullpath');
% MainPath=strrep(MainPath,mfilename,'');
% set(StressModel,'userdata',[MainPath 'Stress_Models'])

%Populate Stress Models.  They exist in the directory and match "Stress_*.m"
% StressDir=get(handles.StressModel,'user');
% StressModels=dir([StressDir '/Stress*.m']);
% for Fi=1:length(StressModels)
%     StressModelFunctions{Fi}=StressModels.name;
%     StressModelFunctions{Fi}=strrep(StressModelFunctions{Fi},'.m','');
%     StressModelFunctions{Fi}=strrep(StressModelFunctions{Fi},'Stress_','');
%     AddStatusLine(['Adding stress model ' StressModelFunctions{Fi} '.'])
% end


% StressModel = 'MinerV1';
% addpath('./Stress_Models/');
% eval(['Stress=Stress_' StressModel '(Results(1));']);
% Results(1)=Results(1).addState('Stress',Stress);

function [parapower_name] = NameLookUp(ps_name)
%NAMELOOKUP Converts PowerSynth material names to those used in ParaPower.
%   This function is a temporary solution only until the material library
%   linking is completed.
if isempty(ps_name)
    ps_name = 'SiC';
end
ps_mats = {'copper', 'Pb-Sn Solder Alloy', 'MarkeTech AlN 160', 'SiC', 'Aluminum', 'Al_N'};
pp_mats = {'Cu', 'SAC405', 'AlN', 'SiC', 'Al', 'AlN'};
if any(strcmp(ps_mats, ps_name))
    mat_map = containers.Map(ps_mats, pp_mats);
    parapower_name = mat_map(ps_name);
else
    parapower_name = ps_name;
end
end

function [data_mat] = List2Mat(data_list)
%LIST2MAT Converts PowerSynth numerical lists to MATLAB double arrays.
%   PowerSynth sends over x, y, and z coordinate start and end locations of
%   features as a list of paired values as text. This function converts
%   them to MATLAB doubles compatible with ParaPower formatting.
data_mat = double([data_list(1) data_list(2)]);

end

