#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The fluorescence_extract() function performs the following:
    1)	Combines MEAN_INTENSITY values from the Spots Statistics TrackMate output files for a single neuron.
    2)	Subtracts the background, finds the maximal value for each timepoint 
    3)	Calculates the change in fluorescence (∆F/F0) over time and plots the ∆F/F0.
    4)	Outputs a .csv with the ∆F/F0 for each time point and the plot of the 
        ∆F/F0 over time as a .png in a separate “Neuron Plots” folder within the results folder.

The loop_fluorescence_extract() function performs the following:
    1)	Runs fluorescence_extract() on all the neurons in a folder. This requires specific file structure as an input. Refer to the README file
    2)	Outputs 2 files for each neuron into the set results folder: the .csv with the ∆F/F0 for each time point  
        and the plot of the ∆F/F0 over time as a .png in a separate “Neuron Plots” folder within the results folder


@author: alisasmacbook,
updated by Hua Bai at March 14 2024, adding more error messages
"""

import os # Handles file and directory operations.
import shutil # Manages high-level file operations, such as deleting directories.
import matplotlib.pyplot as plt # For plotting graphs
import pandas as pd # For handling tabular data (e.g., reading/writing CSV files)
import numpy as np # For numerical operations (e.g., creating arrays, mathematical calculations).
from matplotlib.ticker import MaxNLocator #  Ensures that x-axis labels are integers in plots.

# define function fluorescence_extract
# Processes fluorescence data for one neuron.
# Takes several arguments:
# working_dir: Directory containing CSV files.
# results_folder: Folder to save results (default: "results").
# trial_name: Name of the neuron or experiment (default: "Neuron").
# position_t: Number of time points (default: 100).
# background_averages: Background fluorescence values for subtraction (default: [1]).
def fluorescence_extract(working_dir,
                        results_folder = "results", 
                        trial_name = "Neuron", 
                        position_t=100, 
                        background_averages=[1]):

    # Change working directory to working_dir
    # Remove and recreate a temporary directory (python_files) to store intermediate results.
    os.chdir(working_dir)
    output_path = os.path.join(working_dir, 'python_files')
    
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    os.mkdir('python_files')

    # create a POSITION_T Column
    position_t_column = np.arange(0,position_t) # Generate an array from 0 to position_t-1 to represent time points
    position_t_array = pd.DataFrame(position_t_column, columns=['POSITION_T']) # Convert the array into a DataFrame (position_t_array) with the column name POSITION_T.
    
    POSITION_T_path = os.path.join(output_path, "POSITION_T.csv") # Save this DataFrame to a CSV file (POSITION_T.csv) in the temporary directory.
    position_t_array.to_csv(POSITION_T_path, index=False)


    # Process input files.
    # Loop through files in working_dir:
    # Process only .csv files that don’t start with ~$ (avoids temporary files).
    # Extract relevant columns (POSITION_T and MEAN_INTENSITY_CH1) from each file.
    # Rename columns for clarity (MEAN_INTENSITY_CH1 → filename).
    # Save processed data to a temporary file in python_files.

    for filename in os.listdir(working_dir):
        if filename.endswith(".csv") and not filename.startswith("~$"):
            try:
                df = pd.read_csv(filename, usecols=(["POSITION_T","MEAN_INTENSITY_CH1"]))
                file_name = os.path.splitext(filename)[0]
                df.columns = ['POSITION_T', file_name]
                df.to_csv(f"python_files/{file_name}py.csv", index=False, na_rep='')
            except Exception as e:
                print(f"Error processing file {full_file_path}: {e}")
                continue

    # Merge Data by POSITION_T
    # Merge files:
    # Start with POSITION_T.csv as the base.
    # Sequentially merge each py.csv file, aligning by POSITION_T.
    # Save the merged result back to POSITION_T.csv and delete the temporary file.
    for filename in os.listdir(output_path):
        if filename.endswith("py.csv"):
            try:
                POSITION_T = pd.read_csv(POSITION_T_path, na_values='')
                data = os.path.join(output_path, filename)
                df = pd.read_csv(data)
                joined = POSITION_T.merge(df, on = "POSITION_T", how='left')
                joined.to_csv(POSITION_T_path,index=False, na_rep='')
                os.remove(data)
            except Exception as e:
                print(f"Error processing file {full_file_path}: {e}")
                continue

    # Background Subtraction
    # Read the merged data and sort columns alphabetically.
    # Adjust column order to place POSITION_T first.
    # Perform background subtraction using background_averages.
    subtract_averages = pd.read_csv(POSITION_T_path, na_values='')
    subtract_averages_sort = subtract_averages.reindex(sorted(subtract_averages.columns), axis=1)
    cols = list(subtract_averages_sort.columns)
    cols = [cols[-1]] + cols[:-1] # move the last column 'position_T' to the first
    subtract_averages = subtract_averages_sort[cols]
    Averages = [0]
    for i in background_averages:
        Averages.append(i)

    subtract_averages = subtract_averages - Averages
    subtract_averages.to_csv(f"python_files/{trial_name}_subtracted_averages.csv", index=False, na_rep="")

    # Compute Δ𝐹/F0
    # Find the maximum fluorescence intensity for each time point.
    # Compute baseline fluorescence (F0) as the first value of max_value
    # Calculate Δ𝐹/F0 using the formula and add it to the DataFrame.
    max_value = subtract_averages.drop('POSITION_T', axis=1)
    max_value = max_value.max(axis=1)
    subtract_averages['max_value'] = max_value
    subtract_averages.to_csv(f"python_files/{trial_name}_max_value.csv", index=False, na_rep="")
    
    first_neuron_POSITION_T = subtract_averages['max_value'].first_valid_index()
    Fo = max_value[first_neuron_POSITION_T]
    dF = (max_value-Fo)/Fo
    subtract_averages['dF/F0'] = dF
    file_name = os.path.splitext(filename)[0]

    # Save results and generate plot
    # Save the final processed data and plot Δ𝐹/F0 vs POSITION_T
    subtract_averages.to_csv(f"python_files/{trial_name}_dF_F0.csv", index=False, na_rep="")

    if results_folder == "results":
        new_path = os.path.dirname(working_dir)
        try:
            os.mkdir(f"{new_path}/{results_folder}")
        except:
            pass
        results_folder = f"{new_path}/{results_folder}"
        
    else:
        
        try:
            os.mkdir(results_folder)
            print("Created: " + results_folder)
        except:
            print('Results folder exists')
        
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


# Function: loop_fluorescence_extract
# Batch processes data for multiple neurons by calling fluorescence_extract
def loop_fluorescence_extract(working_dir, 
                              background_file, 
                              number_of_position_t=100,
                              result_folder="results",
                              ):
    # Background Data Processing
    # Reads a background file containing baseline values for each neuron.
    # Constructs a list of background averages for each neuron.
    background_file = pd.read_csv(background_file, keep_default_na=False)
    number_of_neurons = len(background_file.columns)
    
    background_averages_list = []
    
    for i in range(0,number_of_neurons):
        column_name = f"Neuron {i}"
        list1 = background_file.loc[~background_file[column_name].astype(str).str.isdigit(), column_name].tolist()
        list2 = []
        for x in list1:
            try:
                float_list = float(x)
                list2.append(float_list)
            except:
                pass
        background_averages_list.append(list2)

    # Call fluorescence_extract for Each Neuron
    # Iterates over neurons, calling fluorescence_extract for each neuron’s directory and background values.
    for i in range(0, number_of_neurons):
        fluorescence_extract(f'{working_dir}/Neuron {i}',
                             trial_name=f"Neuron {i}",
                             position_t=number_of_position_t,
                             background_averages=background_averages_list[i],
                             results_folder=result_folder )
