#!/usr/bin/env python3
import pandas as pd
import numpy as np
import argparse
import subprocess
import os
import pyvista as pv

parser = argparse.ArgumentParser(
        prog="snaphot visualiser",
        description="Small script to run and visualise SEM proxy via snaphots"
        )

parser.add_argument("-s", "--sem_options", type=str, default="")
parser.add_argument("-f", "--snapshot_folder", type=str, default=".")
parser.add_argument("-i", "--snapshot_interval", type=int, default=100)
parser.add_argument("--run", action=argparse.BooleanOptionalAction)
parser.add_argument("--binary", action=argparse.BooleanOptionalAction)

args = parser.parse_args()

if args.run:
    if args.binary:
        binary_arg = "--snaphot-save-binary"
    else:
        binary_arg = "" 

    args_passed_to_sem = args.sem_options + f" --save-snapshot --snapshot-interval {args.snapshot_interval} --snapshot-folder {args.snapshot_folder} {binary_arg}"

    # If the folder dir doesn't exists, create it
    if not os.path.exists(args.snapshot_folder):
        os.mkdir(args.snapshot_folder)

    # run the simulation
    subprocess.run(f"./build/bin/semproxy {args_passed_to_sem}", shell=True)

file = args.snapshot_folder + "/snapshots.csv";
if args.binary:
    with open(file, 'rb') as f:
        coordinate_data_size = int.from_bytes(f.read(1))
        pressure_data_size = int.from_bytes(f.read(1))
    dt = np.dtype([("iteration", np.int32), ('x', np.float32), ('y', np.float32), ('z', np.float32), ("pressure", np.float32)])
    data = np.fromfile(file, dtype=dt, offset=2) 
    df = pd.DataFrame(data, columns=data.dtype.names)

else:
    df = pd.read_csv(file)
    
print(df)

vmax = df["pressure"].max()
vmin = df["pressure"].min()
vabs = max(abs(vmin), abs(vmax))

plotter = pv.Plotter(off_screen=True)
plotter.open_gif("animation.gif")
plotter.show_axes()

#print(f"Processing file {f}")
for iteration in df["iteration"].unique():
    df_filtered = df[df["iteration"] == iteration]
    cloud = pv.PolyData(df_filtered[["x", "y", "z"]].to_numpy())
    cloud["pressure"] = df_filtered["pressure"].to_numpy()
    plotter.clear()
    p = df_filtered["pressure"].to_numpy()
    alpha = np.clip(np.abs(p) / vabs, 0, 1)
    plotter.add_mesh(cloud, opacity=alpha, scalars="pressure", cmap="viridis", clim=[-vabs, vabs], point_size=3, render_points_as_spheres=True)
    plotter.write_frame()
    print(f"Iteration {iteration} done")

plotter.close()

