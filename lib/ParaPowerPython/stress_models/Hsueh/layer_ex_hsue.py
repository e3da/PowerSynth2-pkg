import numpy as np

def layer_ex_Miner1(Resultsl, row, col, lay, dT, dzl, nlsubl, NLl, Ex, Ey, nux, nuy, ctex, ctey, Matl, Meltl):
    """
    Calculates the thermal stress in the film layers.
    Indices row, col, lay are assumed to be 0-based.
    nlsubl is the count of substrate layers.
    """

    # 1. Calculate Z position (Relative to Substrate-Film Interface)
    # MATLAB: if lay == nlsubl+1 ...
    # Python: nlsubl is the index of the first film layer.
    if lay == nlsubl:
        z = dzl[lay] / 2.0
    else:
        # Sum thicknesses from first film layer up to (but not including) current layer
        z = np.sum(dzl[nlsubl:lay]) + dzl[lay] / 2.0

    # 2. Substrate Reference Properties (Topmost Substrate Layer)
    # MATLAB used index 'nlsubl'. Python index is 'nlsubl - 1'.
    sub_idx = nlsubl - 1
    mat_sub = int(Matl[row, col, sub_idx])

    EbsX = Ex[mat_sub] / (1.0 - nux[mat_sub])
    EbsY = Ey[mat_sub] / (1.0 - nuy[mat_sub])

    # Average Delta T and Total Thickness of Substrate
    dTs = np.mean(dT[row, col, :nlsubl])
    ts = np.sum(dzl[:nlsubl])

    # 3. Current Layer Properties
    mat_curr = int(Matl[row, col, lay])
    EblX = Ex[mat_curr] / (1.0 - nux[mat_curr])
    EblY = Ey[mat_curr] / (1.0 - nuy[mat_curr])

    # 4. Initialize Sums
    sumcnX = 0.0; sumdX = 0.0; sumtbnX = 0.0
    sumrnX = 0.0; sumrdX = 0.0

    sumcnY = 0.0; sumdY = 0.0; sumtbnY = 0.0
    sumrnY = 0.0; sumrdY = 0.0

    # 5. Loop 1: Accumulate C and tb sums
    # Iterate over all film layers (from nlsubl to NLl)
    for i in range(nlsubl, NLl):
        curr_mat_id = int(Matl[row, col, i])
        curr_melt = Meltl[row, col, i]

        # Validity Check
        is_valid_solid = (curr_mat_id != 0)

        if not is_valid_solid or curr_melt > 0:
            pass
        else:
            # X Properties
            EbiX = Ex[curr_mat_id] / (1.0 - nux[curr_mat_id])
            sumcnX += EbiX * dzl[i] * ctex[curr_mat_id] * dT[row, col, i]
            sumdX  += EbiX * dzl[i]

            # Y Properties
            EbiY = Ey[curr_mat_id] / (1.0 - nuy[curr_mat_id])
            sumcnY += EbiY * dzl[i] * ctey[curr_mat_id] * dT[row, col, i]
            sumdY  += EbiY * dzl[i]

            # Calculate him1 (Height of intermediate layers from interface)
            if i == nlsubl:
                him1 = 0.0
            else:
                him1 = np.sum(dzl[nlsubl:i])

            sumtbnX += EbiX * dzl[i] * (2 * him1 + dzl[i])
            sumtbnY += EbiY * dzl[i] * (2 * him1 + dzl[i])

    # 6. Intermediate Constants
    denomX = EbsX * ts + sumdX
    cX = (EbsX * ts * ctex[mat_sub] * dTs + sumcnX) / denomX
    tbX = ((-EbsX * ts**2) + sumtbnX) / (2 * denomX)

    denomY = EbsY * ts + sumdY
    cY = (EbsY * ts * ctey[mat_sub] * dTs + sumcnY) / denomY
    tbY = ((-EbsY * ts**2) + sumtbnY) / (2 * denomY)

    # 7. Loop 2: Accumulate r sums
    for i in range(nlsubl, NLl):
        curr_mat_id = int(Matl[row, col, i])
        curr_melt = Meltl[row, col, i]

        is_valid_solid = (curr_mat_id != 0)

        if not is_valid_solid or curr_melt > 0:
            pass
        else:
            EbiX = Ex[curr_mat_id] / (1.0 - nux[curr_mat_id])
            EbiY = Ey[curr_mat_id] / (1.0 - nuy[curr_mat_id])

            if i == nlsubl:
                him1 = 0.0
            else:
                him1 = np.sum(dzl[nlsubl:i])

            geom_term = (2 * him1 + dzl[i])

            # X Accumulation
            termX = (cX - ctex[curr_mat_id] * dT[row, col, i])
            sumrdX += EbiX * dzl[i] * termX * geom_term

            big_geomX = 6 * (him1**2 + him1 * dzl[i]) + 2 * dzl[i]**2 - 3 * tbX * geom_term
            sumrnX += EbiX * dzl[i] * big_geomX

            # Y Accumulation
            termY = (cY - ctey[curr_mat_id] * dT[row, col, i])
            sumrdY += EbiY * dzl[i] * termY * geom_term

            big_geomY = 6 * (him1**2 + him1 * dzl[i]) + 2 * dzl[i]**2 - 3 * tbY * geom_term
            sumrnY += EbiY * dzl[i] * big_geomY

    # 8. Final Stress Calculation
    # X Axis
    denom_rX = 3 * (EbsX * (cX - ctex[mat_sub] * dTs) * ts**2 - sumrdX)
    rX = ((EbsX * ts**2) * (2 * ts + 3 * tbX) + sumrnX) / denom_rX

    epsX = cX + (z - tbX) / rX
    # Use EblX (Current layer Modulus)
    sigmaX = EblX * (epsX - ctex[mat_curr] * dT[row, col, lay])

    # Y Axis
    denom_rY = 3 * (EbsY * (cY - ctey[mat_sub] * dTs) * ts**2 - sumrdY)
    rY = ((EbsY * ts**2) * (2 * ts + 3 * tbY) + sumrnY) / denom_rY

    epsY = cY + (z - tbY) / rY
    # Use EblY (Current layer Modulus)
    sigmaY = EblY * (epsY - ctey[mat_curr] * dT[row, col, lay])

    return sigmaX, sigmaY