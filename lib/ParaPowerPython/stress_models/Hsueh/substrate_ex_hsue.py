# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

import numpy as np


def substrate_ex_Miner1(Resultss, row, col, lay, dT, dzs, nlsubs, NLs, Ex, Ey,
                        nux, nuy, ctex, ctey, Mats, Melts):
    """
    Calculates the thermal stress in the top layer of the substrate material.
    Indices row, col, lay are assumed to be 0-based.
    """

    # 1. Calculate Z position
    # MATLAB: -sum(dzs(1:nlsubs)) + sum(dzs(1:lay)) - dzs(lay)/2
    # Python: 'lay' is 0-based index. To sum up to (and including) 'lay', we slice [:lay+1]
    z = -np.sum(dzs[:nlsubs]) + np.sum(dzs[:lay + 1]) - dzs[lay] / 2.0

    # 2. Substrate Properties (Current Element)
    # We access material properties using the ID stored in Mats
    mat_id = int(Mats[row, col, lay])

    EbsX = Ex[mat_id] / (1.0 - nux[mat_id])
    EbsY = Ey[mat_id] / (1.0 - nuy[mat_id])

    # Average Delta T in substrate and Total Substrate Thickness
    dTs = np.mean(dT[row, col, :nlsubs])
    ts = np.sum(dzs[:nlsubs])

    # 3. Initialize Sums
    sumcnX = 0.0
    sumdX = 0.0
    sumtbnX = 0.0
    sumrnX = 0.0
    sumrdX = 0.0

    sumcnY = 0.0
    sumdY = 0.0
    sumtbnY = 0.0
    sumrnY = 0.0
    sumrdY = 0.0

    # 4. Loop 1: Accumulate C and tb sums
    # Loop over layers ABOVE substrate (from index nlsubs to NLs-1)
    for i in range(nlsubs, NLs):
        curr_mat_id = int(Mats[row, col, i])
        curr_melt = Melts[row, col, i]

        # Validity Check: Skip if Void (0) or Melted
        # Note: Assuming Resultss...PPMatSolid check is equivalent to mat_id != 0 for simplicity
        is_valid_solid = (curr_mat_id != 0)

        if not is_valid_solid or curr_melt > 0:
            # Equivalent to adding 0, just pass
            pass
        else:
            # Ebi Calculation
            EbiX = Ex[curr_mat_id] / (1.0 - nux[curr_mat_id])

            # Accumulate X
            sumcnX += EbiX * dzs[i] * ctex[curr_mat_id] * dT[row, col, i]
            sumdX += EbiX * dzs[i]

            # Ebi Calculation Y
            EbiY = Ey[curr_mat_id] / (1.0 - nuy[curr_mat_id])

            # Accumulate Y
            sumcnY += EbiY * dzs[i] * ctey[curr_mat_id] * dT[row, col, i]
            sumdY += EbiY * dzs[i]

            # Calculate him1 (height of intermediate layers above substrate)
            if i == nlsubs:
                him1 = 0.0
            else:
                # Sum thicknesses between substrate top and current layer bottom
                him1 = np.sum(dzs[nlsubs:i])

            sumtbnX += EbiX * dzs[i] * (2 * him1 + dzs[i])
            sumtbnY += EbiY * dzs[i] * (2 * him1 + dzs[i])

    # 5. Intermediate Calculations
    # Using denominators. Note: Assumes sumdX + EbsX*ts != 0
    denomX = EbsX * ts + sumdX
    cX = (EbsX * ts * ctex[mat_id] * dTs + sumcnX) / denomX
    tbX = ((-EbsX * ts**2) + sumtbnX) / (2 * denomX)

    denomY = EbsY * ts + sumdY
    cY = (EbsY * ts * ctey[mat_id] * dTs + sumcnY) / denomY
    tbY = ((-EbsY * ts**2) + sumtbnY) / (2 * denomY)

    # 6. Loop 2: Accumulate r sums
    for i in range(nlsubs, NLs):
        curr_mat_id = int(Mats[row, col, i])
        curr_melt = Melts[row, col, i]

        is_valid_solid = (curr_mat_id != 0)

        if not is_valid_solid or curr_melt > 0:
            pass
        else:
            EbiX = Ex[curr_mat_id] / (1.0 - nux[curr_mat_id])
            EbiY = Ey[curr_mat_id] / (1.0 - nuy[curr_mat_id])

            if i == nlsubs:
                him1 = 0.0
            else:
                him1 = np.sum(dzs[nlsubs:i])

            # Precompute common geometry term
            geom_term = (2 * him1 + dzs[i])

            # X Accumulation
            termX = (cX - ctex[curr_mat_id] * dT[row, col, i])
            sumrdX += EbiX * dzs[i] * termX * geom_term

            big_geom_termX = 6 * (
                him1**2 + him1 * dzs[i]) + 2 * dzs[i]**2 - 3 * tbX * geom_term
            sumrnX += EbiX * dzs[i] * big_geom_termX

            # Y Accumulation
            termY = (cY - ctey[curr_mat_id] * dT[row, col, i])
            sumrdY += EbiY * dzs[i] * termY * geom_term

            big_geom_termY = 6 * (
                him1**2 + him1 * dzs[i]) + 2 * dzs[i]**2 - 3 * tbY * geom_term
            sumrnY += EbiY * dzs[i] * big_geom_termY

    # 7. Final Calculations (X)
    # Denom for rX
    denom_rX = 3 * (EbsX * (cX - ctex[mat_id] * dTs) * ts**2 - sumrdX)

    # Avoid division by zero if denom is 0 (Infinite radius / Uniform stress)
    if denom_rX == 0:
        # This case isn't handled in original MATLAB, but implies pure bending or uniform strain.
        # We typically set curvature to 0, implying rX -> infinity.
        # However, following strict translation, we let NumPy raise warning or return inf
        rX = ((EbsX * ts**2) *
              (2 * ts + 3 * tbX) + sumrnX) / 1e-12  # Fail safe or keep math
        # Better strict translation:
        # rX = ((EbsX * ts**2) * (2 * ts + 3 * tbX) + sumrnX) / denom_rX

    rX = ((EbsX * ts**2) * (2 * ts + 3 * tbX) + sumrnX) / denom_rX
    epsX = cX + (z - tbX) / rX
    sigmaX = EbsX * (epsX - ctex[mat_id] * dT[row, col, lay])

    # 8. Final Calculations (Y)
    denom_rY = 3 * (EbsY * (cY - ctey[mat_id] * dTs) * ts**2 - sumrdY)

    rY = ((EbsY * ts**2) * (2 * ts + 3 * tbY) + sumrnY) / denom_rY
    epsY = cY + (z - tbY) / rY
    sigmaY = EbsY * (epsY - ctey[mat_id] * dT[row, col, lay])

    return sigmaX, sigmaY
