import struct
import pandas as pd
import numpy as np

def snapshot_to_dataframe(file, is_binary):
    if not is_binary:
        return pd.read_csv(file)

    pressure_data_types = {
                0: np.float32,
                8: np.uint8,
                16: np.uint16
            }

    with open(file, 'rb') as f:
        coordinate_data_size = int.from_bytes(f.read(1))
        pressure_data_size = int.from_bytes(f.read(1))
        quantisation_level = int.from_bytes(f.read(1))
        number_of_nodes = int.from_bytes(f.read(4), byteorder="little")

    dt_coords = np.dtype([("x", np.float32), ("y", np.float32), ("z", np.float32)])
    data = np.fromfile(file, dtype=dt_coords, offset=7, count=number_of_nodes)
    df_coords = pd.DataFrame(data, columns=data.dtype.names)

    pressure_dtype = pressure_data_types[quantisation_level]

    dt_pressure = np.dtype([("pressure_min", np.float32), ("pressure_max", np.float32), ("iteration", np.int32), ("data", pressure_dtype, (number_of_nodes,))])
    data = np.fromfile(file, dtype=dt_pressure, offset=7 + number_of_nodes*4*3)
    
    n_iter = len(data)

    raw = data["data"]
    pmin = data["pressure_min"][:, None]
    pmax = data["pressure_max"][:, None]

    if quantisation_level == 0:
        pressures = raw
    else:
        levels = 2 ** quantisation_level - 1 
        pressures = pmin + raw.astype(np.float32) / levels * (pmax - pmin)

    df = pd.DataFrame({
        "iteration": np.repeat(data["iteration"], number_of_nodes),
        "node_id": np.tile(np.arange(number_of_nodes), n_iter),
        "x": np.tile(df_coords["x"].to_numpy(), n_iter),
        "y": np.tile(df_coords["y"].to_numpy(), n_iter),
        "z": np.tile(df_coords["z"].to_numpy(), n_iter),
        "pressure": pressures.ravel()
    })

    return df
