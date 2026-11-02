import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("./../histogram.csv")

count = df["count"][:100]
bin = df["bin"][:100]

plt.hist(bin, bins=bin, weights=count)
plt.savefig("histogram.png")

