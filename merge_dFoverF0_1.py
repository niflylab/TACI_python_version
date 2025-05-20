#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 17:29:34 2021
The function performs the following:
    1)	Combines all the ∆F/F0 values for each neuron in the folder into one file. 
        This requires specific file structure as an input. Refer to the README file.
    2)	Calculates the average and SEM of ∆F/F0 and plots the average ∆F/F0 over time.
    3)	Outputs merged_data.csv and Average_dF_Fo.png into a merged_data folder within the results folder. 

@author: alisasmacbook
"""

import os # Handles directory creation and file manipulation
import pandas as pd # For data manipulation and reading/writing CSV files.
import numpy as np # Provides numerical operations (e.g., creating arrays).
import matplotlib.pyplot as plt # Used for creating plots.
from matplotlib.ticker import MaxNLocator # Ensures x-axis labels are integers.

# defines a function <merge_data> that :
# takes in three parameters:
# 1) results_folder: Path to the folder containing input CSV files.
# 2) position_t: Number of time points to process (default is 999).
# 3) plot_title: Title for the generated plot.

def merge_data(results_folder, position_t=999, plot_title = 'Average \u0394F/F0'):
    
    try:
        os.mkdir(f"{results_folder}/merged_data") # Creates a subdirectory named merged_data within results_folder to store output files.

    except:
        pass # Ignores errors if the directory already exists.
    
    # Position T Array Initialization
    position_t_column = np.arange(0,position_t) # Creates an array of integers from 0 to position_t - 1 (representing time points).
    position_t_array = pd.DataFrame(position_t_column, columns = ['POSITION_T']) # Converts the array into a DataFrame with a column named POSITION_T.

    # Defines paths for the output files:
    output_file_path = f"{results_folder}/merged_data/merged_data.csv" # merged_data.csv: The final merged file.
    POSITION_T_path = f"{results_folder}/merged_data/position_t.csv" # position_t.csv: Temporary file for the POSITION_T column.
    position_t_array.to_csv(POSITION_T_path, index=False) # Writes the POSITION_T DataFrame to position_t.csv.

    # Loops through csv files
    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"): #Loops through all files in results_folder and processes only .csv files.
            # Processing Each CSV
            POSITION_T = pd.read_csv(POSITION_T_path) # Reads the POSITION_T file into a DataFrame.
            data = f"{results_folder}/{filename}" # Constructs the path to the current CSV file.
            column_name = os.path.splitext(filename)[0] # Extracts the filename (without extension) to use as the column name.

            df = pd.read_csv(data, usecols=['dF/F0','POSITION_T']) # Reads the dF/F0 and POSITION_T columns from the current file.
            df.rename(columns = {"dF/F0": column_name}, inplace = True) # Renames the dF/F0 column to the filename for identification.

            joined = POSITION_T.merge(df, on = "POSITION_T", how='left') # Merges the current file's data with the POSITION_T column
            joined.to_csv(POSITION_T_path,index=False, na_rep = "") # Updates the temporary POSITION_T_path file with the new merged data

    # Final Merge and Calculations
    merged_data = pd.read_csv(POSITION_T_path, na_values = '')
    average_data = merged_data.drop('POSITION_T', axis=1) # Drops the POSITION_T column to calculate:
    average_column = average_data.mean(axis=1) # average_column: Mean of dF/F0 across all files for each time point.
    sem_column = average_data.sem(axis=1) # sem_column: Standard error of the mean for dF/F0.

    # Sorts columns alphabetically and reorders them to place POSITION_T as the first column.
    merged_data_sort = merged_data.reindex(sorted(merged_data.columns), axis=1)
    cols = list(merged_data_sort.columns)
    cols = [cols[-1]] + cols[:-1]
    merged_data = merged_data_sort[cols]

    # Writes the merged data to merged_data.csv.
    merged_data.to_csv(output_file_path,index=False, na_rep = "")

    # Add Average and SEM
    merged_data_2 = pd.read_csv(output_file_path) # Reads merged_data.csv back into a DataFrame.
    merged_data_2['Average'] = average_column # Adds columns for Average and SEM.
    merged_data_2['SEM'] = sem_column #Adds columns for Average and SEM.

    merged_data_2.to_csv(output_file_path, index=False, na_rep="") # Saves the updated file back to merged_data.csv.

    # Deletes the temporary position_t.csv.
    os.remove(POSITION_T_path)

    # Plot the Results
    # Creates a line plot of Average versus POSITION_T with error bars for SEM.
    merged_plot = merged_data_2.plot.line(x="POSITION_T", y="Average", yerr="SEM", legend=False, title=plot_title)
    merged_plot.set_xlabel("Position T")
    merged_plot.set_ylabel("\u0394F/F0")
    merged_plot.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(f"{results_folder}/merged_data/Average_dF_F0.png", bbox_inches="tight") #Saves the plot as Average_dF_F0.png in the merged_data folder.
