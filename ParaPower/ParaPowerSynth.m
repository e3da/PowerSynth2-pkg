function results = ParaPowerSynth(jsondata,varargin)
%Imports a PowerSynth-generated layout/design and converts it to a
%ParaPower one while performing a specified analysis and returning the
%results.
%   This function imports a layout from PowerSynth and converts it to a
%   ParaPower one before executing the specified analysis and returning the
%   specified results. The first input argument is the JSON data sent from
%   PowerSynth while the remaining arguments specify analysis function,
%   type, and results format as described below:
%   
%   INPUTS:
%   jsondata: PowerSynth-generated layout in JSON format.
%   varargin{1}: Analysis function to be used, either 'thermal,' 'stress,' or 'coupled.'
%   varargin{2}: Analysis type, either 'static,' or 'transient.'
%   varargin{3}: Results type, either 'global' or 'individual.'
%   
%   NOTES:
%   When selecting 'stress,' stress analysis is performed between the
%   process temperature and the user-defined minimum temperature without 
%   considering device heating.'Coupled,' on the other hand, uses the power
%   dissipation specified to calculate a temperature difference between the
%   process temperature and the current layout temperature to calculate
%   stress.
%
%   Selecting 'global' will simply return the maximum temperature of the
%   system. Chosing 'individual' will return a struct/dict in JSON format
%   of the maximum temperature of each individual feature in the model.
%
%   RETURN:
%   results: a JSON file holding the struct/dict of all results

psdata = jsondecode(jsondata);

% Start adding items to make it work with FormModel
psdata.Version = 'V2.0';

% Use and old version of a MatLib to help populate a new one.
matlib_old = load('PackMats_Update.mat');

% Make a new PPMatLib instance
mlib = PPMatLib;

% Get selected items from old MatLib as they apply to the current import
% data.
mat_index = [1 2 3 4 8 9 15];
for i = 1:length(mat_index)
% Testing: cycle through materials in old lib and add them as new materials
% in the new PPMatLib strucure.
    ind = mat_index(i);
    name = matlib_old.MatLib.Material(ind);
    cte = matlib_old.MatLib.cte(ind);
    E = matlib_old.MatLib.e(ind);
    nu = matlib_old.MatLib.nu(ind);
    k = matlib_old.MatLib.k(ind);
    rho = matlib_old.MatLib.rho(ind);
    cp = matlib_old.MatLib.cp(ind);
    %disp(char(name));
    if strcmpi(char(name),'AIR')
        k=0.024;
    
    end
    if strcmpi(char(name),'SAC405')
        k=13.9;
    
    end
    new_matl = PPMatSolid('cte', cte, 'E', E, 'nu', nu, 'k', k, 'rho', rho, 'cp', cp);

    new_matl.Name = char(name);
    %disp(new_matl.Name);
    %disp(k);
    mlib.AddMatl(new_matl);
   
end
new_matl = PPMatPCM('cte', 2, 'E', 1, 'nu', 4, 'k', 7, 'rho', 4, 'cp', 4);
new_matl.Name = char("Test Material");
mlib.AddMatl(new_matl);
% Append the new MatLib to the PowerSynth data.
psdata.MatLib = mlib;


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
%     if strcmp(psdata.Features(i).name, 'Substrate_Isolation')
%        substrate_index = i;
%     end
end

% Reverse order of features so that baseplate is first 'layer' for stress
% model
%psdata.Features = flip(psdata.Features);
psdata.Features(1).name = char('substrate');

% Use Morris's function to convert structure data to PPTCM
psdata_converted = ConvertToPPTCM(psdata);


% Now try to use FormModel
PSMI = FormModel(psdata_converted);

%%%%%%%%%%%%%%%%%%%%%%%%%%
%SELECT ANALYSIS TYPE
%%%%%%%%%%%%%%%%%%%%%%%%%%

if strcmpi(varargin{1}, 'thermal')
    if strcmpi(varargin{2}, 'static')
        resobj = thermal_static(PSMI);
    elseif strcmpi(varargin{2}, 'transient')
        resobj = thermal_transient(PSMI);
    else
        error = 'Unknown function or type';
        disp(error);
    end
elseif strcmpi(varargin{1}, 'stress')
    resobj = stress_static_predefined(PSMI);
else
    error = 'Unknown function or type';
    disp(error);

end % end analysis 

resobj.Model.FeatureDescr = PSMI.FeatureDescr;
resobj.Model.FeatureMatrix = PSMI.FeatureMatrix;
%%%%%%%%%%%%%%%%%%%%%%%%%%
%RESULTS PREPARATION
%%%%%%%%%%%%%%%%%%%%%%%%%%


res_struct = struct('feature', {}, 'time', {}, 'temperature', {}, 'stress', {});
if strcmpi(varargin{3}, 'global') & strcmpi(varargin{1}, 'thermal')
    [time, res] = get_global_max(resobj, 'Thermal');
    % disp(res)
    res_struct(1).feature = 'global';
    res_struct(1).time = time;
    res_struct(1).temperature = res;
    
elseif strcmpi(varargin{3}, 'individual') & strcmpi(varargin{1}, 'thermal')
    for i=1:length(PSMI.FeatureDescr)
        [time, res] = get_max_by_feature(resobj, PSMI.FeatureDescr{i}, 'thermal');
        res_struct(i).feature = PSMI.FeatureDescr{i};
        res_struct(i).time = time;
        res_struct(i).temperature = res;
    end
    
elseif strcmpi(varargin{3}, 'global') & strcmpi(varargin{1}, 'stress')
    [time, res] = get_global_max(resobj, 'Stress');
    % disp(res)
    res_struct(1).feature = 'global';
    res_struct(1).time = time;
    res_struct(1).stress = res;
else
    error = 'Unknown function or type';
    disp(error);
    
end % end results preparation

%   results = res_struct; %debug
results = jsonencode(res_struct);

end % end function

function [parapower_name] = NameLookUp(ps_name)
%NAMELOOKUP Converts PowerSynth material names to those used in ParaPower.
%   This function is a temporary solution only until the material library
%   linking is completed.
if isempty(ps_name)
    ps_name = 'SiC';
end
ps_mats = {'copper', 'Pb-Sn Solder Alloy', 'MarkeTech AlN 160', 'SiC', 'Aluminum', 'Al_N', 'Copper', 'Air'};
pp_mats = {'Cu', 'SAC405', 'AlN', 'SiC', 'Al', 'AlN', 'Cu', 'AIR'};
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

function [Pout]=ConvertToPPTCM(Pin)
%Converts from an old structure definition of PPTCM to the current object
%definition.
%
%P_object=ConvertToPPTCM(P_OldStructure)

Pout=PPTCM;
fFields=fields(Pout.Features(1));
Fields=fields(Pin);
for ThisField=reshape(Fields,1,[])
    ThisField=ThisField{1};

    %disp(['Converting fieldname "' ThisField,'"...'])

    if strcmpi(ThisField,'Features')
        for Fi=1:length(Pin.Features)
            ThisFeature=Pin.Features(Fi);
            for ThisfField=reshape(fFields,1,[])
                ThisfField=ThisfField{1};
                if strcmpi(ThisfField,'Desc')
                    Oldfield='name';
                else
                    Oldfield=ThisfField;
                end
                Pout.Features(Fi).(ThisfField)=Pin.Features(Fi).(Oldfield);
            end
        end
        
    elseif strcmpi(ThisField,'ExternalConditions')
        Pout.ExternalConditions.h_Xminus=Pin.ExternalConditions.h_Left;
        Pout.ExternalConditions.h_Xplus=Pin.ExternalConditions.h_Right;
        Pout.ExternalConditions.h_Yplus=Pin.ExternalConditions.h_Front;
        Pout.ExternalConditions.h_Yminus=Pin.ExternalConditions.h_Back;
        Pout.ExternalConditions.h_Zplus=Pin.ExternalConditions.h_Top;
        Pout.ExternalConditions.h_Zminus=Pin.ExternalConditions.h_Bottom;
    
        Pout.ExternalConditions.Ta_Xminus=Pin.ExternalConditions.Ta_Left;
        Pout.ExternalConditions.Ta_Xplus=Pin.ExternalConditions.Ta_Right;
        Pout.ExternalConditions.Ta_Yplus=Pin.ExternalConditions.Ta_Front;
        Pout.ExternalConditions.Ta_Yminus=Pin.ExternalConditions.Ta_Back;
        Pout.ExternalConditions.Ta_Zplus=Pin.ExternalConditions.Ta_Top;
        Pout.ExternalConditions.Ta_Zminus=Pin.ExternalConditions.Ta_Bottom;
        
        Pout.ExternalConditions.Tproc=Pin.ExternalConditions.Tproc;
    elseif strcmpi(ThisField,'Version')
    else
        Pout.(ThisField)=Pin.(ThisField);
    end
end
end

function [time, results] = get_global_max(ResultsObject,result_type)
%get_global_max Returns the global maximum value for the results type
%specified given a PPResults object.
%   Detailed explanation goes here

if ~strcmpi(result_type, 'thermal') & ~strcmpi(result_type, 'stress')
    error = 'Result type must be specified as either "thermal" or "stress"';
    disp(error);
    time = 0;
    results = 0;
    return
end

time = ResultsObject.Model.GlobalTime;
if isempty(time)
    time = [0 0];
end

temporary_results = zeros(1,length(time));

results_data = ResultsObject.getState(result_type);

    
for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
    if strcmpi(result_type, 'thermal')
        temporary_results(j) = max(results_data_slice, [], 'all');
    else
        %delta = max(results_data_slice, [], 'all') - min(results_data_slice, [], 'all');
        %temporary_results(j) = delta;
        temporary_results(j) = max(abs(results_data_slice), [], 'all');
    end
end
results = temporary_results;

end

function [time, results] = get_max_by_feature(ResultsObject, feature_name, result_type)
%results_by_feature Looks up results for a given feature name from a
%PPResults Object
%   Detailed explanation goes here

if ~strcmpi(result_type, 'thermal') & ~strcmpi(result_type, 'stress')
    error = 'Result type must be specified as either "thermal" or "stress"';
    disp(error);
    time = 0;
    results = 0;
    return
end

FeatureDescr = ResultsObject.Model.FeatureDescr;
time = ResultsObject.Model.GlobalTime;
if isempty(time)
    time = [0 0];
end
ind = 0;

% Match feature_name to the list and return the indexing value.
for i = 1:length(FeatureDescr)
    current_item = FeatureDescr(i);
    current_name = current_item{1};
    if strcmp(feature_name, current_name)
        ind = i;
        %disp(find(ResultsObject.Model.FeatureMatrix == ind));
        %disp(feature_name);
        
    
    
    end
end

% Find the 3D matrix slice containing the feature
feat_ind = find(ResultsObject.Model.FeatureMatrix == ind);

temporary_results = zeros(1,length(time));

results_data = ResultsObject.getState(result_type);

for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
    
	%disp(size(max(results_data_slice(feat_ind))));
	%disp(size(temporary_results(j)));
    %try
	temporary_results(j) = max(results_data_slice(feat_ind));
    %catch
		%continue
    %end    
    
end
results = temporary_results;
end

function resobj = thermal_static(model)

InitTime=[];
StepsToEstimate=0;
ComputeTime=[];

S1=scPPT('MI',model); %Initialize object
setup(S1,[]);
tic
[Tprnt, T_in, MeltFrac,MeltFrac_in]=S1([InitTime ComputeTime(1:min(StepsToEstimate,length(ComputeTime)))]);  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)


if length(ComputeTime)>StepsToEstimate
    [Tprnt2, T_in2, MeltFrac2,MeltFrac_in2]=S1(ComputeTime(3:end));  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
    Tprnt   =cat(4, T_in        , Tprnt   ,  Tprnt2   );
    MeltFrac=cat(4, MeltFrac_in , MeltFrac,  MeltFrac2);
else
    Tprnt=cat(4,T_in,Tprnt);
    MeltFrac=cat(4,MeltFrac_in,MeltFrac);
end

PSMI.GlobalTime = [InitTime ComputeTime]; %Reassemble PSMI's global time to match initialization and computed states.

Results(1)=PPResults(now, PSMI, 1,'Thermal','MeltFrac');
Results(1)=Results(1).setState('Thermal',Tprnt);
Results(1)=Results(1).setState('MeltFrac',MeltFrac);
resobj = Results;

end

function resobj = thermal_transient(model)
GlobalTime = 0:10:100;
% GlobalTime = [0];
model.GlobalTime = GlobalTime;
% InitTime=[];
StepsToEstimate=0;
ComputeTime=[];
InitTime = GlobalTime(1);
ComputeTime = GlobalTime(2:end);
StepsToEstimate = 2;

InitTime=model.GlobalTime(1);    %Time at initializatio extracted from PSMI.GlobalTime
ComputeTime=model.GlobalTime(2:end); %extract time to compute states from PSMI.GlobalTime
model.GlobalTime=InitTime;  %Setup initialization
StepsToEstimate=2;

S1=scPPT('MI',model); %Initialize object
setup(S1,[]);
tic
[Tprnt, T_in, MeltFrac,MeltFrac_in]=S1([InitTime ComputeTime(1:min(StepsToEstimate,length(ComputeTime)))]);  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
EstTime=toc;

if length(ComputeTime)>StepsToEstimate
    [Tprnt2, T_in2, MeltFrac2,MeltFrac_in2]=S1(ComputeTime(3:end));  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
    Tprnt   =cat(4, T_in        , Tprnt   ,  Tprnt2   );
    MeltFrac=cat(4, MeltFrac_in , MeltFrac,  MeltFrac2);
else
    Tprnt=cat(4,T_in,Tprnt);
    MeltFrac=cat(4,MeltFrac_in,MeltFrac);
end

PSMI.GlobalTime = [InitTime ComputeTime]; %Reassemble PSMI's global time to match initialization and computed states.

Etime=toc;

Results(1)=PPResults(now, PSMI, 1,'Thermal','MeltFrac');
Results(1)=Results(1).setState('Thermal',Tprnt);
Results(1)=Results(1).setState('MeltFrac',MeltFrac);
resobj = Results;
end

function resobj = stress_static_predefined(model)
model.Ta = [-40 -40 -40 -40 -40 -40];
model.h = [100 100 100 100 100 100];

GlobalTime = 0:100:100;
% GlobalTime = [];
model.GlobalTime = GlobalTime;
% InitTime=[];
% StepsToEstimate=0;
% ComputeTime=[];
% InitTime = GlobalTime(1);
% ComputeTime = GlobalTime(2:end);
% StepsToEstimate = 2;


if ~isempty(model.GlobalTime)
    InitTime=model.GlobalTime(1);    %Time at initializatio extracted from PSMI.GlobalTime
    ComputeTime=model.GlobalTime(2:end); %extract time to compute states from PSMI.GlobalTime

    model.GlobalTime=InitTime;  %Setup initialization
    StepsToEstimate=2;
else
    InitTime=[];
    StepsToEstimate=0;
    ComputeTime=[];
end
S1=scPPT('MI',model); %Initialize object
setup(S1,[]);
tic
[Tprnt, T_in, MeltFrac,MeltFrac_in]=S1([InitTime ComputeTime(1:min(StepsToEstimate,length(ComputeTime)))]);  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
EstTime=toc;

if length(ComputeTime)>StepsToEstimate
    [Tprnt2, T_in2, MeltFrac2,MeltFrac_in2]=S1(ComputeTime(3:end));  %Compute states at times in ComputeTime (S1 must be called with 1 arg in 2017b)
    Tprnt   =cat(4, T_in        , Tprnt   ,  Tprnt2   );
    MeltFrac=cat(4, MeltFrac_in , MeltFrac,  MeltFrac2);
else
    Tprnt=cat(4,T_in,Tprnt);
    MeltFrac=cat(4,MeltFrac_in,MeltFrac);
end

model.GlobalTime = [InitTime ComputeTime]; %Reassemble PSMI's global time to match initialization and computed states.

Etime=toc;

S_Results(1)=PPResults(now, model, 1,'Thermal','MeltFrac');
S_Results(1)=S_Results(1).setState('Thermal',Tprnt);
S_Results(1)=S_Results(1).setState('MeltFrac',MeltFrac);

%Results.Model.FeatureDescr(1) = {'substrate'};
addpath('./Stress_Models/');
stress_results = StressV1(S_Results(1));
S_Results(1)=S_Results(1).addState('Stress',stress_results);
S_Results.getState('Stress');

resobj = S_Results;
end
