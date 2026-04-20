# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

from PPMatNull import PPMatNull
import numpy as np

def ComputeVA(DCoord):
    Lx = len(DCoord["X"])
    Ly = len(DCoord["Y"])
    Lz = len(DCoord["Z"])

    DCoord["X"] = DCoord["X"][np.newaxis, :]
    DCoord["Y"] = DCoord["Y"][np.newaxis, :]
    DCoord["Z"] = DCoord["Z"][np.newaxis, :]

    VA = np.reshape(np.dot(DCoord["X"].T, DCoord["Y"]).reshape(-1, 1) * DCoord["Z"], (Lx, Ly, -1))

    Xz = (DCoord["X"] == 0)
    Yz = (DCoord["Y"] == 0)
    Zz = (DCoord["Z"] == 0)

    Az = (DCoord["X"].T @ DCoord["Y"]).reshape(-1, 1) * Zz
    Az = Az.reshape(Lx, Ly, -1)

    Ay = (DCoord["X"].T @ Yz).reshape(-1, 1) * DCoord["Z"]
    Ay = Ay.reshape(Lx, Ly, -1)

    Ax = (Xz.T @ DCoord["Y"]).reshape(-1, 1) * DCoord["Z"]
    Ax = Ax.reshape(Lx, Ly, -1)

    VA = VA + (Ax+Ay+Az) * 1j

    return VA

def GetZeroLayer(Coords, FeatureCoords):
    ZeroLayer = np.where(Coords == FeatureCoords[0])[0]
    
    if ZeroLayer.size == 0:  # Check if ZeroLayer is empty
        ZeroLayer = np.where(np.abs(Coords - FeatureCoords[0]) < np.finfo(float).eps)[0]
    
    if ZeroLayer.size > 0:  # Check if ZeroLayer has any valid indices
        ZeroLayer = ZeroLayer[0]  # Get the first valid index
        if ZeroLayer == 0:  # Adjusting for zero-based index in Python
            UseLayer = 1  # UseLayer should be 2 in MATLAB, but we need to adjust
        else:
            UseLayer = ZeroLayer  # UseLayer is ZeroLayer - 1 in Python
            UseLayer -= 1
    else:
        UseLayer = None  # Handle case where no valid layer is found
    
    return UseLayer


def ismembertol(A, B, tol):
    # Combine A and B to find the maximum absolute value
    max_abs_value = np.max(np.abs(np.concatenate((A, B))))
    
    # Scale the tolerance based on the maximum absolute value
    scaled_tol = tol * max_abs_value
    
    # Create a 2D array of absolute differences
    abs_diff = np.abs(np.subtract.outer(A, B))
    
    # Return a boolean array where the condition is met
    return (abs_diff <= scaled_tol).any(axis=1)

def GetInXYZ(FeatureExtent, Coords, Precision=None):
    if Precision is not None:
        E = 10 ** (-Precision)
    else:
        E = 1000 * np.finfo(float).eps * np.max(np.abs(Coords))
    
    # eps tolerancing implemented to combat precision issues.
    if FeatureExtent[0] == FeatureExtent[1]:
        In = np.where(np.abs(FeatureExtent[0] - Coords) < np.finfo(float).eps)[0]
        return In[:-1]  # Return all but the last index
    else:
        In = np.where((FeatureExtent[0] - E <= Coords) & (Coords < FeatureExtent[1] - E))[0]
        return In


def FormModel(TestCaseModel):

    Xminus = 0
    Xplus = 1
    Yminus = 2
    Yplus = 3
    Zminus = 4
    Zplus = 5
    NoMatl = "NoMatl"

    ExternalConditions = TestCaseModel.ExternalConditions
    Features = TestCaseModel.Features
    Params = TestCaseModel.Params
    PottingMaterial = TestCaseModel.PottingMaterial
    Props = ["PottingMaterial", "MatLib", "ParamVar", "VariableList", "Features", "Params", "ExternalConditions", "Version"]

    MatLib = TestCaseModel.MatLib
    mat_names = MatLib.MatList()
    if NoMatl not in mat_names:
        null_material = PPMatNull(name = NoMatl)
        MatLib.AddMatl(null_material)

    if "h_Xminus" in list(ExternalConditions.keys()):
        h = np.zeros((6,))
        Ta = np.zeros((6,))
        h[Xminus] = ExternalConditions["h_Xminus"]
        h[Xplus] = ExternalConditions["h_Xplus"]
        h[Yminus] = ExternalConditions["h_Yminus"]
        h[Yplus] = ExternalConditions["h_Yplus"]
        h[Zminus] = ExternalConditions["h_Zminus"]
        h[Zplus] = ExternalConditions["h_Zplus"]

        Ta[Xminus] = ExternalConditions["Ta_Xminus"]
        Ta[Xplus] = ExternalConditions["Ta_Xplus"]
        Ta[Yminus] = ExternalConditions["Ta_Yminus"]
        Ta[Yplus] = ExternalConditions["Ta_Yplus"]
        Ta[Zminus] = ExternalConditions["Ta_Zminus"]
        Ta[Zplus] = ExternalConditions["Ta_Zplus"]

    Tproc = ExternalConditions["Tproc"]

    X = []
    Y = []
    Z = []
    X0 = []
    Y0 = []
    Z0 = []
    Xu = []
    Yu = []
    Zu = []

    MinFeatureSize = np.ones((3,)) * np.inf
    for i in range(len(Features)):
        Features[i]["x"] = sorted(Features[i]["x"])
        Features[i]["y"] = sorted(Features[i]["y"])
        Features[i]["z"] = sorted(Features[i]["z"])

        coords = np.linspace(Features[i]["x"][0], Features[i]["x"][1], 1 + Features[i]["dx"])
        Xu = Xu + [coords[0]] + [coords[-1]]
        if Features[i]["x"][0] != Features[i]["x"][1]:
            X = X + list(coords[1:-1])
            MinFeatureSize[0] = min(MinFeatureSize[0], np.min(coords[1:] - coords[:-1]))
        else:
            X0 = X0 + [coords[0]]

        coords = np.linspace(Features[i]["y"][0], Features[i]["y"][1], 1 + Features[i]["dy"])
        Yu = Yu + [coords[0]] + [coords[-1]]
        if Features[i]["y"][0] != Features[i]["y"][1]:
            Y = Y + list(coords[1:-1])
            MinFeatureSize[1] = min(MinFeatureSize[1], np.min(coords[1:] - coords[:-1]))
        else:
            Y0 = Y0 + [coords[0]]

        coords = np.linspace(Features[i]["z"][0], Features[i]["z"][1], 1 + Features[i]["dz"])
        Zu = Zu + [coords[0]] + [coords[-1]]
        if Features[i]["z"][0] != Features[i]["z"][1]:
            Z = Z + list(coords[1:-1])
            MinFeatureSize[2] = min(MinFeatureSize[2], np.min(coords[1:] - coords[:-1]))
        else:
            Z0 = Z0 + [coords[0]]

    Toler = 2
    if len(X0) > 0:
        max_value = np.max(X0)
        epsilon = np.spacing(max_value * 10 ** Toler)
        rounded_X0 = np.round(X0, int(np.floor(np.abs(np.log10(epsilon)))))
        X0 = list(np.unique(rounded_X0))
    if len(Y0) >0:
        max_value = np.max(Y0)
        epsilon = np.spacing(max_value * 10 ** Toler)
        rounded_Y0 = np.round(Y0, int(np.floor(np.abs(np.log10(epsilon)))))
        Y0 = list(np.unique(rounded_Y0))
    if len(Z0) > 0:
        max_value = np.max(Z0)
        epsilon = np.spacing(max_value * 10 ** Toler)
        rounded_Z0 = np.round(Z0, int(np.floor(np.abs(np.log10(epsilon)))))
        Z0 = list(np.unique(rounded_Z0))
    

    max_value = np.max(Xu)
    epsilon = np.spacing(max_value * 10 ** Toler)
    rounded_Xu = np.round(Xu, int(np.floor(np.abs(np.log10(epsilon)))))
    Xu = list(np.unique(rounded_Xu))

    max_value = np.max(Yu)
    epsilon = np.spacing(max_value * 10 ** Toler)
    rounded_Yu = np.round(Yu, int(np.floor(np.abs(np.log10(epsilon)))))
    Yu = list(np.unique(rounded_Yu))

    max_value = np.max(Zu)
    epsilon = np.spacing(max_value * 10 ** Toler)
    rounded_Zu = np.round(Zu, int(np.floor(np.abs(np.log10(epsilon)))))
    Zu = list(np.unique(rounded_Zu))

    MinFeatureSize = 2 + np.floor(np.abs(np.floor(np.minimum(0, np.log10(MinFeatureSize)))))
    X = np.unique(np.round(X, int(MinFeatureSize[0])))
    Y = np.unique(np.round(Y, int(MinFeatureSize[1])))
    Z = np.unique(np.round(Z, int(MinFeatureSize[2])))

    Toler = 0.001
    # Combine and sort arrays
    X = np.sort(np.concatenate([X0, Xu, X[~ismembertol(X, Xu, Toler)]]))  # Combine and sort for X
    Y = np.sort(np.concatenate([Y0, Yu, Y[~ismembertol(Y, Yu, Toler)]]))  # Combine and sort for Y
    Z = np.sort(np.concatenate([Z0, Zu, Z[~ismembertol(Z, Zu, Toler)]]))  # Combine and sort for Z

    DeltaCoord = {
        'X': X[1:] - X[:-1],
        'Y': Y[1:] - Y[:-1],
        'Z': Z[1:] - Z[:-1]
    }

    OriginPoint = [min(X), min(Y), min(Z)]
    Params["Tsteps"] = np.floor(Params["Tsteps"])
    ModelMatrix = np.nan * np.zeros((len(DeltaCoord['X']), len(DeltaCoord['Y']), len(DeltaCoord['Z'])))
    S = ModelMatrix.shape
    assert len(S) >=3, "Model cannot be planar!"

    Q = np.ones((S[0], S[1], S[2])) * -1

    if len(Params["Tsteps"]) == 0:
        GlobalTime = []
    else:
        GlobalTime = np.arange(0, (Params["Tsteps"] + 1) * Params["DeltaT"], Params["DeltaT"])


    MinCoord = [min(X), min(Y), min(Z)]

    ZeroThickness = []
    NonZeroThickness = []
    for Fi in range(len(Features)):
        x_unique = np.unique(Features[Fi]['x'])
        y_unique = np.unique(Features[Fi]['y'])
        z_unique = np.unique(Features[Fi]['z'])
        
        if any([len(x_unique) == 1, len(y_unique) == 1, len(z_unique) == 1]):
            ZeroThickness.append(Fi)
        else:
            NonZeroThickness.append(Fi)
    
    for Fii in range(len(NonZeroThickness)):
        Fi = NonZeroThickness[Fii]
        InX = GetInXYZ(Features[Fi]['x'], X, MinFeatureSize[0])
        InY = GetInXYZ(Features[Fi]['y'], Y, MinFeatureSize[1])
        InZ = GetInXYZ(Features[Fi]['z'], Z, MinFeatureSize[2])
        
        ModelMatrix[InX[0]:InX[-1]+1, InY[0]:InY[-1]+1, InZ[0]:InZ[-1]+1] = Fi

    for Fii in range(len(ZeroThickness)):
        Fi = ZeroThickness[Fii]
        InX = GetInXYZ(Features[Fi]['x'], X,)
        InY = GetInXYZ(Features[Fi]['y'], Y,)
        InZ = GetInXYZ(Features[Fi]['z'], Z,)
        
        if len(np.unique(Features[Fi]["x"])) == 1:
            UseLayer = GetZeroLayer(X, Features[Fi]["x"]) #.item()
            Plane = ModelMatrix[:,:,InX]
            PlaneUse = ModelMatrix[:,:,UseLayer]
            PlaneUse = PlaneUse.reshape(PlaneUse.shape[0],PlaneUse.shape[1],1)
            nan_indices = np.isnan(Plane)
            Plane[nan_indices] = PlaneUse[nan_indices]
            ModelMatrix[:,:,InX] = Plane
        elif len(np.unique(Features[Fi]["y"])) == 1:
            UseLayer = GetZeroLayer(Y, Features[Fi]["y"]) #.item()
            Plane = ModelMatrix[:,:,InY]
            PlaneUse = ModelMatrix[:,:,UseLayer]
            PlaneUse = PlaneUse.reshape(PlaneUse.shape[0],PlaneUse.shape[1],1)
            nan_indices = np.isnan(Plane)
            Plane[nan_indices] = PlaneUse[nan_indices]
            ModelMatrix[:,:,InY] = Plane
        elif len(np.unique(Features[Fi]["z"])) == 1:
            UseLayer = GetZeroLayer(Z, Features[Fi]["z"]) #.item()
            Plane = ModelMatrix[:,:,InZ]
            PlaneUse = ModelMatrix[:,:,UseLayer]
            PlaneUse = PlaneUse.reshape(PlaneUse.shape[0],PlaneUse.shape[1],1)
            nan_indices = np.isnan(Plane)
            Plane[nan_indices] = PlaneUse[nan_indices]
            ModelMatrix[:,:,InZ] = Plane
        
        ModelMatrix[InX[0]:InX[-1]+1, InY[0]:InY[-1]+1, InZ[0]:InZ[-1]+1] = Fi

    VA = ComputeVA(DeltaCoord)
    ScaledQ = np.zeros_like(ModelMatrix)
    ModelMatrix[VA == 0] = 0

    FeatureVolume = []
    for Fi in range(len(Features)):
        if Features[Fi]["Q"] == 0:
            ThisQ = []
        else:
            ThisQ = [-1 * Features[Fi]["Q"]]
        
        Fmask = (ModelMatrix == Fi)
        sol = VA[Fmask]
        Area = np.imag(sol)
        Volm = np.real(sol)
        TotalA = np.sum(Area).item()
        TotalV = np.sum(Volm).item()
        FeatureVolume.append(TotalV)

        if len(ThisQ) > 0:
            if TotalV == 0: # If this is a zero-thickness feature
                ScaledQ[Fmask] = Area / TotalA
            else:
                ScaledQ[Fmask] = Volm / TotalV

            Fmask_flat = Fmask.flatten(order = "F")  # Reshape Fmask to a 1D array, order is "F" to match matlab
            indices = np.where(Fmask_flat == 1)[0]

            for Ei in indices:
                original_index = np.unravel_index(Ei, Fmask.shape, order = "F")
                Q[original_index] = (ThisQ[0] * ScaledQ[original_index]).item()
    
    FeatureMatrix = ModelMatrix  
    ModelMatrix = ModelMatrix * 1j

    MatsInUse = np.zeros((MatLib.NumMat,))
    for Fi in range(len(Features)):
        feature_mat = Features[Fi]["Matl"]
        mat_index = MatLib.iNameList.index(feature_mat)
        MatsInUse[mat_index] = 1
    
    MatsInUse = np.where(MatsInUse)[0]


    FeatureMass = []
    for Fi in range(len(Features)):
        feature_mat = Features[Fi]["Matl"]
        try:
            mat_index = MatLib.iNameList.index(feature_mat)
        except:
            raise ValueError(f"Material {feature_mat} is unknown")

        ModelMatrix[ModelMatrix == Fi * 1j] = mat_index
        FeatureMat = MatLib.GetMatNum(mat_index)
        if hasattr(FeatureMat, 'rho'):
            FeatureMass.append(FeatureVolume[Fi] * FeatureMat.rho)
        else:
            FeatureMass.append(np.nan)
    
    MatNum = PottingMaterial 
    ModelMatrix[np.isnan(ModelMatrix)] = -1 #MatNum

    Fs = np.unique(FeatureMatrix[~np.isnan(FeatureMatrix)])
    Ftext = []
    for Fi in range(len(Fs)):
        if "Desc" in list(TestCaseModel.Features[int(Fi)].keys()):
            Ftext.append(TestCaseModel.Features[int(Fi)]["Desc"])
        else:
            Ftext.append("Feature " + f"{Fi}")

    ModelInput = {}
    ModelInput["OriginPoint"] = OriginPoint
    ModelInput["h"] = h    
    ModelInput["Ta"] = Ta  
    ModelInput["X"] = DeltaCoord["X"]  
    ModelInput["Y"] = DeltaCoord["Y"]  
    ModelInput["Z"] = DeltaCoord["Z"]  
    ModelInput["Tproc"] = Tproc
    ModelInput["Model"] = np.real(ModelMatrix)
    ModelInput["Model"] += 1
    ModelInput["FeatureMatrix"] = FeatureMatrix # The non-nan elements differ by 1
    # Let's also make it equal
    ModelInput["FeatureMatrix"] = np.where(np.isnan(ModelInput["FeatureMatrix"]), np.nan, ModelInput["FeatureMatrix"] + 1)
    ModelInput["FeatureDescr"] = Ftext
    ModelInput["Q"] = Q
    ModelInput["GlobalTime"] = GlobalTime
    ModelInput["Tinit"] = Params["Tinit"]
    ModelInput["MatLib"] = MatLib
    ModelInput["Descriptor"] = [] 
    ModelInput["FeatureVolume"] = FeatureVolume
    ModelInput["FeatureMass"] = FeatureMass
    ModelInput["Version"] = "V2.0"
    
    return ModelInput




    












    


