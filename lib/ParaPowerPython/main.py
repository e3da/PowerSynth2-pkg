import json
from PPMatLib import PPMatLib
from PPMatSolid import PPMatSolid
from PPMATPCM import PPMATPCM
import numpy as np
from utils import ConvertToPPTCM
from SCPPT import ScPPT
from FormModel import FormModel
from PRResults import PPResults
from stress_models.stress_hsue import Stress_Hsueh
import os


def list_to_mat(data_list):
    """
    Converts PowerSynth numerical lists to a list of floats.
    PowerSynth sends over x, y, and z coordinate start and end locations of
    features as a list of paired values as text. This function converts
    them to a list of floats compatible with ParaPower formatting.
    """
    data_mat = [float(data) for data in data_list[:2]]
    return data_mat


def NameLookUp(ps_name):
    """
    Converts PowerSynth material names to those used in ParaPower.
    This function is a temporary solution only until the material library linking is completed.
    """
    if not ps_name:
        ps_name = 'SiC'

    ps_mats = [
        'copper', 'Pb-Sn Solder Alloy', 'MarkeTech AlN 160', 'SiC', 'Aluminum',
        'Al_N', 'Copper', 'Air'
    ]
    pp_mats = ['Cu', 'SAC405', 'AlN', 'SiC', 'Al', 'AlN', 'Cu', 'AIR']

    if ps_name.lower() in (mat.lower() for mat in ps_mats):
        mat_map = dict(zip(ps_mats, pp_mats))
        parapower_name = mat_map.get(ps_name, ps_name)
    else:
        parapower_name = ps_name

    return parapower_name


def stress_static(model):
    model["Ta"] = np.array([-40, -40, -40, -40, -40, -40])
    model["h"] = np.array([100, 100, 100, 100, 100, 100])

    GlobalTime = [0, 100]
    model["GlobalTime"] = GlobalTime

    # 2. Time Logic initialization
    if len(model["GlobalTime"]) > 0:
        InitTime = [model["GlobalTime"][0]]
        ComputeTime = model["GlobalTime"][1:]

        # Reset model time for initialization setup
        model["GlobalTime"] = InitTime
        StepsToEstimate = 2
    else:
        InitTime = []
        StepsToEstimate = 0
        ComputeTime = []

    # 3. Initialize Object
    S1 = ScPPT(MI=model)
    S1.setup_impl()

    steps_limit = min(StepsToEstimate, len(ComputeTime))
    # Combine lists for the time argument
    current_times = InitTime + ComputeTime[:steps_limit]

    Tprnt, T_in, MeltFrac, MeltFrac_in = S1.step_impl(current_times)

    # 5. Simulation Part 2 and Concatenation
    if len(ComputeTime) > StepsToEstimate:
        # Compute states for the remaining times
        remaining_times = ComputeTime[StepsToEstimate:]

        Tprnt2, T_in2, MeltFrac2, MeltFrac_in2 = S1.step_impl(remaining_times)

        def ensure_4d(arr):
            return arr if arr.ndim == 4 else arr[:, :, :, np.newaxis]

        Tprnt = np.concatenate(
            (ensure_4d(T_in), ensure_4d(Tprnt), ensure_4d(Tprnt2)), axis=3)

        MeltFrac = np.concatenate((ensure_4d(MeltFrac_in), ensure_4d(MeltFrac),
                                   ensure_4d(MeltFrac2)),
                                  axis=3)

    else:
        # Concatenate: T_in + Tprnt
        Tprnt = np.concatenate(
            (T_in[:, :, :, np.newaxis], Tprnt[:, :, :, np.newaxis]), axis=3)
        MeltFrac = np.concatenate(
            (MeltFrac_in[:, :, :, np.newaxis], MeltFrac[:, :, :, np.newaxis]),
            axis=3)

    # 6. Restore Global Time
    model["GlobalTime"] = InitTime + ComputeTime

    # 7. Store Thermal Results
    # Matching the pattern: PPResults(ID, 'Thermal', 'MeltFrac')
    S_Results = PPResults(1, "Thermal", "MeltFrac")
    S_Results.setModel(model)
    S_Results.setState("Thermal", Tprnt)
    S_Results.setState("MeltFrac", MeltFrac)

    # Instantiate Stress model passing the current results
    stress_results = Stress_Hsueh(S_Results)

    # Add Stress state to results
    S_Results.addState("Stress", stress_results)

    S_Results.getState("Stress")

    return S_Results


def thermal_static(model):
    InitTime = []
    StepsToEstimate = 0
    ComputeTime = []

    S1 = ScPPT(MI=model)
    S1.setup_impl()
    Tprnt, T_in, MeltFrac, MeltFrac_in = S1.step_impl(ComputeTime)

    if len(ComputeTime) > StepsToEstimate:
        raise NotImplementedError(
            "The number of steps to estimate is greater than the number of steps to compute."
        )
    else:
        Tprnt = np.concatenate(
            (T_in[:, :, :, np.newaxis], Tprnt[:, :, :, np.newaxis]), axis=3)
        MeltFrac = np.concatenate(
            (MeltFrac_in[:, :, :, np.newaxis], MeltFrac[:, :, :, np.newaxis]),
            axis=3)

    results = PPResults(1, "Thermal", "MeltFrac")
    results.setState("Thermal", Tprnt)
    results.setState("MeltFrac", MeltFrac)
    return results


def get_global_max(results_object, result_type):
    time = [0, 0]
    temporary_results = np.zeros((len(time)))
    results_data = results_object.getState(result_type)

    for i in range(len(time)):
        results_data_slice = results_data[:, :, :, i]
        if result_type.lower() == "thermal":
            temporary_results[i] = np.max(results_data_slice)

    return temporary_results


def get_max_by_feature(results_object, result_type):
    FeatureDescr = results_object.Model["FeatureDescr"]
    time = [0, 0]
    results_data = results_object.getState(result_type)
    results = {}
    for i in range(len(FeatureDescr)):
        current_item = FeatureDescr[i]

        feat_ind = np.where(results_object.Model["FeatureMatrix"].flatten(
            order="F") == i + 1)
        temporary_results = np.zeros((len(time)))

        for j in range(len(time)):
            results_data_slice = results_data[:, :, :, j]
            temporary_results[j] = np.max(
                results_data_slice.flatten(order="F")[feat_ind])

        results[current_item] = temporary_results

    return results


def ParaPowerSynth(json_file, mode, type_, results_type):

    data = json.loads(json_file)
    data["Version"] = "V2.0"

    mlib = PPMatLib()

    # 1. Get the directory where THIS script (main.py) is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Create the full path to materials.npy
    mat_file_path = os.path.join(script_dir, "materials.npy")

    # 3. Load using the full path
    materials = np.load(mat_file_path, allow_pickle=True).item()

    mat_index = [0, 1, 2, 3, 7, 8, 14]
    for i in range(len(mat_index)):
        # Testing: cycle through materials in old lib and add them as new materials in the new PPMatLib structure.
        ind = mat_index[i]
        name = materials["Material"][ind]
        cte = materials["cte"][ind]
        E = materials["E"][ind]
        nu = materials["nu"][ind]
        k = materials["k"][ind]
        rho = materials["rho"][ind]
        cp = materials["cp"][ind]

        # Adjust thermal conductivity based on material name
        if name.lower() == 'air':
            k = 0.024
        elif name.lower() == 'sac405':
            k = 13.9

        # Create new material object
        new_matl = PPMatSolid(cte=cte, E=E, nu=nu, k=k, rho=rho, cp=cp)
        new_matl.name = name

        # Add the new material to the material library
        mlib.AddMatl(new_matl)

    new_matl = PPMATPCM(cte=2, E=1, nu=4, k=7, rho=4, cp=4)
    new_matl.name = "Test Material"
    mlib.AddMatl(new_matl)
    data["MatLib"] = mlib

    for i in range(len(data["Features"])):
        # Convert PowerSynth Material Names into ParaPower Material Names
        data["Features"][i]["Matl"] = NameLookUp(data["Features"][i]["Matl"])
        data["Features"][i]["x"] = [
            value * 1e-6 for value in data["Features"][i]["x"]
        ]
        data["Features"][i]["y"] = [
            value * 1e-6 for value in data["Features"][i]["y"]
        ]
        data["Features"][i]["z"] = [
            value * 1e-6 for value in data["Features"][i]["z"]
        ]

    # Update the name of the BasePlate to be Substrate
    data["Features"][0]["name"] = "substrate"

    data_converted = ConvertToPPTCM(data)

    PSMI = FormModel(data_converted)

    if mode == "thermal":
        if type_ == "static":
            resobj = thermal_static(PSMI)

    elif mode == "stress":
        if type_ == "static":
            resobj = stress_static(PSMI)

    resobj.Model["FeatureDescr"] = PSMI["FeatureDescr"]
    resobj.Model["FeatureMatrix"] = PSMI["FeatureMatrix"]

    res = []

    if mode == "thermal":
        if results_type == "global":
            ind_res = get_global_max(resobj, "Thermal")
        elif results_type == "individual":
            ind_res = get_max_by_feature(resobj, "Thermal")
        return ind_res
