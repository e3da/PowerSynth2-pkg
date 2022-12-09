function Pout=ConvertToPPTCM(Pin)
%Converts from an old structure definition of PPTCM to the current object
%definition.
%
%P_object=ConvertToPPTCM(P_OldStructure)

Pout=PPTCM;
fFields=fields(Pout.Features(1));
Fields=fields(Pin);
for ThisField=reshape(Fields,1,[])
    ThisField=ThisField{1};
    disp(['Converting fieldname "' ThisField,'"...'])
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
