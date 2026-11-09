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
parser.add_argument("-f", "--snapshot_folder", type=str, default=".")
parser.add_argument("-i", "--snapshot_interval", type=int, default=100)
parser.add_argument("-b", "--histogram_bar_sizes", type=float, default=0.1)
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

pressure_values = [list(df["pressure"])]
pressure_values_flattened = [x for l in pressure_values for x in l]

pressure_max = max(pressure_values_flattened)
pressure_min = min(pressure_values_flattened)
pressure_avg = np.mean(pressure_values_flattened)
pressure_std = np.std(pressure_values_flattened)

print(f"Pressure global statistics:\nMax: {pressure_max}\nMin: {pressure_min}\nAvg: {pressure_avg}\nStd: {pressure_std}")

plt.hist(pressure_values_flattened, bins=np.arange(pressure_min // args.histogram_bar_sizes * args.histogram_bar_sizes,(pressure_max // args.histogram_bar_sizes + 1) * args.histogram_bar_sizes, args.histogram_bar_sizes))
plt.savefig("hist.png")
