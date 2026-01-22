import numpy as np
import sys

# Assuming Stress_Substrate_Hsueh is located in a module named 'Hsueh'
# inside the current package. Adjust import as necessary.
try:
    from .Hsueh import Stress_Substrate_Hsueh
except ImportError:
    # Fallback if file structure differs
    pass


def Stress_Hsueh(Results):
    """
    Shell to call the Hsueh substrate model.

    Returns:
        dict: Containing 'X', 'Y', 'Z', 'VM' stress fields
        str: Error message if validation fails
    """

    err_text = []

    # Access Model Input
    # Assuming 'Results' is an object with a 'Model' attribute
    model_input = Results.Model

    # 1. Check for Thermal State
    # MATLAB: ~isempty(find(strcmpi(Results.StatesAvail,'Thermal')))
    states_avail_lower = [s.lower() for s in Results.StatesAvail]

    if 'thermal' in states_avail_lower:
        # In MATLAB this variable 'Tres' was retrieved but not seemingly used
        # in this shell function (likely used inside Stress_Substrate_Hsueh).
        Tres = Results.getState('Thermal')
    else:
        err_text.append('No thermal state exists for computing stress.\n')

    # 2. Substrate Validation
    substrate_keyword = 'substrate'

    # Find feature index (Case insensitive)
    # MATLAB: SubstrateFeature=find(strcmpi(...))
    substrate_feature_id = -1

    # Assuming FeatureDescr is a list of strings
    for idx, desc in enumerate(model_input["FeatureDescr"]):
        if desc.lower() == substrate_keyword:
            substrate_feature_id = idx  # Python uses 0-based indexing for IDs
            break

    if substrate_feature_id == -1:
        err_text.append(
            f'No substrate found. A feature named "{substrate_keyword}" '
            f'must exist to use this substrate dominated stress model.\n')
    else:
        fm = model_input["FeatureMatrix"]

        # --- THE FIX IS HERE ---
        # Python ID is 0, but Matrix contains 1. We must match the matrix data.
        target_id = substrate_feature_id + 1 

        # Check dimensions to ensure we slice Z correctly
        # Assuming shape is (X, Y, Z) -> (56, 55, 12)
        z_col_at_origin = fm[0, 0, :] 

        # Find indices where the feature matches the target_id (1)
        sub_layers = np.where(z_col_at_origin == target_id)[0]

        if len(sub_layers) == 0:
            err_text.append('Substrate must extend across entire base layer.\n')
        else:
            # Check if it starts at the bottom (Index 0)
            # MATLAB: SubLayers(1) ~= 1
            if sub_layers[0] != 0:
                err_text.append('Substrate must start at the bottom layer.\n')

            # Check continuity
            # MATLAB: max(diff(SubLayers)) > 1
            if len(sub_layers) > 1:
                diffs = np.diff(sub_layers)
                if np.max(diffs) > 1:
                    err_text.append(
                        'Substrate must be continuous from the bottom\n')

            # Check full layer continuity (ensure the whole XY plane at this Z is substrate)
            for layer in sub_layers:
                # MATLAB: ModelInput.FeatureMatrix(:,:,Layer)
                layer_slice = fm[:, :, layer]

                # Check if all elements in this slice equal the substrate ID
                if not np.all(layer_slice == target_id):
                    err_text.append(
                        f'Layer {layer} discontinuous. Substrate feature must '
                        f'be continuous across the length & width of the model.\n'
                    )

    # 3. Return Error or Calculate
    if len(err_text) > 0:
        # Return the accumulated error string (trimming the last newline not strictly required but matches MATLAB)
        raise ValueError("".join(err_text).strip())

    else:
        # Call the calculation function
        # We pass len(sub_layers) to represent the thickness/count

        # Ensure the helper function is imported
        if 'Stress_Substrate_Hsueh' not in globals():
            from .Hsueh.stress_substrate_hsue import Stress_Substrate_Miner1 as Stress_Substrate_Hsueh

        stress_x, stress_y = Stress_Substrate_Hsueh(Results, len(sub_layers))

        # 4. Calculate Von Mises
        # MATLAB: Stress.Z=Stress.X*0;
        stress_z = np.zeros_like(stress_x)

        # Von Mises Formula
        # VM = sqrt( ((s1-s2)^2 + (s1-s3)^2 + (s2-s3)^2) / 2 )
        term1 = (stress_x - stress_z)**2
        term2 = (stress_x - stress_y)**2
        term3 = (stress_y - stress_z)**2

        vm = np.sqrt((term1 + term2 + term3) / 2.0)

        # Create Output Dictionary
        stress = {
            "X": stress_x,
            "Y": stress_y,
            "VM": vm,
            "Z": np.full_like(stress_x,
                              np.nan)  # MATLAB sets Z to NaN at the very end
        }

        return stress
