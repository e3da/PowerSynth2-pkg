function [time, results] = get_global_max(ResultsObject,result_type)
%get_global_max Returns the global maximum value for the results type
%specified given a PPResults object.
%   Detailed explanation goes here

if ~strcmp(result_type, 'Thermal') & ~strcmp(result_type, 'Stress')
    error = 'Result type must be specified as either "Thermal" or "Stress"';
    disp(error);
    time = 0;
    results = 0;
    return
end

time = ResultsObject.Model.GlobalTime;

temporary_results = zeros(1,length(time));

results_data = ResultsObject.getState(result_type);

    
for j = 1:length(time)
    results_data_slice = results_data(:,:,:,j);
    if strcmp(result_type, 'Thermal')
        temporary_results(j) = max(results_data_slice, [], 'all');
    else
        %delta = max(results_data_slice, [], 'all') - min(results_data_slice, [], 'all');
        %temporary_results(j) = delta;
        temporary_results(j) = max(abs(results_data_slice), [], 'all');
    end
end
results = temporary_results;

end

