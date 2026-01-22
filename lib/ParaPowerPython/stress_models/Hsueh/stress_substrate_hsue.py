import numpy as np
import sys

# Assuming these helper functions exist in a module named 'Hsueh'
# You may need to adjust this import based on your file structure
from .substrate_ex_hsue import substrate_ex_Miner1 as substrate_ex_Hsueh
from .layer_ex_hsue import layer_ex_Miner1 as layer_ex_Hsueh


def Stress_Substrate_Miner1(Results, nlsub):
    """
    Calculates thermal stress based on CTE mismatch (Hsueh model).
    """
    DEBUG = False

    # 1. Load States
    # Assuming Temps/Melts shape is (X, Y, Z, Time) or similar
    Temps = Results.getState('Thermal')
    Melts = Results.getState('MeltFrac')

    # Check Time Dimension (Assuming last dimension is time)
    if Temps.shape[-1] != Melts.shape[-1]:
        raise ValueError(
            'MeltFrac and Thermal must have the same number of states.')

    num_states = Temps.shape[-1]

    # Initialize Output
    stressX = np.full(Temps.shape, np.nan)
    stressY = np.full(Temps.shape, np.nan)

    # 2. Load Static Model Data
    model = Results.Model

    # Load material properties (Assuming GetParam returns full 3D arrays)
    mat_lib = model["MatLib"]

    # In Python, we usually access methods or dict keys.
    # Adjust 'GetParam' call depending on your MatLib implementation.
    EX = mat_lib.GetParam('E')
    EY = mat_lib.GetParam('E')  # Usually Isotropic E
    nuX = mat_lib.GetParam('nu')
    nuY = mat_lib.GetParam('nu')
    cteX = mat_lib.GetParam('cte')
    cteY = mat_lib.GetParam('cte')

    ProcT = model["Tproc"]
    dz = model["Z"].flatten()

    # Geometry Dimensions
    # Note: MATLAB code explicitly mapped NR to X and NC to Y
    NL = len(model["Z"].flatten())
    NR = len(model["X"].flatten())
    NC = len(model["Y"].flatten())

    # Load Material Map (3D Integer Array)
    Mat = model["Model"]  # or model["Model"]

    # 3. Time Loop
    for state in range(num_states):

        # Extract current state data
        # Assuming layout (X, Y, Z, Time)
        Temp = Temps[..., state]
        Melt = Melts[..., state]

        delT = Temp - ProcT

        # 4. Spatial Loops
        # Python ranges are 0 to N-1
        for kk in range(NL):
            for ii in range(NR):
                for jj in range(NC):

                    # Retrieve Material ID
                    mat_id = Mat[ii, jj, kk]

                    # Logic: Check if material is valid
                    # In MATLAB: isa(..., 'PPMatSolid')
                    # In Python: We assume mat_id > 0 implies material exists.
                    # If you have a strict class check, implement it here.

                    ckMatl = False
                    if mat_id != 0:
                        # Placeholder for strict type checking if needed:
                        # ckMatl = isinstance(mat_lib.GetMatNum(mat_id), PPMatSolid)
                        ckMatl = True  # Assuming non-zero is solid for now

                    # Condition to Skip
                    if not ckMatl or Melt[ii, jj, kk] > 0:
                        stressX[ii, jj, kk, state] = np.nan
                        stressY[ii, jj, kk, state] = np.nan
                    else:
                        # Logic: Substrate vs Layer
                        # MATLAB: if kk <= nlsub (1-based comparison)
                        # Python: if kk < nlsub  (0-based comparison)
                        # Example: nlsub=1. MATLAB checks kk=1 (True). Python checks kk=0 (True).

                        if kk < nlsub:
                            sx, sy = substrate_ex_Hsueh(
                                Results, ii, jj, kk, delT, dz, nlsub, NL, EX,
                                EY, nuX, nuY, cteX, cteY, Mat, Melt)
                        else:
                            sx, sy = layer_ex_Hsueh(Results, ii, jj, kk, delT,
                                                    dz, nlsub, NL, EX, EY, nuX,
                                                    nuY, cteX, cteY, Mat, Melt)

                        stressX[ii, jj, kk, state] = float(sx)
                        stressY[ii, jj, kk, state] = float(sy)

    if DEBUG:
        print('\nDone.')

    return stressX, stressY
