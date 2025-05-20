#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script read background_i.xlsx, and generate a new file named Background_list.csv.
The final CSV file have each neuron's non-empty stack averages listed vertically .
Each neuron should be a column, and each row should correspond to the average of
the background data from a non-empty stack for that neuron.

Usage: python Generate_background.py /path/to/background_i.xlsx

@author: Hua Bai @ Ni-Lab
"""

import pandas as pd
import os
import sys


def generate_background(file_path):
    # Check if the Excel file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Check if the output CSV file already exists
    output_file_path = os.path.join(os.path.dirname(file_path), 'Background_list.csv')
    if os.path.exists(output_file_path):
        raise FileExistsError(f"The output file {output_file_path} already exists.")

    # Read the Excel file
    df = pd.read_excel(file_path, engine='openpyxl')

    # Calculate mean for each stack in each neuron, ignoring NaN values
    means = df.groupby('Neurons').mean()

    # Drop all stacks with no input
    non_empty_stacks = means.dropna(axis=1, how='all')

    # Transpose and reset index to start the stack means right under the neuron names
    transposed = non_empty_stacks.transpose().reset_index(drop=True)

    # Ensure that all data starts right under the column names, no empty cells
    transposed = transposed.apply(lambda x: pd.Series(x.dropna().values), axis=0).fillna('')

    # Generate the CSV file
    transposed.to_csv(output_file_path, index=False)

    return output_file_path


# Main function to execute script with command line argument
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_background.py /path/to/background_i.xlsx")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        output_file_path = generate_background(file_path)
        print(f"Background list has been generated successfully at {output_file_path}")
    except Exception as e:
        print(e)
        sys.exit(1)