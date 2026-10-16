#!/usr/bin/env python3
import pandas as pd
import argparse
import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
        prog="snaphot visualiser",
        description="Small script to run and visualise SEM proxy via snaphots"
        )

parser.add_argument("-s", "--sem_options", type=str, default="")
parser.add_argument("-f", "--sismos_folder", type=str, default="./sismos")
parser.add_argument("-p", "--sismos_pos_file", type=str, default="./sismos.csv")
parser.add_argument("-i", "--sismos_interval", type=int, default=1)
parser.add_argument("--run", action=argparse.BooleanOptionalAction)

args = parser.parse_args()

if args.run:
    args_passed_to_sem = args.sem_options + f" --sismos-pos-file {args.sismos_pos_file} --sismos-save-folder {args.sismos_folder} --sismos-save-interval {args.sismos_interval}"

    # If the folder dir doesn't exists, create it
    if not os.path.exists(args.sismos_folder):
        os.mkdir(args.sismos_folder)

    # run the simulation
    subprocess.run(f"./build/bin/semproxy {args_passed_to_sem}", shell=True)

files = [e.path for e in os.scandir(args.sismos_folder)]
measurements = {}

for f in files:
    df = pd.read_csv(f)
    time = int(f.split("_")[1].split(".")[0])
    for i, row in df.iterrows():
        name = f"({float(row['x'])},{float(row['y'])},{float(row['z'])})"
        if measurements.get(name, None) is None:
            measurements[name] = ([float(time)], [float(row["pressure"])])
        else:
            measurements[name][0].append(float(row["pressure"]))
            measurements[name][1].append(float(time))

for k, v in measurements.items():
    sp = np.fft.fft(v[0])
    freq = np.fft.fftfreq(len(v[0]), args.sismos_interval)
    plt.plot(freq, sp.real, label=k)
    break
plt.legend()
plt.savefig("fft.png")
