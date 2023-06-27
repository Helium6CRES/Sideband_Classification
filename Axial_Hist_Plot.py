"""
File takes a path to a CSV outputted by Sideband_Classification and displays a
grid of histograms for the axial frequencies of each field in the data.
"""

import matplotlib.pyplot as plt
import pandas as pd

# Input and sort data
data_path = input("Input sideband-processed data path: ")
datafile = open(data_path)
df = pd.read_csv(datafile, sep=',')
fields = sorted(df["set_field"].unique())

fig, axs = plt.subplots(3, 4, figsize=(10, 10))

axs = axs.flatten()

# Create histograms for each field
for i in range(len(fields)):
    field = fields[i]
    data = df[df["set_field"] == field]
    axs[i].hist(data["Axial_Frequency"], bins=75)
    axs[i].set_xlim(4e7, 5e8)
    axs[i].set_ylim(0, 150)
    axs[i].set_title(str(field) + " T")
    axs[i].set_ylabel("Count")
    axs[i].set_xlabel("Hz")

fig.suptitle("Axial Frequency Distributions by Field")
plt.tight_layout()
plt.show()
