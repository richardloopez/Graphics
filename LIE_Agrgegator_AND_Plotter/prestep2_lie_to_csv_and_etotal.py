#!/usr/bin/env python3

# Author: Richard Lopez Corbalan
# GitHub: github.com/richardloopez
# Citation: If you use this code, please cite Lopez-Corbalan, R.

import pandas as pd
import glob
import os
import csv
from statistics import mean, stdev

def process_lie_files(folder_path="."):
    """
    1. Finds LIE files (.dat), calculates the total energy (EELEC + EVDW),
       and saves the result to a new CSV file.
    2. Calls the function to filter and analyze the newly created CSVs.

    Args:
        folder_path (str): The path to the folder containing the files.
                           Defaults to the current folder (.).
    """

    # --- PART 1: DAT to CSV Conversion and ETOTAL Calculation ---

    print("--- Part 1: Converting .dat to .csv and calculating [ETOTAL] ---")

    # Find all files ending in .dat in the folder
    search_pattern_dat = os.path.join(folder_path, "*.dat")
    lie_files = glob.glob(search_pattern_dat)

    if not lie_files:
        print(f"?? No LIE files (.dat) found in the folder: {folder_path}")
        # Proceed to check for existing CSVs if no DATs are found
    else:
        print(f"? Found {len(lie_files)} LIE files to process.")

        for lie_file in lie_files:
            print(f"\nProcessing file: {os.path.basename(lie_file)}...")

            try:
                # Define column names based on the file format
                lie_columns = ['Frame', 'EELEC_val', 'EVDW_val']

                # Read the file, skipping the header line (#Frame...)
                # 'sep=r"\s+"' handles multiple spaces as separator.
                df = pd.read_csv(
                    lie_file,
                    sep=r"\s+",
                    skiprows=1,
                    names=lie_columns,
                    index_col=False,
                    engine='python'
                )

                # Rename columns to their full Amber names for clarity (assuming they are columns 2 and 3)
                df.rename(columns={'EELEC_val': 'LIE_00001[EELEC]', 'EVDW_val': 'LIE_00001[EVDW]'}, inplace=True)

                # Convert columns to numeric (coercing errors) and calculate Total Energy
                df['LIE_00001[EELEC]'] = pd.to_numeric(df['LIE_00001[EELEC]'], errors='coerce')
                df['LIE_00001[EVDW]'] = pd.to_numeric(df['LIE_00001[EVDW]'], errors='coerce')

                # Add the [ETOTAL] column
                df['[ETOTAL]'] = df['LIE_00001[EELEC]'] + df['LIE_00001[EVDW]']

                # Generate the new CSV file name
                base_name = os.path.splitext(lie_file)[0]  # Removes original extension
                csv_file = base_name + ".csv"

                # Save the DataFrame to a CSV file
                df.to_csv(csv_file, index=False)
                print(f"File successfully saved as: {os.path.basename(csv_file)}")

            except Exception as e:
                print(f"? An error occurred while processing {os.path.basename(lie_file)}: {e}")
                continue

    # --- PART 2: Filtering, Analysis, and Header Insertion ---

    print("\n--- Part 2: Filtering, Analyzing, and Inserting Statistics ---")
    analyze_filtered_csvs(folder_path)
    
    print("\n? Process completed.")


def analyze_filtered_csvs(folder_path="."):
    """
    Filters CSV files by keywords in the name, calculates mean/std for energy
    columns, and inserts these results at the top of the CSV file.

    Args:
        folder_path (str): The path to the folder containing the files.
    """
    
    # 1. Define the list of variables (keywords) for similarity filtering
    # MODIFY THIS LIST WITH YOUR REQUIRED KEYWORDS
    keywords_similitude = ["DOCK","LIG"]
    print(f"Searching for CSV files containing ALL these keywords: {keywords_similitude}")
    print("-" * 50)

    # Find all files ending in .csv in the folder
    search_pattern_csv = os.path.join(folder_path, "*.csv")
    csv_files = glob.glob(search_pattern_csv)

    if not csv_files:
        print(f"?? No CSV files found in the folder: {folder_path}")
        return

    filtered_files = []
    
    # 2. Filter CSV files by name
    for csv_file in csv_files:
        file_name = os.path.basename(csv_file)
        
        # Check if ALL keywords are present in the filename (case-insensitive)
        if all(keyword.lower() in file_name.lower() for keyword in keywords_similitude):
            filtered_files.append(csv_file)
            print(f"? Found and marked: {file_name}")
    
    print("-" * 50)
    if not filtered_files:
        print("? No files met the similarity condition.")
        return

    print(f"Processing {len(filtered_files)} filtered files.")


    # 3. to 7. Process filtered files, calculate stats, and insert header
    for csv_file in filtered_files:
        file_name = os.path.basename(csv_file)
        print(f"Calculating statistics for: {file_name}")

        try:
            # Load the DataFrame
            df = pd.read_csv(csv_file)

            # Columns for analysis
            cols_analysis = {
                'LIE_00001[EELEC]': '[EELEC]',
                'LIE_00001[EVDW]': '[EVDW]',
                '[ETOTAL]': '[ETOTAL]'
            }
            
            # List to store results for insertion
            results = []
            
            for df_col, short_name in cols_analysis.items():
                if df_col in df.columns:
                    # Calculate mean and standard deviation
                    mean_val = df[df_col].mean()
                    std_val = df[df_col].std()
                    
                    # Store results in a simplified list format
                    results.append([
                        f"{short_name} Mean", f"{mean_val:.4f}"
                    ])
                    results.append([
                        f"{short_name} Std", f"{std_val:.4f}"
                    ])
                else:
                    print(f"   Warning: Column '{df_col}' not found in the file. Skipping stats for it.")

            
            # 7. Insert results at the very top of the document
            if results:
                temp_file = csv_file + ".tmp"
                
                # Create the new header structure
                header_lines = [
                    ["# LIE STATISTICS - " + file_name],
                    ["#--------------------------------------"],
                ]
                
                # Consolidate all statistics into a single metadata line
                metadata_line = ["# METADATA:"]
                for label, value in results:
                    metadata_line.append(f"{label.replace(':', '')} = {value}")
                
                header_lines.append(metadata_line)
                header_lines.append(["#--------------------------------------"])
                
                
                # Open the temp file for writing and the original for reading
                with open(csv_file, 'r', newline='') as infile, \
                     open(temp_file, 'w', newline='') as outfile:
                    
                    # Use the csv module for safe reading/writing
                    reader = csv.reader(infile)
                    writer = csv.writer(outfile)
                    
                    # Write the new statistics header
                    for row in header_lines:
                        writer.writerow(row)

                    # Copy the original content (including the original header row)
                    for row in reader:
                        writer.writerow(row)

                # Replace the original file with the temporary one
                os.replace(temp_file, csv_file)
                print(f"   ? Statistics inserted at the beginning of: {file_name}")

        except Exception as e:
            print(f"   ? An error occurred while processing {file_name}: {e}")
            continue

# --- Script Execution ---

# ?? INSTRUCTION: Change the argument if your files are in a different folder.
process_lie_files()
