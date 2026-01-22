<div align="center">

# ParaPowerPython

Python adaptation of the (open-source) thermal solver [ParaPower](https://github.com/USArmyResearchLab/ParaPower) (originally written in MATLAB) for rapid evaluation of 3D power module thermal behavior using a lumped thermal resistance network.

</div>

## Overview

ParaPowerPython builds a discretized 3D representation (features: substrates, layers, components, bond wires, etc.) and computes temperature distribution for (currently) a single static thermal step. Internally it:

1. Loads a user JSON description (geometry, materials, boundary conditions, parameters).
2. Executes a static thermal solution (`main(..., mode="thermal", type_="static")`).
3. Returns either global maximum temperatures or per‑feature maxima.

## Installation

Requirements:

* Python ≥ 3.8
* `numpy`

Clone or copy this repository and ensure `materials.npy` stays in the root directory.

## Input JSON Structure

Top‑level keys expected by `main()`:

```jsonc
{
    "ExternalConditions": { /* convection & ambient temps */ },
    "Features": [ /* geometric feature list */ ],
    "Params": { /* simulation parameters */ }
}
```

### 1. ExternalConditions

Boundary convection coefficients (h) and ambient temperatures (Ta) are face‑labeled. Also include process / internal reference temperature `Tproc` if applicable.

| JSON Key    | Meaning                            | Example |
|-------------|------------------------------------|---------|
| h_Left      | Convection coeff at -X face        | 0       |
| h_Right     | Convection coeff at +X face        | 0       |
| h_Front     | Convection coeff at +Y face        | 0       |
| h_Back      | Convection coeff at -Y face        | 0       |
| h_Bottom    | Convection coeff at -Z face        | 150.0   |
| h_Top       | Convection coeff at +Z face        | 0       |
| Ta_Left     | Ambient temp at -X face (°C)       | 27.0    |
| Ta_Right    | Ambient temp at +X face (°C)       | 27.0    |
| Ta_Front    | Ambient temp at +Y face (°C)       | 27.0    |
| Ta_Back     | Ambient temp at -Y face (°C)       | 27.0    |
| Ta_Bottom   | Ambient temp at -Z face (°C)       | 27.0    |
| Ta_Top      | Ambient temp at +Z face (°C)       | 27.0    |
| Tproc       | Internal process / junction temp   | 230.0   |

Example:

```json
"ExternalConditions": {
    "h_Left": 0,
    "h_Right": 0,
    "h_Front": 0,
    "h_Back": 0,
    "h_Bottom": 150.0,
    "h_Top": 0,
    "Ta_Left": 27.0,
    "Ta_Right": 27.0,
    "Ta_Front": 27.0,
    "Ta_Back": 27.0,
    "Ta_Bottom": 27.0,
    "Ta_Top": 27.0,
    "Tproc": 230.0
}
```

### 2. Params

General simulation parameters (current implementation uses a single static step):

| Key      | Meaning                                 | Example |
|----------|-----------------------------------------|---------|
| Tsteps   | (Reserved) list of time steps           | []      |
| DeltaT   | Time increment between steps (s)        | 1       |
| Tinit    | Initial temperature (°C)                | 27.0    |

Example:

```json
"Params": {
    "Tsteps": [],
    "DeltaT": 1,
    "Tinit": 27.0
}
```

### 3. Features

Each feature describes a rectangular prism region (layer/component/etc.). Coordinates are given in micrometers (µm) and converted internally to meters. Mesh resolution is controlled by `dx`, `dy`, `dz` (number of divisions per axis segment).

| Key  | Meaning                                           |
|------|---------------------------------------------------|
| name | Feature descriptor (will map to `Desc`)           |
| x    | `[x_start, x_end]` in µm                          |
| y    | `[y_start, y_end]` in µm                          |
| z    | `[z_start, z_end]` in µm                          |
| dx   | Divisions along X (larger => finer)               |
| dy   | Divisions along Y                                 |
| dz   | Divisions along Z                                 |
| Q    | Volumetric heat generation term (units TBD)       |
| Matl | Material name (mapped to internal library)        |

Example feature list (simplified):

```json
"Features": [
    {
        "name": "base_plate",
        "x": [0, 10000],
        "y": [0, 10000],
        "z": [0, 500],
        "dx": 2, "dy": 2, "dz": 2,
        "Q": 0,
        "Matl": "Copper"
    },
    {
        "name": "mosfet_A",
        "x": [2000, 4000],
        "y": [2000, 4000],
        "z": [500, 800],
        "dx": 2, "dy": 2, "dz": 2,
        "Q": 10,
        "Matl": "SiC"
    }
]
```

Material names from external sources are auto‑translated (e.g. `copper` → `Cu`, `Pb-Sn Solder Alloy` → `SAC405`, `Air` → `AIR`). If an unknown name is supplied it is passed through unchanged.

## Full Minimal JSON Example

```json
{
    "ExternalConditions": {
        "h_Left": 0, "h_Right": 0, "h_Front": 0, "h_Back": 0,
        "h_Bottom": 150.0, "h_Top": 0,
        "Ta_Left": 27.0, "Ta_Right": 27.0, "Ta_Front": 27.0, "Ta_Back": 27.0,
        "Ta_Bottom": 27.0, "Ta_Top": 27.0,
        "Tproc": 230.0
    },
    "Params": { "Tsteps": [], "DeltaT": 1, "Tinit": 27.0 },
    "Features": [
        {"name": "base_plate", "x": [0, 10000], "y": [0, 10000], "z": [0, 500], "dx": 10, "dy": 10, "dz": 2, "Q": 0, "Matl": "Copper"},
        {"name": "mosfet_A", "x": [2000, 4000], "y": [2000, 4000], "z": [500, 800], "dx": 4, "dy": 4, "dz": 2, "Q": 10, "Matl": "SiC"}
    ]
}
```

## Usage


```python
from main import main
result = main("model.json", mode="thermal", type_="static", results_type="global")
print(result)
```

Arguments:

| Parameter     | Allowed Values          | Description |
|---------------|-------------------------|-------------|
| json_file     | Path to JSON model      | Input geometry & conditions |
| mode          | "thermal"               | (Future: other physics) |
| type_         | "static"                | Static thermal step (no transient loop yet) |
| results_type  | "global" / "individual" | Max temperature overall or per feature |

Return value:
* `global` → array of length 2 (initial and computed max temperatures).
* `individual` → dict: `{feature_name: [T_init, T_final], ...}`.

## Mesh & Performance Notes

* Larger `dx/dy/dz` values increase resolution but also runtime.
* All coordinates in the JSON are in micrometers (µm); they are automatically converted to meters.
