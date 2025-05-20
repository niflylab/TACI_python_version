#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Calcium Imaging Analysis Script.

This script conducts Calcium Imaging analyses such as fluorescence extraction and plotting.
It supports two types of cells:
    1. DOCC - Uses `individual_dFoverF0_1.py` for analysis. F0=F0(first time point)
    2. DOWC - Uses `individual_dFoverF0_DOWC.py` for analysis. F0=Fmin(the lowest fluorescence in first 120 min)

Functions:
    - loop_fluorescence_extract(): For DOCC analysis.
    - loop_fluorescence_extract_DOWC(): For DOWC analysis.
    - merge_data(): Combines results and generates summary plots.
    - generate_background(): Generates Background_list.csv from background_i.xlsx.

Usage:
    python CIAnalysis_120min.py -i <project_dir> [-t <number of position t>] [-b <background_file>] [--merge] [--cell_type DOCC/DOWC] [--help]

@author: Hua Bai Ni-Lab
"""

import os
import sys
import argparse
from utility import parse_file
from individual_dFoverF0_1 import loop_fluorescence_extract  # For DOCC cells
from individual_dFoverF0_DOWC import loop_fluorescence_extract_DOWC  # For DOWC cells
from merge_dFoverF0_1 import merge_data  # For merging results
from Generate_background import generate_background  # For generating background list

def main():
    # Default project directory as the current script path
    project_dir = os.getcwd()

    # Initialize argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--project_dir', type=str, required=False, help='Project directory to do analysis')
    parser.add_argument('-t', '--position_t', type=int, required=False, default=100, help='Number of position t')
    parser.add_argument('-r', '--merge', type=int, required=False, help='Merge extracted data', nargs='?', const=1)
    parser.add_argument('--cell_type', type=str, required=True, choices=['DOCC', 'DOWC'],
                        help="Specify the cell type: DOCC or DOWC")

    args = parser.parse_args()

    # Prompt user if project directory is not specified in command-line arguments
    if args.project_dir is None:
        print("Project directory is not specified. Use the current directory? (y/n): ")
        choice = input().lower()
        if choice not in ("y", "yes", ""):
            parser.print_help()
            print("Please type the project directory, then press ENTER...")
            project_dir = input().strip()
    else:
        project_dir = args.project_dir.strip()

    # Define paths
    analysis_dir = os.path.join(project_dir)
    results_dir = os.path.join(analysis_dir, "results")
    background_file = os.path.join(analysis_dir, "Background_list.csv")
    background_input_file = os.path.join(analysis_dir, "background_i.xlsx")

    # Generate Background_list.csv if it doesn't exist
    if not os.path.exists(background_file):
        if os.path.exists(background_input_file):
            print(f"Generating Background_list.csv from {background_input_file}...")
            try:
                generate_background(background_input_file)
                print(f"Background_list.csv has been successfully generated at {background_file}.")
            except Exception as e:
                print(f"Error generating Background_list.csv: {e}")
                sys.exit(1)
        else:
            print(f"Background_list.csv and {background_input_file} are missing. Please provide the required file.")
            sys.exit(1)

    # Ensure results directory exists
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    print(f"""
Running CIAnalysis with settings:
    --Project Folder: {project_dir}
    --Position t: {args.position_t}
    --Background List: {background_file}
    --Merge Results: {str(args.merge)}
    --Cell Type: {args.cell_type}
    """)

    # Step 1: Execute fluorescence extraction based on cell type
    if args.position_t is not None:
        number_of_position_t = int(args.position_t)
        print(f"Processing fluorescence extraction for {args.cell_type}...")

        if args.cell_type == "DOCC":
            # Use loop_fluorescence_extract for DOCC analysis
            loop_fluorescence_extract(analysis_dir, background_file, number_of_position_t, results_dir)
        elif args.cell_type == "DOWC":
            # Use loop_fluorescence_extract_DOWC for DOWC analysis
            loop_fluorescence_extract_DOWC(analysis_dir, background_file, number_of_position_t, results_dir)

    # Step 2: Merge data if specified
    if args.merge is not None:
        # Check for fluorescence extraction results
        if not os.path.exists(results_dir) or not os.listdir(results_dir):
            print("Fluorescence extraction results are not found.")
            sys.exit()
        else:
            print("Merging data...")
            merge_data(results_dir, args.position_t, "Average ΔF/F0")

if __name__ == "__main__":
    main()
