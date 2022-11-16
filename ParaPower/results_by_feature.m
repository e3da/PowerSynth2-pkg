function [time, results] = results_by_feature(ResultsObject, feature_name, result_type)
%results_by_feature Looks up results for a given feature name from a
%PPResults Object
%   Detailed explanation goes here

if ~strcmp(result_type, 'Thermal') & ~strcmp(result_type, 'Stress')
    error = 'Result type must be specified as either "Thermal" or "Stress"';
    disp(error);
    time = 0;
    results = 0;
    return
end

FeatureDescr = ResultsObject.Model.FeatureDescr;
time = ResultsObject.Model.GlobalTime;
ind = 0;

% Match feature_name to the list and return the indexing value.
for i = 1:length(FeatureDescr)
    current_item = FeatureDescr(i);
    current_name = current_item{1};
    if strcmp(feature_name, current_name)
        ind = i;
    end
end

% Find the 3D matrix slice containing the feature
feat_ind = find(ResultsObject.Model.FeatureMatrix == ind);

temporary_results = zeros(1,length(time));

results_data = ResultsObject.getState(result_type);

for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
    temporary_results(j) = max(results_data_slice(feat_ind));
end
results = temporary_results;
end

