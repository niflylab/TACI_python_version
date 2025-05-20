#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is designed to process and analyze fluorescence intensity data for DOWC neurons.

The fluorescence_extract_DOWC() function performs the following:
    1) Combines MEAN_INTENSITY values from the TrackMate output files for a single neuron.
    2) Subtracts the background fluorescence and finds the minimal fluorescence value during cooling
       (from POSITION_T 0 to 36) as F0.
    3) Calculates the change in fluorescence (∆F/F0) over time using the formula:
           ∆F/F0 = (F - F0) / F0
    4) Outputs a .csv file containing ∆F/F0 for each time point and a .png plot showing ∆F/F0 over time.

The loop_fluorescence_extract_DOWC() function batch-processes multiple neurons in a folder.

@author: Hua Bai
"""

import os  # Handles file and directory operations.
import shutil  # Manages high-level file operations, such as deleting directories.
import matplotlib.pyplot as plt  # For plotting graphs
import pandas as pd  # For handling tabular data (e.g., reading/writing CSV files)
import numpy as np  # For numerical operations (e.g., creating arrays, mathematical calculations)
from matplotlib.ticker import MaxNLocator  # Ensures x-axis labels are integers in plots.

# This function processes fluorescence data for one neuron
def fluorescence_extract_DOWC(working_dir,
                               results_folder="results",
                               trial_name="Neuron",
                               position_t=100,
                               background_averages=[1]):
    """
    Parameters:
        working_dir: Directory containing CSV files for a single neuron.
        results_folder: Folder to save processed results (default: "results").
        trial_name: Name for the output files (default: "Neuron").
        position_t: Number of time points (default: 100).
        background_averages: Background fluorescence values for subtraction (default: [1]).
    """
    # Step 1: Change to the working directory and create a temporary folder for intermediate files.
    os.chdir(working_dir)
    output_path = os.path.join(working_dir, 'python_files')
    if os.path.exists(output_path):
        shutil.rmtree(output_path)  # Clear the temporary folder if it already exists.
    os.mkdir('python_files')

    # Step 2: Create a DataFrame for POSITION_T (time points) and save it as a CSV file.
    position_t_column = np.arange(0, position_t)  # Create an array of integers from 0 to position_t-1.
    position_t_array = pd.DataFrame(position_t_column, columns=['POSITION_T'])  # Convert array to a DataFrame.
    POSITION_T_path = os.path.join(output_path, "POSITION_T.csv")
    position_t_array.to_csv(POSITION_T_path, index=False)

    # Step 3: Process input files (e.g., fluorescence intensity data from TrackMate output).
    for filename in os.listdir(working_dir):
        if filename.endswith(".csv") and not filename.startswith("~$"):  # Skip temporary files.
            try:
                # Read the POSITION_T and MEAN_INTENSITY_CH1 columns from the input file.
                df = pd.read_csv(filename, usecols=["POSITION_T", "MEAN_INTENSITY_CH1"])
                file_name = os.path.splitext(filename)[0]  # Extract the file name without extension.
                df.columns = ['POSITION_T', file_name]  # Rename columns for clarity.
                df.to_csv(f"python_files/{file_name}py.csv", index=False, na_rep='')
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

    # Step 4: Merge all processed files based on POSITION_T.
    for filename in os.listdir(output_path):
        if filename.endswith("py.csv"):
            try:
                POSITION_T = pd.read_csv(POSITION_T_path, na_values='')
                data = os.path.join(output_path, filename)
                df = pd.read_csv(data)
                joined = POSITION_T.merge(df, on="POSITION_T", how='left')  # Merge by POSITION_T.
                joined.to_csv(POSITION_T_path, index=False, na_rep='')
                os.remove(data)  # Clean up intermediate files after merging.
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

    # Step 5: Perform background subtraction.
    subtract_averages = pd.read_csv(POSITION_T_path, na_values='')
    subtract_averages_sort = subtract_averages.reindex(sorted(subtract_averages.columns), axis=1)  # Sort columns.
    cols = list(subtract_averages_sort.columns)
    cols = [cols[-1]] + cols[:-1]  # Move POSITION_T to the first column.
    subtract_averages = subtract_averages_sort[cols]

    Averages = [0] + background_averages  # Prepend 0 for POSITION_T column.
    subtract_averages = subtract_averages - Averages  # Subtract background averages.
    subtract_averages.to_csv(f"python_files/{trial_name}_subtracted_averages.csv", index=False, na_rep="")

    # Step 6: Compute ∆F/F0.
    max_value = subtract_averages.drop('POSITION_T', axis=1).max(axis=1)  # Find the max fluorescence for each time point.
    subtract_averages['max_value'] = max_value
    subtract_averages.to_csv(f"python_files/{trial_name}_max_value.csv", index=False, na_rep="")

    # Modified: Use the minimum fluorescence value in POSITION_T 0 to 50 as F0.
    min_region = subtract_averages[(subtract_averages['POSITION_T'] >= 0) & (subtract_averages['POSITION_T'] <= 50)]
    Fo = min_region['max_value'].min()  # Find the minimum value in this range.
    dF = (max_value - Fo) / Fo  # Calculate ∆F/F0.
    subtract_averages['dF/F0'] = dF

    # Step 7: Save results and plot ∆F/F0 over time.
    subtract_averages.to_csv(f"{results_folder}/{trial_name}.csv", index=False, na_rep="")
    average_plot = subtract_averages.plot.line(x="POSITION_T", y="dF/F0", legend=False, title=trial_name)
    average_plot.set_xlabel("Position T")
    average_plot.set_ylabel("\u0394F/F0")
    average_plot.xaxis.set_major_locator(MaxNLocator(integer=True))

    try:
        os.mkdir(f"{results_folder}/Neuron Plots")
    except:
        pass

    plt.savefig(f"{results_folder}/Neuron Plots/{trial_name}.png", bbox_inches="tight")


def loop_fluorescence_extract_DOWC(working_dir,
                                   background_file,
                                   number_of_position_t=100,
                                   result_folder="results"):
    """
    This function batch-processes data for multiple neurons.

    Parameters:
        working_dir: Directory containing folders for each neuron.
        background_file: Path to the background file containing averages.
        number_of_position_t: Number of time points for each dataset (default: 100).
        result_folder: Folder to save processed results (default: "results").
    """
    background_file = pd.read_csv(background_file, keep_default_na=False)
    number_of_neurons = len(background_file.columns)

    background_averages_list = []

    # Parse background averages for each neuron.
    for i in range(number_of_neurons):
        column_name = f"Neuron {i}"
        list1 = background_file.loc[~background_file[column_name].astype(str).str.isdigit(), column_name].tolist()
        list2 = []
        for x in list1:
            try:
                list2.append(float(x))
            except:
                pass
        background_averages_list.append(list2)

    # Process each neuron's data using fluorescence_extract_DOWC.
    for i in range(number_of_neurons):
        fluorescence_extract_DOWC(f'{working_dir}/Neuron {i}',
                                  trial_name=f"Neuron {i}",
                                  position_t=number_of_position_t,
                                  background_averages=background_averages_list[i],
                                  results_folder=result_folder)
