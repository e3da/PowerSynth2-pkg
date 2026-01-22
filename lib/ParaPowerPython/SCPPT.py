# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

import numpy as np
from sPPT import sPPT
from scipy.sparse import csr_matrix, coo_matrix, diags
from scipy.sparse.linalg import spsolve


class ScPPT(sPPT):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sc_mask = None

    def setup_impl(self):
        super().setupImpl()
        Types = self.MI["MatLib"].GetParam('Type')
        self.sc_mask = np.zeros(
            self.Map.shape)  #TODO: This is not how it is supposed to be

        if self.sc_mask.any() and not self.meltable:
            self.meltmask = np.zeros_like(self.sc_mask)
            self.meltable = True

    def Qinit(self, Q, GlobalTime, Qmask=None):
        if Qmask is None:
            Qmask = np.array([q is not None for q in Q])

        if len(GlobalTime) == 0:
            # Static Analysis
            Qval = Q.reshape(-1, order="F")[Qmask]
            indices = np.where(Qmask)[0]
            j = np.zeros(indices.shape)
            # Create a sparse matrix using coo_matrix
            Qv = csr_matrix((Qval, (indices, j)), shape=(len(Qmask), 1))
        else:
            # Transient Analysis

            # 1. Get the Active Indices (QmFind)
            # We must flatten in 'F' order to match MATLAB's linear indexing
            # This assumes Qmask is a boolean array of the same shape as Q
            flat_mask = Qmask.flatten(order='F')
            flat_indices = np.flatnonzero(flat_mask)

            # 2. Get the Values (Qval)
            # Because the function is constant, the "average over the timestep"
            # is simply the value itself.
            active_values = Q.flatten(order='F')[flat_indices]

            # 3. Determine Matrix Dimensions
            # MATLAB: Qv is (TotalPixels) x (TimeSteps - 1)
            num_rows = Q.size  # Total number of pixels/voxels
            num_cols = len(GlobalTime) - 1
            num_active = len(flat_indices)

            # 4. Construct the Sparse Matrix (Qv)
            # We need to repeat the active_values for every time column.
            # Using COO format (data, (row, col)) is the fastest way to build this.

            # Repeat indices: [Idx1, Idx1, Idx2, Idx2...]
            rows = np.repeat(flat_indices, num_cols)

            # Tile time steps: [0, 1, 0, 1...]
            cols = np.tile(np.arange(num_cols), num_active)

            # Repeat data: [Val1, Val1, Val2, Val2...]
            data = np.repeat(active_values, num_cols)

            # Create the sparse matrix
            # This matches MATLAB's Qv structure exactly
            Qv = coo_matrix((data, (rows, cols)),
                            shape=(num_rows, num_cols)).tocsc()

        return Qv  #Equal to matlab

    def step_impl(self, ComputeTime):
        if not ComputeTime or np.isnan(ComputeTime).any():
            self.GlobalTime = ComputeTime
        else:
            if not self.GlobalTime:
                self.GlobalTime = ComputeTime
            else:
                if ComputeTime[0] <= self.GlobalTime[0]:
                    raise ValueError(
                        'Attempted time reversal prior to beyond stored record'
                    )
                elif ComputeTime[0] > self.GlobalTime[-1]:
                    ComputeTime = np.concatenate(
                        ([self.GlobalTime[-1]], ComputeTime))
                    self.GlobalTime = ComputeTime
                else:
                    resume_step = np.where(
                        self.GlobalTime < ComputeTime[0])[0][-1]
                    self.T[:, -1] = self.T[:, resume_step]
                    self.PH[:, -1] = self.PH[:, resume_step]
                    ComputeTime = np.concatenate(
                        ([self.GlobalTime[resume_step]], ComputeTime))
                    self.GlobalTime = ComputeTime

        MI = self.MI
        Q = self.Q
        Qmask = self.Qmask
        meltmask = self.meltmask
        meltable = self.meltable
        Lv = self.Lv
        Map = self.Map
        Mat = self.Mat
        A = self.A
        Atrans = self.Atrans
        Cap = self.Cap
        vol = self.vol
        B = self.B
        C = self.C
        Aj = self.Aj
        Bj = self.Bj

        Qv = self.Qinit(Q, ComputeTime, Qmask)

        T = np.zeros((np.count_nonzero(Mat > 0), max(2, len(ComputeTime))))
        PH = np.zeros((np.count_nonzero(Mat > 0), max(2, len(ComputeTime))))
        # Add a new axis to the self.T and self.PH vector, self.T has shape (a,) but I want (a,1)
        self.T = self.T[:, np.newaxis]
        self.PH = self.PH[:, np.newaxis]

        T[:, 0] = self.T[:, -1]
        PH[:, 0] = self.PH[:, -1]

        if len(ComputeTime) > 0:
            delta_t = np.diff(ComputeTime)
            Cap, vol = self.mass(MI["X"], MI["Y"], MI["Z"], self.RHO, self.CP, Mat)
            vol = vol.reshape(Mat.shape, order='F')

            # It is faster to do the division on the vector first
            dt = delta_t[0]  # MATLAB index 1 -> Python index 0
            diag_values = -Cap / dt

            # Create the sparse diagonal matrix
            Atrans = diags(diag_values, 0, shape=A.shape, format='csc')

            # 4. Calculate C (The Source Vector)
            # Logic: Element-wise multiplication of the transient factor and the initial temperature.
            # Note: T[:, 0] corresponds to MATLAB's T(:,1)
            C = diag_values * T[:, 0]
        else:
            delta_t = np.nan
            # Create an all zero-sparse with the same shape as A
            Atrans = csr_matrix((A.shape[0], A.shape[1]))
            ComputeTime = [0, np.nan]

        self.delta_t = delta_t
        for it in range(1, len(ComputeTime)):
            matrixA = A + Atrans
            vectorB = (-B @ self.Ta_vec)[:, np.newaxis] + Qv[Map - 1, it -1] + C[:,np.newaxis]

            T[:, it] = spsolve(matrixA, vectorB)

            if meltable and not np.isnan(ComputeTime[1]):
                T[:,
                  it], PH[:,
                          it], changing, self.K, self.CP, self.RHO = self.vec_Phase_Change(
                              T[:, it], PH[:, it - 1], Mat, Map, meltmask,
                              MI.MatLib.GetParamVector('k'),
                              MI.MatLib.GetParamVector('k_l'),
                              MI.MatLib.GetParamVector('cp'),
                              MI.MatLib.GetParamVector('cp_l'),
                              MI.MatLib.GetParamVector('rho'),
                              MI.MatLib.GetParamVector('rho_l'),
                              MI.MatLib.GetParamVector('tmelt'), Lv, self.K,
                              self.CP, self.RHO)
                T, PH, changing = self.ph_ch_hook(T, PH, changing, it)

            if not np.isnan(ComputeTime[1]):
                if meltable and changing.any():
                    touched = changing | (Aj.adj @ changing) > 0
                    Cap[changing] = self.mass(MI.X, MI.Y, MI.Z, self.RHO,
                                              self.CP, Mat, changing)
                    A, B, _ = self.conduct_update(A, B, Aj.areas, Bj.areas,
                                                  Aj.hLengths, Bj.hLengths,
                                                  self.htcs, self.K, touched)

                # 1. Get the time delta for this step
                # MATLAB: delta_t(it-1)  -> Accesses the previous index (1-based math)
                # Python: delta_t[it-1]  -> Accesses the correct corresponding index
                dt = delta_t[it - 1]

                # 2. Calculate the diagonal values (Vectorized)
                # It is much cleaner to do the division once on the vector
                diag_values = -Cap / dt

                # 3. Create Atrans
                # MATLAB: -spdiags(Cap, 0, ...)./dt
                # Python: We create the diagonal matrix directly using the calculated values.
                # 'format' should match your matrix 'A' (likely 'csr' or 'csc') to make addition fast later.
                Atrans = diags(diag_values, 0, shape=A.shape, format='csc')

                # 4. Calculate C
                # MATLAB: ... .* T(:,it)
                # Python: T[:, it] gets the column corresponding to the current step 'it'
                C = diag_values * T[:, it]

            self.T = T[:, it]
            self.PH = PH[:, it]
            self.A = A
            self.B = B

        Tres = np.zeros((Mat.size, T.shape[1] - 1))
        PHres = np.zeros_like(Tres)
        T_in = np.zeros(Mat.size)
        PH_in = np.zeros_like(T_in)

        T_in[(Mat > 0).flatten(order="F")] = T[:, 0]
        Tres[(Mat > 0).flatten(order="F")] = T[:, 1:]
        PH_in[(Mat > 0).flatten(order="F")] = PH[:, 0]
        PHres[(Mat > 0).flatten(order="F")] = PH[:, 1:]

        modelsize = MI["Model"].shape
        T_in = T_in.reshape(modelsize, order="F")
        Tres = Tres.reshape(modelsize, order="F")
        PH_in = PH_in.reshape(modelsize, order="F")
        PHres = PHres.reshape(modelsize, order="F")

        self.T_in = T_in
        self.Tres = Tres
        self.PH_in = PH_in
        self.PHres = PHres

        self.Q = Q
        self.T = T
        self.PH = PH
        self.Atrans = Atrans
        self.Cap = Cap
        self.C = C

        return Tres, T_in, PHres, PH_in

    def mass(self, dx, dy, dz, RHO, CP, Mat, Mask=None):
        """
        Calculates capacity and volume vectors.

        Parameters:
        dx, dy, dz : 1D arrays representing grid spacing (lengths NC, NR, NL)
        RHO        : Density array (flattened or 3D)
        CP         : Specific Heat array (flattened or 3D)
        Mat        : Material ID matrix (3D)
        Mask       : (Optional) Mask defining which elements to calculate.
                     If provided, it is assumed to be an index/mask relative 
                     to the 'solid' elements (Mat > 0).

        Returns:
        cap        : Heat capacity vector (masked/compressed)
        vol        : The FULL flattened volume vector
        """

        # 1. Calculate the 3D Volume Grid
        dx = dx.flatten()
        dy = dy.flatten()
        dz = dz.flatten()
        vol_3d = dx[:, None, None] * dy[None, :, None] * dz[None, None, :]

        # Flatten to 1D using Fortran order to match MATLAB linear indexing
        vol = vol_3d.flatten(order='F')

        # Ensure inputs are flat (Fortran order)
        if RHO.ndim > 1: RHO = RHO.flatten(order='F')
        if CP.ndim > 1: CP = CP.flatten(order='F')

        # Identify solid materials
        Mat_flat = Mat.flatten(order='F')
        is_solid = Mat_flat > 0

        # 2. Extract solid volumes
        # In MATLAB: solid_vol = vol(Mat>0)
        solid_vol = vol[is_solid]

        # 3. Calculate Capacity
        if Mask is None:
            # CHECK: Are RHO/CP already compressed to the solid size?
            if RHO.size == solid_vol.size and CP.size == solid_vol.size:
                # CASE A: Inputs are already compressed
                cap = RHO * CP * solid_vol
            else:
                # CASE B: Inputs are full grid size (36960) and need filtering
                cap = RHO[is_solid] * CP[is_solid] * solid_vol
        else:
            # Case: Mask is provided
            # MATLAB Logic: cap = RHO(Mask).*CP(Mask).*solid_vol(Mask)

            # IMPORTANT: The MATLAB code implies 'Mask' is an index into 
            # the *subset* of solid elements (because it indexes 'solid_vol').

            # If Mask is boolean relative to the 'solid_vol' array:
            cap = RHO[Mask] * CP[Mask] * solid_vol[Mask]

            # If Mask passed from Python is Global (full size), you would do this instead:
            # global_mask_flat = Mask.flatten(order='F')
            # target_indices = global_mask_flat[is_solid] # Intersection
            # cap = RHO[global_mask_flat] * CP[global_mask_flat] * vol[global_mask_flat]

        return cap, vol
    
    def ph_ch_hook(self, T, PH, changing, it):
        sc_mask = self.sc_mask
        if not sc_mask.any():
            return T, PH, changing

        prop_thres = 0
        T_nucM = self.MI.MatLib.GetParamVector('dT_Nucl')
        T_nucM = self.MI.MatLib.GetParamVector('tmelt') - T_nucM

        T_nuc = np.zeros_like(sc_mask)
        T_nuc = T_nucM[self.Mat[self.Map]]
        T_nuc = T_nuc[sc_mask]

        priorPH = PH[:, it - 1]
        newPH = PH[:, it]

        state = np.zeros((len(sc_mask), 3))
        state[sc_mask, 0] = priorPH[sc_mask] < 1
        state[sc_mask, 1] = T[sc_mask, it] <= T_nuc
        state[sc_mask, 3] = priorPH[sc_mask] <= prop_thres

        if state[sc_mask, 3].size > 0:
            state[sc_mask, 3] = state[sc_mask, 3] | (
                self.Aj.adj(sc_mask, sc_mask) @ state[sc_mask, 3]) > 0

        newtouch = state[:, 3]
        prop = True
        T_iter = T[:, it]

        while prop:
            sc_trig = state.any(axis=1)

            T_iter, newPH, sc_changing, self.K, self.CP, self.RHO = self.vec_Phase_Change(
                T_iter, priorPH, self.Mat, self.Map, sc_trig,
                self.MI.MatLib.GetParamVector('k'),
                self.MI.MatLib.GetParamVector('k_l'),
                self.MI.MatLib.GetParamVector('cp'),
                self.MI.MatLib.GetParamVector('cp_l'),
                self.MI.MatLib.GetParamVector('rho'),
                self.MI.MatLib.GetParamVector('rho_l'),
                self.MI.MatLib.GetParamVector('tmelt'), self.Lv, self.K,
                self.CP, self.RHO)

            newtouch[sc_mask] = newPH[sc_mask] <= prop_thres

            if newtouch[sc_mask].size > 0:
                newtouch[sc_mask] = newtouch[sc_mask] | (
                    self.Aj.adj(sc_mask, sc_mask) @ newtouch[sc_mask]) > 0

            prop = (newtouch[sc_mask] & np.logical_xor(
                state[sc_mask, 3], newtouch[sc_mask])).any()
            if prop:
                priorPH = newPH
                state[sc_mask, 3] = newtouch[sc_mask]

        T[:, it] = T_iter
        PH[:, it] = newPH
        changing = sc_changing | changing

        return T, PH, changing
