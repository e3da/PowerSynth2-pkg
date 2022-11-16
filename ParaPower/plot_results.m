function plot_results(Results)

MI=Results.Model;
if isfield(MI,'FeatureMatrix')
   TestCaseModel = Results.Case;

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
       % FeatureMat{end+1}=TestCaseModel.Features(Fi).Matl;
     
   end
   
   plot(DoutT(:,1),DoutT(:,2:end));
   xlabel('Time')
   ylabel('Temperature')
end