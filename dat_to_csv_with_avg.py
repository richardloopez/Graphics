#!/usr/bin/env python3

import pandas as pd
import glob
import os

def process_lie_files(folder_path="."):
    search_pattern_dat = os.path.join(folder_path, "*.dat")
    lie_files = glob.glob(search_pattern_dat)

    if not lie_files:
        print(f"No .dat files found in: {folder_path}")
        return

    print(f"Found {len(lie_files)} .dat files to process.\n")

    all_averages = []

    for lie_file in sorted(lie_files):
        base_name = os.path.splitext(os.path.basename(lie_file))[0]
        print(f"Processing: {os.path.basename(lie_file)}...")

        lie_columns = ['Frame', 'LIE_00001[EELEC]', 'LIE_00001[EVDW]']

        df = pd.read_csv(lie_file, sep=r"\s+", skiprows=1, names=lie_columns, engine='python')
        df['LIE_00001[EELEC]'] = pd.to_numeric(df['LIE_00001[EELEC]'], errors='coerce')
        df['LIE_00001[EVDW]'] = pd.to_numeric(df['LIE_00001[EVDW]'], errors='coerce')
        df['[ETOTAL]'] = df['LIE_00001[EELEC]'] + df['LIE_00001[EVDW]']

        csv_file = os.path.join(folder_path, base_name + ".csv")
        df.to_csv(csv_file, index=False)
        print(f"  -> Saved: {os.path.basename(csv_file)}")

        averages = {}
        for col in df.columns:
            avg = df[col].mean()
            averages[col] = f"{avg:.4f}"
        averages['File'] = base_name
        all_averages.append(averages)

    if all_averages:
        avg_df = pd.DataFrame(all_averages)
        cols = ['File'] + [c for c in avg_df.columns if c != 'File']
        avg_df = avg_df[cols]
        avg_file = os.path.join(folder_path, "column_averages.csv")
        avg_df.to_csv(avg_file, index=False)
        print(f"\nColumn averages saved to: {os.path.basename(avg_file)}")
        print("\nSummary of averages:")
        print(avg_df.to_string(index=False))

    print("\nDone.")

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    process_lie_files(folder)
