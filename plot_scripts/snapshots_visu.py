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
parser.add_argument("-f", "--snapshot_folder", type=str, default="./snapshots")
parser.add_argument("-i", "--snapshot_interval", type=int, default=100)
parser.add_argument("--run", action=argparse.BooleanOptionalAction)

args = parser.parse_args()

if args.run:
    args_passed_to_sem = args.sem_options + f" --save-snapshot --snapshot-interval {args.snapshot_interval} --snapshot-folder {args.snapshot_folder}"

    # If the folder dir doesn't exists, create it
    if not os.path.exists(args.snapshot_folder):
        os.mkdir(args.snapshot_folder)

    # run the simulation
    subprocess.run(f"./build/bin/semproxy {args_passed_to_sem}", shell=True)

files = [e.path for e in os.scandir(args.snapshot_folder)]
vmax = max(pd.read_csv(f, usecols=["pressure"])["pressure"].max() for f in files)
vmin = min(pd.read_csv(f, usecols=["pressure"])["pressure"].min() for f in files)
vabs = max(abs(vmin), abs(vmax))

plotter = pv.Plotter(off_screen=True)
plotter.open_gif("animation.gif")
plotter.show_axes()
for f in files:
    print(f"Processing file {f}")
    df = pd.read_csv(f)
    cloud = pv.PolyData(df[["x", "y", "z"]].to_numpy())
    cloud["pressure"] = df["pressure"].to_numpy()
    plotter.clear()
    p = df["pressure"].to_numpy()
    alpha = np.clip(np.abs(p) / vabs, 0, 1)
    plotter.add_mesh(cloud, opacity=alpha, scalars="pressure", cmap="viridis", clim=[-vabs, vabs], point_size=3, render_points_as_spheres=True)
    plotter.write_frame()
plotter.close()

