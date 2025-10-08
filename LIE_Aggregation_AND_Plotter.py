import pandas as pd
import glob
import os
import csv
import re
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt # Import for plotting

# ==============================================================================
# 0. GLOBAL CONFIGURATION (ENGLISH LABELS)
# ==============================================================================

# Define the ligands used in the study for coloring and legend
LIGANDS = ['Fe', 'Ga'] 

# Define which metrics (columns) should be plotted from the aggregated data.
# Options: '[EELEC]', '[EVDW]', '[ETOTAL]'
METRICS_TO_PLOT = ['[EELEC]', '[EVDW]'] 

# 1. VARIABLE PARA RANGO DEL EJE Y (Y-AXIS RANGE VARIABLE)
# Define el rango [min, max] para el eje Y (Energy). 
# Ejemplos: [-100, 0] para limitar. Usa None o un array vacío para que Matplotlib lo determine automáticamente.
Y_LIMITS = None 

# Plot styling and labels
PLOT_TITLE = "Electrostatic (EELEC) & Van der Waals (EVDW) Energy Analysis"
Y_AXIS_LABEL = "Energy (kcal/mol)"
# Bar colors (Fe metrics will be orangish, Ga metrics will be blueish)
COLORS = {
    'Fe[EELEC]': '#ff7f0e', # Dark Orange
    'Fe[EVDW]': '#ffbb78', # Light Orange
    'Ga[EELEC]': '#1f77b4', # Dark Blue
    'Ga[EVDW]':  '#aec7e8', # Light Blue
    'Fe[ETOTAL]': '#98df8a', # Light Green (if used)
    'Ga[ETOTAL]': '#2ca02c', # Dark Green (if used)
}

# ==============================================================================
# I. AGGREGATION PHASE FUNCTIONS
# ==============================================================================

def get_descriptive_name(config: Dict[str, List[Any]]) -> str:
    """
    Generates a descriptive filename based on AND, OR, and NOT search terms.
    """
    parts = []
    if config['AND']:
        parts.append("AND-" + "_".join(config['AND']))
    
    if config['OR_GROUPS']:
        or_names = []
        for i, group in enumerate(config['OR_GROUPS']):
            group_str = f"OR{i+1}-" + "_".join(group[:2]) 
            if len(group) > 2:
                group_str += "_etc"
            or_names.append(group_str)
        parts.append("_".join(or_names))
        
    if config['NOT']:
        parts.append("NOT-" + "_".join(config['NOT'][:3])) 
        if len(config['NOT']) > 3:
            parts.append("_etc")
            
    base_name = "_".join(parts)
    base_name = re.sub(r'[^\w\-]', '_', base_name)
    
    return base_name if base_name else "Empty_Query"


def matches_boolean_query(filename: str, config: Dict[str, List[Any]]) -> bool:
    """
    Checks if a filename meets the boolean logic: 
    (AND) AND (one option from EACH OR group) AND (NONE of NOT)
    """
    name_lower = filename.lower()
    and_condition = all(k.lower() in name_lower for k in config['AND'])
    
    or_groups_condition = True
    if config['OR_GROUPS']:
        for group in config['OR_GROUPS']:
            group_matched = any(k.lower() in name_lower for k in group)
            if not group_matched:
                or_groups_condition = False
                break
    
    not_condition = not any(k.lower() in name_lower for k in config['NOT'])
    
    return and_condition and or_groups_condition and not_condition


def analyze_and_combine_csvs(folder_path=".") -> Dict[str, str]:
    """
    Processes multiple search configurations, filters, combines, calculates statistics, 
    saves a file for each configuration, and returns a map of config NAME to filepath.
    """

    # 1. DEFINITION OF MULTIPLE GROUPS (16 configurations defined by the user)
    # CADA DICCIONARIO ES UNA AGRUPACIÓN QUE GENERARÁ UN ARCHIVO CSV
    # -------------------------------------------------------------------------
    SEARCH_CONFIGS = [
        { 'NAME': "Fe-FeGa_ARG_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["104", "844"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_ARG_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["104", "844"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_ARG_MET", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["104", "844"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_ARG_MET", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["104", "844"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_TRP_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["107", "847"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_TRP_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["107", "847"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_TRP_MET", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["107", "847"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_TRP_MET", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["107", "847"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_HIS-A_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["108", "848"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_HIS-A_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["108", "848"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_HIS-A_MET", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["108", "848"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_HIS-A_MET", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["108", "848"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_HIS-B_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["270", "1010"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_HIS-B_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["270", "1010"], ["1481", "1483"]], 'NOT': [] },
        { 'NAME': "Fe-FeGa_HIS-B_MET", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["270", "1010"], ["1482", "1484"]], 'NOT': [] },
        { 'NAME': "Ga-GaFe_HIS-B_MET", 'AND': ["HW"], 'OR_GROUPS': [["_GA_", "_GAFE_"], ["270", "1010"], ["1482", "1484"]], 'NOT': [] },
    ]
    # -------------------------------------------------------------------------
    
    generated_files = {}

    search_pattern_csv = os.path.join(folder_path, "*.csv")
    all_csv_files = glob.glob(search_pattern_csv)

    if not all_csv_files:
        print(f"⚠️ No CSV files found in the folder: {folder_path}")
        return {}

    num_configs = len(SEARCH_CONFIGS)
    print(f"🔎 Processing {num_configs} search configurations.")

    # Bucle principal para procesar CADA configuración de búsqueda
    for config_index, config in enumerate(SEARCH_CONFIGS):
        
        print("\n" + "="*80)
        print(f"CONFIGURATION {config_index + 1}/{num_configs}: {config['NAME']}")
        print("="*80)
        
        filtered_files = []
        
        # 2. Filter CSV files
        for csv_file in all_csv_files:
            file_name = os.path.basename(csv_file)
            if matches_boolean_query(file_name, config):
                filtered_files.append(csv_file)
            
        print(f"✅ Found {len(filtered_files)} files matching the condition.")

        if not filtered_files:
            print(f"❌ Configuration {config['NAME']} found no files. Skipping.")
            continue
            
        # Print list of included files for verification
        print("\nFiles included in this group:")
        for f in filtered_files:
            print(f"   - {os.path.basename(f)}")
        print("-" * 50)


        # 3. Combine DataFrames
        try:
            dataframes = []
            for f in filtered_files:
                try:
                    df = pd.read_csv(f)
                    # Use the correct columns for analysis, even if they contain LIE_00001
                    required_cols = ['LIE_00001[EELEC]', 'LIE_00001[EVDW]', '[ETOTAL]']
                    
                    # Ensure the dataframe has at least one of the required columns
                    if not df.empty and any(col in df.columns for col in required_cols):
                        dataframes.append(df)
                    elif df.empty:
                        print(f"   Info: Skipping empty file {os.path.basename(f)}.")
                    else:
                        print(f"   Warning: File {os.path.basename(f)} is missing required columns. Skipping.")
                        
                except Exception as e:
                    print(f"   Error reading {os.path.basename(f)}: {e}")
                    
            if not dataframes:
                print("❌ No valid DataFrames to combine. Skipping.")
                continue
                
            df_combined = pd.concat(dataframes, ignore_index=True)
            print(f"✅ DataFrames from {len(dataframes)} files combined. Total rows: {len(df_combined)}.")
        except Exception as e:
            print(f"❌ Error combining DataFrames: {e}")
            continue


        # 4. Calculate statistics
        # Map the dataframe column names to the short names used for plotting
        cols_analysis = {
            'LIE_00001[EELEC]': '[EELEC]',
            'LIE_00001[EVDW]': '[EVDW]',
            '[ETOTAL]': '[ETOTAL]'
        }
        
        results = []
        
        for df_col, short_name in cols_analysis.items():
            if df_col in df_combined.columns:
                mean_val = df_combined[df_col].mean()
                std_val = df_combined[df_col].std()
                results.append([f"{short_name} Media", f"{mean_val:.4f}"])
                results.append([f"{short_name} Std", f"{std_val:.4f}"])
            else:
                # Check for the short name if the LIE_ prefix is not present
                if short_name in df_combined.columns:
                    mean_val = df_combined[short_name].mean()
                    std_val = df_combined[short_name].std()
                    results.append([f"{short_name} Media", f"{mean_val:.4f}"])
                    results.append([f"{short_name} Std", f"{std_val:.4f}"])
                else:
                    print(f"   Warning: Column '{df_col}' or '{short_name}' not found. Skipping calculation.")

        
        # 5. and 6. Generate descriptive name and save the file
        output_base_name = get_descriptive_name(config)
        output_csv_file = os.path.join(folder_path, f"{output_base_name}_STATS.csv")
        
        # Save CSV without stats first
        df_combined.to_csv(output_csv_file, index=False)
        
        # 7. Insert results into the header
        if results:
            temp_file = output_csv_file + ".tmp"
            
            # Format criteria for the header (more readable)
            and_str = f"AND: ({', '.join(config['AND'])})"
            not_str = f"NOT: ({', '.join(config['NOT'])})"
            or_str_parts = []
            for group in config['OR_GROUPS']:
                or_str_parts.append(f"({' OR '.join(group)})")
            or_str = f"OR GROUPS: " + " AND ".join(or_str_parts)

            # Prepare header lines as simple strings (NOT lists for csv.writer)
            header_lines = [
                f"# GROUP: {config['NAME']}",
                f"# Applied Criteria: {and_str} | {or_str} | {not_str}", 
                f"#--------------------------------------",
            ]
            
            # Consolidate statistics into a single, pipe-separated metadata string
            metadata_parts = []
            for label, value in results:
                # Rename Spanish labels to English for consistency (Media -> Mean, Std -> Std)
                english_label = label.replace(" Media", " Mean").replace(" Std", " Std")
                metadata_parts.append(f"{english_label} = {value}")
            
            # **FIX: Use pipe '|' as delimiter for robust reading later**
            stats_line = "# STATS: " + " | ".join(metadata_parts)
            header_lines.append(stats_line)
            header_lines.append("#--------------------------------------")
            
            # Perform header insertion using file write for clean metadata
            # We open with newline='' to ensure correct newline handling for csv reader/writer
            with open(output_csv_file, 'r', newline='') as infile, \
                 open(temp_file, 'w', newline='') as outfile:
                
                # Write header lines directly as strings
                for line in header_lines:
                    outfile.write(line + '\n') 
                
                # Copy original content (including data header) using csv module
                csv.writer(outfile).writerows(csv.reader(infile))

            # Replace original file
            os.replace(temp_file, output_csv_file)
            print(f"   ✅ Final file generated: {os.path.basename(output_csv_file)}")
            
            # Save the generated file path for plotting phase
            generated_files[config['NAME']] = output_csv_file
            
        else:
            print("⚠️ Could not calculate statistics.")
            
    return generated_files

# ==============================================================================
# II. PLOTTING PHASE FUNCTIONS
# ==============================================================================

def extract_stats_from_csv(file_path: str, metrics: List[str]) -> Dict[str, Tuple[float, float]]:
    """
    Reads the mean and standard deviation (std) from the metadata header of the CSV file.
    
    Returns:
        A dictionary mapping metric name to a (mean, std) tuple, e.g.,
        {'[EELEC]': (mean_val, std_val)}
    """
    data = {}
    
    # Generate the search keys based on the desired metrics
    mean_keys = [f"{m} Mean" for m in metrics]
    std_keys = [f"{m} Std" for m in metrics]
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Stop when the data header starts (i.e., when no longer a comment/metadata line)
                if not line.startswith('#'):
                    break
                
                # Find the STATS line
                if line.startswith('# STATS:'):
                    # Remove the prefix and split by ' | '
                    stats_str = line.strip().replace('# STATS:', '').strip()
                    parts = stats_str.split(' | ') 
                    
                    # Parse each key=value pair
                    stats_map = {}
                    for part in parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            # Now, we ensure correct type conversion.
                            try:
                                stats_map[key.strip()] = float(value.strip())
                            except ValueError as ve:
                                print(f"   Error converting value to float for {key.strip()}: {value.strip()}. Error: {ve}")
                                
                    # Consolidate mean and std into the final data structure
                    for metric in metrics:
                        mean_label = f"{metric} Mean"
                        std_label = f"{metric} Std"
                        
                        if mean_label in stats_map and std_label in stats_map:
                            data[metric] = (stats_map[mean_label], stats_map[std_label])
                        else:
                            print(f"   Warning: Missing data for {metric} in {os.path.basename(file_path)}")
                    return data
                    
    except FileNotFoundError:
        print(f"   Error: File not found for plotting: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"   Error parsing stats from {os.path.basename(file_path)}: {e}")
        
    return data

def generate_bar_chart(plot_groups: List[Dict[str, Any]], ligands: List[str], metrics_to_plot: List[str], generated_files: Dict[str, str]):
    """
    Generates a grouped bar chart with error bars from the aggregated data.
    """
    if not generated_files:
        print("❌ Cannot generate chart: No files were successfully aggregated.")
        return

    # 1. Collect all data
    data_points = []
    x_labels = []

    print("\n📈 Collecting data for plotting...")

    # Iterate through the desired groups for the X-axis (all groups are included now)
    for group in plot_groups:
        current_x_label = group['X_LABEL']
        x_labels.append(current_x_label)
        group_data = {}
        is_group_valid = True
        
        # Iterate through the ligands (Fe, Ga) for the current X-axis group
        for config_name in group['CONFIG_NAMES']:
            
            if config_name not in generated_files:
                # If a file is missing, we invalidate the entire group for plotting
                print(f"   Warning: File for config '{config_name}' not found. Skipping plot group: {current_x_label}")
                is_group_valid = False
                break
                
            file_path = generated_files[config_name]
            stats = extract_stats_from_csv(file_path, metrics_to_plot)
            
            # DETERMINE LIGAND SAFELY:
            ligand = None
            try:
                # Extract the part before the first hyphen and find the matching ligand
                prefix = config_name.split('-')[0]
                ligand = next((L for L in ligands if L.lower() == prefix.lower()), None)
            except Exception as e:
                print(f"   Error determining ligand from config name '{config_name}': {e}")
                
            if ligand is None:
                # This should not happen if config_names are correct, but handles unexpected data gracefully.
                print(f"   Error: Could not determine primary ligand (Fe or Ga) from config name: '{config_name}'. Skipping plot group: {current_x_label}")
                is_group_valid = False
                break # Skip the entire group if the ligand cannot be identified
            
            # Store the extracted stats
            for metric, (mean, std) in stats.items():
                key = f"{ligand}{metric}" # e.g., 'Fe[EELEC]'
                group_data[key] = {'mean': mean, 'std': std}
        
        # Only append data if the entire group passed checks
        if is_group_valid and group_data:
            data_points.append(group_data)
        else:
            # If the group was invalid or empty, we append None as a placeholder
            data_points.append(None)


    # Filter out any groups that were skipped (i.e., where data_points item is None)
    # This also ensures valid_x_labels matches the data_points indices.
    valid_data_points = [dp for dp in data_points if dp is not None]
    valid_x_labels = [x_labels[i] for i, dp in enumerate(data_points) if dp is not None]
    
    if not valid_data_points:
        print("❌ All plot groups were empty or had missing files. Chart generation failed.")
        return
        
    # 2. Prepare plot data structure
    
    # Total number of unique bars per X-axis group (e.g., 2 ligands * 2 metrics = 4 bars)
    num_bars_per_group = len(ligands) * len(metrics_to_plot)
    
    # Width of a single bar
    bar_width = 0.8 / num_bars_per_group 
    
    # List of all keys in the order they should appear (Fe metrics, then Ga metrics)
    plot_keys = [f"{L}{M}" for L in ligands for M in metrics_to_plot]
    
    # X positions for each group (0, 1, 2, ...) based on valid groups
    x = range(len(valid_x_labels))
    
    # Mayor tamaño de figura para una mejor visualización
    fig, ax = plt.subplots(figsize=(16, 8)) 
    
    # 3. Plotting loop
    
    # Keep track of which bar key corresponds to which legend label
    handles = []
    labels = []
    
    for i, key in enumerate(plot_keys):
        # Calculate the X position for this specific bar type (e.g., Fe[EELEC])
        x_pos = [p + i * bar_width - (num_bars_per_group - 1) * bar_width / 2 for p in x]
        
        # Extract means and stds for this key across all X-axis groups
        means = [d.get(key, {}).get('mean', 0) for d in valid_data_points]
        stds = [d.get(key, {}).get('std', 0) for d in valid_data_points]

        # Determine color and label for the legend
        ligand_name = key[:2] if key.startswith(tuple(L.upper() for L in ligands)) or key.startswith(tuple(ligands)) else '??'
        metric = key[len(ligand_name):]
        
        color = COLORS.get(key, 'gray')
        label = f"{ligand_name} {metric}" # e.g., "Fe [EELEC]"

        # Plot the bars with error bars
        bar_handle = ax.bar(
            x_pos, 
            means, 
            bar_width, 
            yerr=stds, 
            label=label, 
            color=color, 
            capsize=5, 
            error_kw={'capthick': 1.5}
        )
        
        # Collect handles for the legend
        if label not in labels:
            handles.append(bar_handle[0]) 
            labels.append(label)

    # 4. Final plot customization
    
    # Set X-axis ticks to the center of the bar groups
    ax.set_xticks(x)
    ax.set_xticklabels(valid_x_labels, rotation=45, ha="right")
    
    # Título en negrita
    ax.set_title(PLOT_TITLE, fontweight='bold', fontsize=16) 
    
    # Eje Y en negrita
    ax.set_ylabel(Y_AXIS_LABEL, fontweight='bold')
    
    # 1. Aplicar el rango del Eje Y si está definido
    if Y_LIMITS and len(Y_LIMITS) == 2:
        ax.set_ylim(Y_LIMITS)
        print(f"📊 Applied Y-axis limits: {Y_LIMITS}")

    # 2. Leyenda con cuadro y bordes redondeados (fancybox=True)
    ax.legend(
        loc='best', 
        handles=handles, 
        labels=labels, 
        fancybox=True,      # Activa los bordes redondeados
        framealpha=0.9,     # Opacidad del cuadro (0.8 para verlo bien)
        shadow=True,        # Opcional, añade sombra para mejor relieve
        fontsize=10
    )
    
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Save the figure
    plot_filename = "Combined_Energy_Analysis_Plot.png"
    plt.savefig(plot_filename, bbox_inches='tight')
    plt.close(fig)
    print(f"\n✨ Plotting successful. Image saved as: {plot_filename}")


# --- Main Execution Block ---

# 1. Define the 8 main plot groups (X-axis labels) and map them to the 
#    16 generated file configuration names (Fe and Ga versions).
PLOT_GROUPS = [
    {
        'X_LABEL': r"$\text{Arg(104)} \rightarrow \text{HEM}$",
        'CONFIG_NAMES': ["Fe-FeGa_ARG_HEM", "Ga-GaFe_ARG_HEM"]
    },
    {
        'X_LABEL': r"$\text{Arg(104)} \rightarrow \text{Fe/Ga}$",
        'CONFIG_NAMES': ["Fe-FeGa_ARG_MET", "Ga-GaFe_ARG_MET"]
    },
    {
        'X_LABEL': r"$\text{Trp(107)} \rightarrow \text{HEM}$",
        'CONFIG_NAMES': ["Fe-FeGa_TRP_HEM", "Ga-GaFe_TRP_HEM"]
    },
    {
        'X_LABEL': r"$\text{Trp(107)} \rightarrow \text{Fe/Ga}$",
        'CONFIG_NAMES': ["Fe-FeGa_TRP_MET", "Ga-GaFe_TRP_MET"]
    },
    {
        'X_LABEL': r"$\text{His}\alpha\text{(108)} \rightarrow \text{HEM}$",
        'CONFIG_NAMES': ["Fe-FeGa_HIS-A_HEM", "Ga-GaFe_HIS-A_HEM"]
    },
    {
        'X_LABEL': r"$\text{His}\alpha\text{(108)} \rightarrow \text{Fe/Ga}$",
        'CONFIG_NAMES': ["Fe-FeGa_HIS-A_MET", "Ga-GaFe_HIS-A_MET"]
    },
    {
        'X_LABEL': r"$\text{His}\beta\text{(270)} \rightarrow \text{HEM}$",
        'CONFIG_NAMES': ["Fe-FeGa_HIS-B_HEM", "Ga-GaFe_HIS-B_HEM"]
    },
    {
        'X_LABEL': r"$\text{His}\beta\text{(270)} \rightarrow \text{Fe/Ga}$",
        'CONFIG_NAMES': ["Fe-FeGa_HIS-B_MET", "Ga-GaFe_HIS-B_MET"]
    },
]

# Run Phase 1: Aggregation
generated_files = analyze_and_combine_csvs()

# Run Phase 2: Plotting
generate_bar_chart(PLOT_GROUPS, LIGANDS, METRICS_TO_PLOT, generated_files)

print("\n✨ Process completed: Aggregation and Plotting finished.")
