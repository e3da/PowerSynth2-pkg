# Modified from the original file, which can be found in https://github.com/USArmyResearchLab/ParaPower
# Github Repo: https://github.com/FhG-IISB/ParaPowerPython
# Developed by: Fraunhofer IISB

import numpy as np
from scipy.sparse import csr_matrix, diags
import scipy.sparse


class sPPT:

    def __init__(self, **kwargs):
        self.htcs = None
        self.Ta_vec = None
        self.Q = None
        self.GlobalTime = None
        self.MI = kwargs["MI"]
        self.Tres = None
        self.PHres = None
        self.T_in = None
        self.PH_in = None
        self.Qmask = None
        self.meltmask = None
        self.meltable = None
        self.Qv = None
        self.delta_t = None
        self.K = None
        self.CP = None
        self.RHO = None
        self.Lv = None
        self.Map = None
        self.fullheader = None
        self.Mat = None
        self.T = None
        self.PH = None
        self.A = None
        self.Atrans = None
        self.Cap = None
        self.vol = None
        self.B = None
        self.C = None
        self.Aj = None
        self.Bj = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def setupImpl(self):
        MI = self.MI
        h = MI['h']  # Same as matlab
        Ta = MI['Ta']  # Same as matlab
        Mat = MI['Model']  # Differs by 1 from Matlab
        Q = MI['Q'] 
        T_init = MI['Tinit']  # Same as matlab

        rollcall = list(set(Mat.flatten()))
        rollcall = [x for x in rollcall if x > 0]

        if MI['Version'] != 'V2.0':
            raise ValueError(
                f"Incorrect ModelInput version. V2.0 required, this data is {MI['Version']}"
            )

        Types = MI['MatLib'].GetParam('Type')
        vmatnum = [
            int(rollcall[i]) for i in range(len(rollcall))
            if Types[int(rollcall[i])] == 'IBC'
        ]
        hint = [0] * len(vmatnum)
        Ta_void = hint.copy()

        for vn in range(len(vmatnum)):
            h_ibc = MI['MatLib'].GetParamVector('h_ibc')
            hint[vn] = h_ibc[vmatnum[vn]]
            T_ibc = MI['MatLib'].GetParamVector('T_ibc')
            Ta_void[vn] = T_ibc[vmatnum[vn]]
            Mat[Mat == vmatnum[vn]] = -vn

        # Everything still fine here
        Qmask = np.where(Q == -1, False,
                         True).flatten(order="F")  # Same as matlab

        C = np.array([0] * sum(Mat.flatten(order="F") > 0))  # Same as matlab
        T = np.array([0] * sum(Mat.flatten(order="F") > 0))  # Same as matlab
        T[
            :,
        ] = T_init

        kond = MI['MatLib'].GetParamVector('k')  #same as matlab
        rho = MI['MatLib'].GetParamVector('rho')  #same as matlab
        spht = MI['MatLib'].GetParamVector('cp')  #same as matlab

        K = np.array([0] * sum(Mat.flatten(order="F") > 0))
        CP = K.copy()
        RHO = K.copy()

        Mat_flattened = Mat.flatten(order="F")

        indices = (Mat_flattened[Mat_flattened > 0]).astype(int)
        indices -= 1  # Due to matlab and python difference

        K = kond[indices]  # Same as matlab
        CP = spht[indices]  # Same as matlab
        RHO = rho[indices]  # Same as matlab

        meltable = any([
            Types[int(rollcall[i])] in ['PCM', 'SCPCM']
            for i in range(len(rollcall))
        ])
        PH = np.array([0] * sum(Mat.flatten() > 0))

        if meltable:
            kondl = MI['MatLib'].GetParamVector('k_l')
            sphtl = MI['MatLib'].GetParamVector('cp_l')
            rhol = MI['MatLib'].GetParamVector('rho_l')
            Lw = MI['MatLib'].GetParamVector('lf')
            Tmelt = MI['MatLib'].GetParamVector('tmelt')
            MatGZVec = [
                Mat[i] for i in range(len(Mat.flatten()))
                if Mat.flatten()[i] > 0
            ]
            for ThisMat in set(MatGZVec):
                MatMask = [
                    i for i in range(len(MatGZVec)) if MatGZVec[i] == ThisMat
                ]
                for mask in MatMask:
                    PH[mask] = 1 if T[mask] >= Tmelt[ThisMat] else 0
            self.Lv = [(rho[i] + rhol[i]) / 2 * Lw[i] for i in range(len(rho))]
        else:
            self.Lv = np.zeros_like(rho)

        Aj = {'adj': [], 'areas': [], 'hLengths': []}
        Bj = Aj.copy()

        Aj['adj'], Bj['adj'], _, Map = self.Connect_Init(Mat, h)
        Aj['adj'], Bj['adj'], Map, fullheader, Ta_vec = self.null_void_init(
            Mat, h, hint, Aj['adj'], Bj['adj'], Map, Ta, Ta_void)

        meltmask = [PH[i] > 0 for i in range(len(PH))]
        if any(meltmask):
            for i in range(len(meltmask)):
                if meltmask[i]:
                    K[i] = 1 / (PH[i] / kondl[Mat[Map[i]]] +
                                (1 - PH[i]) / kond[Mat[Map[i]]])
                    CP[i] = sphtl[Mat[Map[i]]] * PH[i] + spht[Mat[Map[i]]] * (
                        1 - PH[i])
                    RHO[i] = rhol[Mat[Map[i]]] * PH[i] + rho[Mat[Map[i]]] * (
                        1 - PH[i])

        A, B, Aj['areas'], Bj['areas'], Aj['hLengths'], Bj[
            'hLengths'], htcs = self.conduct_build(Aj['adj'], Bj['adj'], Map,
                                                   fullheader, K, hint, h, Mat,
                                                   MI['X'], MI['Y'], MI['Z'])

        if meltable:
            self.meltmask = [
                Types[Mat[Map[i]]] == 'PCM' for i in range(len(Map))
            ]

        self.MI = MI
        self.htcs = htcs
        self.Ta_vec = Ta_vec
        self.Q = Q
        self.Qmask = Qmask
        self.meltable = meltable
        self.K = K
        self.CP = CP
        self.RHO = RHO
        self.Map = Map
        self.fullheader = fullheader
        self.Mat = Mat
        self.T = T
        self.PH = PH
        self.A = A
        self.B = B
        self.C = C
        self.Aj = Aj
        self.Bj = Bj

    def Connect_Init(self, Mat, h):
        """
        Initializes matrix blocks A, B, and expanded B with connectivity entries implied by
        Mat and h.
        
        Parameters:
        Mat: 3D numpy array
        h: array of boundary conditions
        
        Returns:
        A, B, Bexp, Map: Connectivity matrices and mapping
        """

        # Create mapping array
        Map = np.arange(Mat.size).reshape(Mat.shape, order="F")  # x,y,z
        Map += 1  # Like this Map is equal in matlab and python
        nodes = Map.size  # number of rows of A and B

        # Convection coefficients with adjusted dimensions for padding
        h1 = np.ones((1, Mat.shape[1] + 2, Mat.shape[2]))
        h2 = h1.copy()
        h3 = np.ones((Mat.shape[0], 1, Mat.shape[2]))
        h4 = h3.copy()
        h5 = np.ones((Mat.shape[0] + 2, Mat.shape[1] + 2, 1))
        h6 = h5.copy()

        # Create padded map
        padmap = np.vstack([
            h1 * (nodes + 1),
            np.hstack([h3 * (nodes + 3), Map, h4 * (nodes + 4)]),
            h2 * (nodes + 2)
        ])
        padmap = np.concatenate([h5 * (nodes + 5), padmap, h6 * (nodes + 6)],
                                axis=2)

        # Build expanded connectivity map
        rowup = padmap[
            2:, 1:-1,
            1:-1]  # Row-wise map of columns of [A B] that need to be 1
        rowdown = padmap[:-2, 1:-1, 1:
                         -1]  # The ith element (linear indexing) of these vectors
        colup = padmap[
            1:-1, 2:,
            1:-1]  # contains the column index j of element ij in [A B]
        coldown = padmap[1:-1, :-2, 1:-1]  # that needs a 1
        layup = padmap[1:-1, 1:-1, 2:]
        laydown = padmap[1:-1, 1:-1, :-2]

        # Creating sparse triplet vectors (row,column,value)
        i = np.tile(np.arange(nodes), 6)
        j = np.concatenate([
            rowup.flatten(order="F"),
            rowdown.flatten(order="F"),
            colup.flatten(order="F"),
            coldown.flatten(order="F"),
            layup.flatten(order="F"),
            laydown.flatten(order="F")
        ])
        j -= 1  # Because it is an index and needs to match matlab
        v = np.concatenate([
            np.ones(nodes * 2), 2 * np.ones(nodes * 2), 3 * np.ones(nodes * 2)
        ])

        Full = csr_matrix((v, (i, j)), shape=(nodes, nodes + len(h)))

        A = Full[:, :Mat.size]
        Bexp = Full[:, Mat.size:]
        B = Bexp[:, h != 0]

        # Check symmetry and connectivity
        if not (A != A.T).nnz == 0:  # Check if A is symmetric
            raise ValueError('Symmetry of A violated')
        elif Full.nnz / Full.shape[0] != 6:
            print('Warning: Non-standard connectivity')

        return A, B, Bexp, Map

    def null_void_init(self, Mat, h, hint, A, B, Map, Ta, Ta_void):
        """
        Modifies connectivity maps to account for internal voids and null materials.
        
        Parameters:
        Mat: numpy array - material matrix
        h: array - boundary conditions
        hint: array - void heat transfer coefficients
        A, B: sparse matrices - connectivity matrices
        Map: array - mapping array
        Ta: array - ambient temperatures
        Ta_void: array - void temperatures
        
        Returns:
        A, B: modified connectivity matrices
        Map: updated mapping
        fullheader: combined header information
        Ta_vec: temperature vector
        """

        Map = Map.reshape(-1, 1, order="F")
        header = np.array([], dtype=int)

        if np.any(
                Mat < 0
        ):  # Handle voids present in the model  -1 due to the indexing difference between python and matlab
            for voidnum in range(1, int(abs(min(Mat.flatten()))) + 1):
                voids = (Mat == -voidnum).flatten()
                if not np.any(voids):  # no voids of this number
                    continue

                if voidnum > len(hint) or hint[voidnum -
                                               1] == 0:  # undefined or zero h
                    Mat[Mat == -voidnum] = 0  # reset to null material
                    print(f'Void {-voidnum} has zero or undefined h.')
                    continue

                remap_full = np.concatenate(
                    [np.where(~voids)[0],
                     np.where(voids)[0]])
                remain = np.sum(~voids)

                A = A[remap_full][:, remap_full]
                B = B[remap_full]
                Map = Map[remap_full]
                Mat = Mat.flatten()[remap_full]

                # Collapse A by shifting void connections to B
                Badd = A[:remain, remain:].tocsr()
                i = Badd.nonzero()[0]

                if len(i) == len(np.unique(i)):  # no multiplicities
                    B = np.hstack([Badd.sum(axis=1), B[:remain]])
                    mt = 1
                else:
                    Badd = np.sort(Badd.toarray(),
                                   axis=1)[:, ::-1]  # sort descending
                    j = np.nonzero(Badd)[1]
                    mt = j.max() + 1  # j lists multiplicity
                    B = np.hstack([Badd[:, :mt], B[:remain]])

                A = A[:remain, :remain]
                Map = Map[:remain]
                Mat = Mat[:remain]

                header = np.concatenate(
                    [-voidnum * np.ones(mt, dtype=int), header])

        if np.any(Mat == 0):  # Handle null materials
            remap = np.where(Mat.flatten(order="F") != -0)[0]

            A = A[remap][:, remap]  # delete rows and cols for null materials
            B = B[remap]  # delete rows
            Map = Map[remap]  # consolidate Map and Mat
            Mat = Mat.flatten(order="F")[remap]

        # Construct fullheader and Ta_vec
        h_nonzero = np.where(h != 0)[0] + 1  # adding 1 to match MATLAB indexing
        fullheader = np.concatenate([header, h_nonzero])

        Ta_vec = Ta_void[-header] if len(header) > 0 else np.array([])
        Ta_vec = np.concatenate([Ta_vec, Ta[h != 0]])

        return A, B, Map, fullheader, Ta_vec

    def conduct_build(self, Acon, Bcon, Map, header, K, hint, h, Mat, drow,
                      dcol, dlay):
        """
        Builds Conductance Matrices using connectivity matrices, dimensional info,
        and material properties/convection coefficients.
        
        Parameters:
        Acon, Bcon: sparse matrices - connectivity matrices
        Map: array - mapping array
        header: array - header information
        K: array - thermal conductivity values
        hint, h: arrays - heat transfer coefficients
        Mat: 3D array - material matrix
        drow, dcol, dlay: arrays - dimensional information
        
        Returns:
        Acond, Bcond: conductance matrices
        A_areas, B_areas: area matrices
        A_hLengths, B_hLengths: length matrices
        htcs: heat transfer coefficients
        """
        """
        Acon is the same, Bcon also the same and so is Map.
        """
        # Initialize sparse matrices
        A_areas = csr_matrix((Acon.shape), dtype=float)
        A_hLengths = csr_matrix((Acon.shape), dtype=float)
        B_areas = csr_matrix((Bcon.shape), dtype=float)
        B_hLengths = csr_matrix((Bcon.shape), dtype=float)

        # Helper function for reciprocal of sparse matrix
        def reciprocal(X):
            X = X.tocoo()
            data_recip = np.float64(1.0) / np.float64(X.data)
            return csr_matrix((data_recip, (X.row, X.col)),
                              shape=X.shape,
                              dtype=np.float64)

        # Store Geometry
        for dir in range(1, 4):
            # Find connections for current direction
            A = scipy.sparse.find(Acon == dir)
            B = scipy.sparse.find(Bcon == dir)
            Ai = A[1]
            Aj = A[0]
            Bi = B[0]
            Bj = B[1]

            # Convert linear indices to subscripts
            # The -1 in Map[Ai] - 1 assures that the indexes are the same in Python and matlab.
            A_rows, A_cols, A_lays = np.unravel_index(Map[Ai] - 1,
                                                      Mat.shape,
                                                      order='F')
            B_rows, B_cols, B_lays = np.unravel_index(Map[Bi] - 1,
                                                      Mat.shape,
                                                      order="F")

            # Calculate areas and lengths based on direction
            if dir == 1:  # row-wise connections
                areasA = dcol[:, A_cols] * dlay[:, A_lays]
                areasB = dcol[:, B_cols] * dlay[:, B_lays]
                lengthsA = drow[:, A_rows] / 2
                lengthsB = drow[:, B_rows] / 2
            elif dir == 2:  # column-wise connections
                areasA = drow[:, A_rows] * dlay[:, A_lays]
                areasB = drow[:, B_rows] * dlay[:, B_lays]
                lengthsA = dcol[:, A_cols] / 2
                lengthsB = dcol[:, B_cols] / 2
            else:  # layer-wise connections
                areasA = dcol[:, A_cols] * drow[:, A_rows]
                areasB = dcol[:, B_cols] * drow[:, B_rows]
                lengthsA = dlay[:, A_lays] / 2
                lengthsB = dlay[:, B_lays] / 2

            areasA = areasA.reshape(-1)
            areasB = areasB.reshape(-1)
            lengthsA = lengthsA.reshape(-1)
            lengthsB = lengthsB.reshape(-1)

            # Update sparse matrices
            A_areas += csr_matrix((areasA, (Ai, Aj)), shape=Acon.shape)
            A_hLengths += csr_matrix((lengthsA, (Ai, Aj)), shape=Acon.shape)
            B_areas += csr_matrix((areasB, (Bi, Bj)), shape=Bcon.shape)
            B_hLengths += csr_matrix((lengthsB, (Bi, Bj)), shape=Bcon.shape)

        # Incorporate Conductivities
        Acond = A_areas.multiply(reciprocal(A_hLengths))
        K_diag = diags(K.reshape(-1), 0, shape=Acon.shape)
        Acond = K_diag.dot(Acond)
        Acond = reciprocal(reciprocal(Acond) + reciprocal(Acond.T))

        # Check symmetry
        if not (Acond != Acond.T).nnz == 0:
            raise ValueError('Symmetry Error!')

        # Calculate Bcond
        Bcond_out = B_areas.multiply(reciprocal(B_hLengths))
        Bcond_out = K_diag.dot(Bcond_out)

        # Build htcs from header and h lists
        htcs = h[header - 1]
        htcs_diag = diags(htcs, 0)
        Bcond_in = B_areas.dot(htcs_diag)
        Bcond = reciprocal(reciprocal(Bcond_out) + reciprocal(Bcond_in))

        # Update diagonal elements
        total_sum = Acond.sum(axis=1) + Bcond.sum(axis=1)
        Acond = Acond - diags(total_sum.A.flatten(), 0)

        return Acond, Bcond, A_areas, B_areas, A_hLengths, B_hLengths, htcs
