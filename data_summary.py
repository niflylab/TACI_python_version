import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys
import os

# Check if the user provided two CSV file paths
if len(sys.argv) != 3:
    print("Usage: python script.py <neuron_response_csv> <temperature_csv> ")
    sys.exit(1)

# Get the file paths from the command line arguments
temp_csv = sys.argv[2]
neuron_csv = sys.argv[1]

# Extract the folder path from the provided file path
folder_path = os.path.dirname(temp_csv)

# Verify if the provided files exist
try:
    df_temp = pd.read_csv(temp_csv)
    df_neuron = pd.read_csv(neuron_csv)
except FileNotFoundError:
    print(f"Error: One or both files do not exist.")
    sys.exit(1)

# Check if the CSV files have a 'Time' or 'Time(s)' column
if 'Time' in df_temp.columns:
    time_temp = df_temp['Time']
elif 'Time(s)' in df_temp.columns:
    time_temp = df_temp['Time(s)']
else:
    print(f"Error: The temperature file must have a 'Time' or 'Time(s)' column.")
    sys.exit(1)

if 'Time' in df_neuron.columns:
    time_neuron = df_neuron['Time']
elif 'Time(s)' in df_neuron.columns:
    time_neuron = df_neuron['Time(s)']
else:
    print(f"Error: The neuron response file must have a 'Time' or 'Time(s)' column.")
    sys.exit(1)

# Calculate mean and SEM for temperature data
mean_temp = df_temp.iloc[:, 1:].mean(axis=1)
sem_temp = df_temp.iloc[:, 1:].sem(axis=1)

# Calculate mean and SEM for neuron response data
mean_neuron = df_neuron.iloc[:, 1:].mean(axis=1)
sem_neuron = df_neuron.iloc[:, 1:].sem(axis=1)

# Increase all font sizes
plt.rcParams.update({'font.size': 16})




# Create a figure with two subplots stacked vertically sharing the x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 4), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

# Plot neuron response data (Top Plot)
ax1.errorbar(time_neuron, mean_neuron, yerr=sem_neuron,
             fmt='-o', color='black', ecolor='lightgray', markersize=2,
             capsize=0, label='Mean', linewidth=2)
#ax1.fill_between(time_neuron, mean_neuron - sem_neuron, mean_neuron + sem_neuron,
#                 color='gray', alpha=0.5, label='SEM')
ax1.set_ylabel(r'$\Delta F/F_{min}$')
#ax1.set_ylim(0, 4.5)
ax1.grid(False)



# Remove x-axis labels from the top plot
ax1.tick_params(axis='x', which='both', bottom=False, labelbottom=False)

# Plot temperature data (Bottom Plot)
ax2.errorbar(time_temp, mean_temp, yerr=sem_temp, fmt='-o',
             color='black', ecolor='lightgray', markersize=2,
             capsize=0, label='Temperature (°C)', linewidth=2)
#ax2.fill_between(time_temp, mean_temp - sem_temp, mean_temp + sem_temp,
#                 color='black', alpha=0.5)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Temperature (°C)")
ax2.set_ylim(10, 30)


# Set custom x-axis ticks only on the bottom plot
ax2.set_xticks([30, 60, 90, 120, 150, 180, 210])

# Manually Set X-Axis Range
ax1.set_xlim(0, 210)
ax2.set_xlim(0, 210)

plt.tight_layout()

# Save the plot to the extracted folder path
output_path = os.path.join(folder_path, 'combined_gradient_plot.png')
plt.savefig(output_path, dpi=300)
plt.show()

print(f"Plot saved as {output_path}")
