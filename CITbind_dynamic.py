#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CITbind_dynamic.py updated 01212025

This script processes a specified folder containing two CSV files:
    - One starting with 'Analog'
    - Another named 'merged_data.csv'

It renames these files based on the folder name and combines the temperature data
with calcium imaging results to generate a plot. The number of neurons to process
must be specified by the user.

Usage:
    python CITbind_dynamic.py -i <sample_folder> -n <number_of_neurons>

Parameters:
    -i / --input_folder: Folder containing the sample data files.
    -n / --neurons: Number of neurons to process.

Input Files in the Sample Folder:
    1. merged_data.csv
    2. Analog*.csv

Outputs:
    1. Renamed Files:
        - <folder_name>.csv
        - <folder_name>-temp.csv
    2. Combined CSV: <folder_name>-cbind.csv
    3. Combined Plot (PDF): <folder_name>-cbind.pdf
    4. Additional Plot (PDF): <folder_name>-cbind1.pdf (y-axis range set from -1 to 10)

Updated at Feb 26, 2025: Output one more figure with y-axis range from -1 to 10.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys

def rename_files_in_folder(folder_path):
    """Rename files in the folder based on folder name."""
    folder_name = os.path.basename(os.path.normpath(folder_path))

    analog_file_path = None
    merged_data_file_path = None

    for file_name in os.listdir(folder_path):
        if file_name.startswith('Analog') and file_name.endswith('.csv'):
            analog_file_path = os.path.join(folder_path, file_name)
        elif file_name == 'merged_data.csv':
            merged_data_file_path = os.path.join(folder_path, file_name)

    if analog_file_path and merged_data_file_path:
        new_merged_data_file_name = f"{folder_name}.csv"
        new_analog_file_name = f"{folder_name}-temp.csv"

        new_merged_data_file_path = os.path.join(folder_path, new_merged_data_file_name)
        new_analog_file_path = os.path.join(folder_path, new_analog_file_name)

        os.rename(merged_data_file_path, new_merged_data_file_path)
        os.rename(analog_file_path, new_analog_file_path)

        print(f"Renamed '{merged_data_file_path}' to '{new_merged_data_file_path}'")
        print(f"Renamed '{analog_file_path}' to '{new_analog_file_path}'")

        return new_merged_data_file_path, new_analog_file_path
    else:
        raise FileNotFoundError("Required files not found: 'Analog*.csv' and/or 'merged_data.csv'.")

def convert_time_to_seconds(time_str):
    """Convert time in format 'MM:SS.s' to total seconds."""
    minutes, seconds = time_str.split(':')
    return int(minutes) * 60 + float(seconds)

def combine_and_plot(folder_path, neuron_count):
    """Combine temperature and calcium imaging data and generate plots."""
    folder_name = os.path.basename(folder_path)

    # Rename files and get new file paths
    data_file, temp_file = rename_files_in_folder(folder_path)

    # Load data
    data_df = pd.read_csv(data_file, engine='python', skipfooter=12)
    temp_df = pd.read_csv(temp_file, skiprows=6)

    # Validate neuron count
    neuron_columns = data_df.columns[1:1 + neuron_count]
    if len(neuron_columns) < neuron_count:
        raise ValueError(f"Specified neuron count ({neuron_count}) exceeds available data columns.")

    print(f"Processing {len(neuron_columns)} neuron(s): {', '.join(neuron_columns)}")

    # Extract the last value in 'Sample' column from temp_df
    tmax = temp_df['Sample'].iloc[-1]

    # Create combined DataFrame
    cbind_df = pd.DataFrame()
    cbind_df['POSITION_T'] = data_df['POSITION_T']
    cbind_df['tt'] = (cbind_df['POSITION_T'] * tmax / data_df['POSITION_T'].max()).round().astype(int)
    cbind_df['Time (s)'] = cbind_df['tt'].apply(
        lambda x: temp_df[temp_df['Sample'] == x]['Time (s)'].values[0] if x in temp_df['Sample'].values else None)
    cbind_df['Time (s)'] = cbind_df['Time (s)'].apply(convert_time_to_seconds)
    cbind_df['Time (s)'] = cbind_df['Time (s)'].astype(int)
    cbind_df['Temperature(°C)'] = cbind_df['tt'].apply(
        lambda x: temp_df[temp_df['Sample'] == x]['AI0 (°C)'].values[0] if x in temp_df['Sample'].values else None)

    for col in neuron_columns:
        cbind_df[col] = data_df[col]

    # Save combined data to CSV
    output_csv = os.path.join(folder_path, f'{folder_name}-cbind.csv')
    cbind_df.to_csv(output_csv, index=False)
    print(f"Combined data saved to {output_csv}")

    # X-axis limit
    x_max = cbind_df['Time (s)'].max()
    x_ticks = [0, 30, 60, 90, 120, 150, 180, 210]

    # Generate both plots
    for idx, y_range in enumerate([None, (-1, 10)]):
        fig = plt.figure(figsize=(10, 6))
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        neuron_colors = ['red', 'blue', 'green', 'purple', 'orange']

        for i, col in enumerate(neuron_columns):
            color = neuron_colors[i % len(neuron_colors)]
            ax1.plot(cbind_df['Time (s)'], cbind_df[col], marker='o', color=color, label=col)
        ax1.axhline(y=0, color='black', linewidth=0.8)
        ax1.set_ylabel('ΔF/F0')
        ax1.legend(loc='upper right', frameon=False)

        ax2.plot(cbind_df['Time (s)'], cbind_df['Temperature(°C)'], marker='o', color='black', label='Temperature')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Temperature (°C)')
        ax2.legend(loc='upper right', frameon=False)

        ax2.set_ylim(10, 30)

        if y_range:
            ax1.set_ylim(y_range)

        ax1.set_xlim(0, x_max)
        ax2.set_xlim(0, x_max)

        ax1.set_xticks(x_ticks)
        ax2.set_xticks(x_ticks)

        for line_position in x_ticks:
            ax1.axvline(x=line_position, color='black', linestyle='--', linewidth=0.8)
            ax2.axvline(x=line_position, color='black', linestyle='--', linewidth=0.8)

        fig.suptitle(f"{folder_name}", fontsize=14)

        output_pdf = os.path.join(folder_path, f'{folder_name}-cbind{idx}.pdf')
        plt.savefig(output_pdf, format='pdf')
        print(f"Plot saved to {output_pdf}")

        plt.close()

def main():
    parser = argparse.ArgumentParser(description="Combine temperature and calcium imaging data.")
    parser.add_argument('-i', '--input_folder', type=str, required=True, help="Folder containing the sample data files.")
    parser.add_argument('-n', '--neurons', type=int, required=True, help="Number of neurons to process.")
    args = parser.parse_args()

    combine_and_plot(args.input_folder, args.neurons)

if __name__ == "__main__":
    main()
