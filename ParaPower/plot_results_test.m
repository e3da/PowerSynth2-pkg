function plot_results_test(test_case_model, Results)

MI=Results.Model;
if isfield(MI,'FeatureMatrix')
   TestCaseModel = test_case_model;

   DoutT(:,1)=MI.GlobalTime;
   DoutM(:,1)=MI.GlobalTime;
   DoutS(:,1)=MI.GlobalTime;
   Ftext=[];
   FeatureMat=[];
   Fs=unique(MI.FeatureMatrix(~isnan(MI.FeatureMatrix)));
   Fs=Fs(Fs~=0);
   for Fi=1:length(Fs)

       Ftext{end+1}=MI.FeatureDescr{Fs(Fi)};
       Fmask=ismember(MI.FeatureMatrix,Fs(Fi));
       Fmask=repmat(Fmask,1,1,1,length(MI.GlobalTime));
       if ~isempty(Results.getState('thermal'))
            DoutT(:,end+1)=max(reshape(Results.getState('thermal',Fmask),[],length(MI.GlobalTime)),[],1);
       end
       if ~isempty(Results.getState('MeltFrac'))
            DoutM(:,end+1)=max(reshape(Results.getState('meltfrac',Fmask),[],length(MI.GlobalTime)),[],1);
       end
       if ~isempty(Results.getState('Stress'))
            DoutS(:,end+1)=max(reshape(Results.getState('stress',Fmask),[],length(MI.GlobalTime)),[],1);
       end
       FeatureMat{end+1}=TestCaseModel.Features(Fi).Matl;
     
   end
   PCMFeatures=[];
   for Fi=1:length(FeatureMat)
       if ~isempty(findstr(lower(MI.MatLib.GetMatName(FeatureMat{Fi}).Type),'pcm'))
           PCMFeatures=[PCMFeatures Fi];
       end
   end
   if isempty(PCMFeatures)
       DoutM=[];
   end
   NumAx=0;
   if size(DoutT,2)>1
       DoutT(:,1)=MI.GlobalTime;
       NumAx=NumAx+1;
   else
       DoutT=[];
   end
   if size(DoutM,2)>1
       DoutM(:,1)=MI.GlobalTime;
       NumAx=NumAx+1;
   else
       DoutM=[];
   end
   if size(DoutS,2)>1
       DoutS(:,1)=MI.GlobalTime;
       NumAx=NumAx+1;
   else
       DoutS=[];
   end
   MaxTitle='Max Results';
   Figs=findobj('type','figure');
   FigTitles=get(Figs,'name');
   MaxResultsFig=find(strcmpi(FigTitles,MaxTitle));
   ThisAx=NumAx;
   if isempty(MaxResultsFig)
       set(figure,'name',MaxTitle')
   else
       figure(Figs(MaxResultsFig))
   end
   clf

    VarPlotTitle='';
    % if ~isempty(Results.Case.ParamVar)
    if ~isempty(TestCaseModel.ParamVar)
        for II=1:length(Results.Case.ParamVar(:,1))
            VarPlotTitle=[VarPlotTitle sprintf('%s: %s\n',Results.Case.ParamVar{II,1},Results.Case.ParamVar{II,2})];
        end
        VarPlotTitle=sprintf('\nCase %g: %s\n',ThisCase,VarPlotTitle);
    end
    if ~isempty(DoutT)
       subplot(1,NumAx,ThisAx)
       plot(DoutT(:,1),DoutT(:,2:end));
       xlabel('Time')
       ylabel('Temperature')
       T=('Max Temp in Feature');
       PlotTitle=[T VarPlotTitle];
       title(PlotTitle,'interp','none');
       legend(Ftext)
       ThisAx=ThisAx-1;
   end
   if ~isempty(DoutM)
       subplot(1,NumAx,ThisAx)
       plot(DoutM(:,1),DoutM(:,PCMFeatures+1));
       legend(Ftext(PCMFeatures))
       xlabel('Time')
       ylabel('Melt Fraction')
       T=('Max Melt Fraction in Feature');
       PlotTitle=[T VarPlotTitle];
       title(PlotTitle,'interp','none');
       ThisAx=ThisAx-1;
   end
   if ~isempty(DoutS)
       subplot(1,NumAx,ThisAx)
       plot(DoutS(:,1),DoutS(:,2:end));
       xlabel('Time')
       ylabel('Stress')
       T=('Max Stress in Feature');
       PlotTitle=[T VarPlotTitle];
       title(PlotTitle,'interp','none');
       legend(Ftext)
       ThisAx=ThisAx-1;
   end
else
   Dout(:,1)=MI.GlobalTime;
   scan_mats = find(strcmp(MI.MatLib.Type,'PCM'));  %Select only PCM materials
   scan_mask=ismember(MI.Model,scan_mats);
   scan_mask=repmat(scan_mask,1,1,1,length(MI.GlobalTime));
   Dout(:,2)=max(reshape(Results.getState('Thermal'),[],length(MI.GlobalTime)),[],1);
   %Dout(:,3)=max(Results.Stress,[],[1 2 3]);
   Dout(:,4)=max(reshape(Results.getState('MeltFrac',scan_mask),[],length(MI.GlobalTime)),[],1);


   numplots = 1;
   figure(numplots)
   if isempty(scan_mats)
       SP=1;
   else
       SP=2;
   end
   subplot(1,SP,1)
   plot (Dout(:,1), Dout(:,2))
   xlabel('Time (s)')
   ylabel('Temperature')
   title('Max Temperature Across All Model')
   if SP==2
       subplot(1,SP,2)
       plot (Dout(:,1), Dout(:,4))
       xlabel('Time (s)')
       ylabel('Melt Fraction')
       title('Max Melt Fraction All PCM Materials')
   end
end
