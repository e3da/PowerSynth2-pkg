clear all;

% jsonfiles = dir('./TestJSON/*.json');
jsonfiles = dir('./TestLayers/*.json');
results = zeros(2, length(jsonfiles));

for i = 1:length(jsonfiles)
%for i = 1:2
    file = jsonfiles(i);
    filename = strcat(file.folder, '\', file.name);
    Tres = PSPPThermal(filename);
    Sres = PSPPStress(filename);
    [t, temp] = get_global_max(Tres, 'Thermal');
    [t, stress] = get_global_max(Sres, 'Stress');
    temp = max(temp);
    stress = max(stress);
    results(1,i) = temp;
    results(2,i) = stress;
   
end

figure
scatter(results(1,:), results(2,:))
title('Simple Layout Analaysis Using ParaPower API')
xlabel('Max Temperature (^oC)')
ylabel('Max Abs(Pressure) (Pa)')

figure
stress_res = Sres.getState('Stress');
Visualize('Stress', Sres.Model, 'State', stress_res(:,:,:,end));