#!/usr/bin/env python3
import pandas as pd
import numpy as np
import argparse
import subprocess
import os
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
        prog="snaphot visualiser",
        description="Small script to run and visualise SEM proxy via snaphots"
        )

parser.add_argument("-s", "--sem_options", type=str, default="")
parser.add_argument("-f", "--snapshot_folder", type=str, default="./snapshots")
parser.add_argument("-i", "--snapshot_interval", type=int, default=100)
parser.add_argument("-b", "--histogram_bar_sizes", type=float, default=0.1)
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

pressure_values = [list(pd.read_csv(f)["pressure"]) for f in files]
pressure_values_flattened = [x for l in pressure_values for x in l]

pressure_max = max(pressure_values_flattened)
pressure_min = min(pressure_values_flattened)
pressure_avg = np.mean(pressure_values_flattened)
pressure_std = np.std(pressure_values_flattened)

print(f"Pressure global statistics:\nMax: {pressure_max}\nMin: {pressure_min}\nAvg: {pressure_avg}\nStd: {pressure_std}")

plt.hist(pressure_values_flattened, bins=np.arange(pressure_min // args.histogram_bar_sizes * args.histogram_bar_sizes,(pressure_max // args.histogram_bar_sizes + 1) * args.histogram_bar_sizes, args.histogram_bar_sizes))
plt.savefig("hist.png")
