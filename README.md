# Graphics

**LIE_Aggregation_AND_Plotter.py**

Energy Data Aggregation and Plotting Script (EELEC, EVDW)
This Python script is designed to automate the processing, aggregation, and visualization of multiple CSV files containing energy calculation results (typically from docking or LIE simulations). It combines files based on defined Boolean criteria, calculates descriptive statistics (Mean and Standard Deviation) for specific metrics, and generates a grouped bar chart with error bars.

1. Requirements and Initial Setup
To run this script, you need to have Python and the following libraries installed:

pandas: For data manipulation and combining CSV files.

matplotlib: For generating the bar chart.

You can install the libraries using pip:

pip install pandas matplotlib

2. Input File Structure
The script expects all resulting CSV files to be located in the same folder where the script is executed (folder_path=".").

A. Filename Convention (CRITICAL)
The script's filtering logic relies entirely on the keywords present in the CSV filenames.

For example, a file named: HW_FE_104_1481.csv

Must contain the required terms (e.g., HW, FE, 104, 1481) to be included in a specific aggregation.

B. CSV Content Structure
Each input CSV file must contain, at minimum, the energy metric columns you wish to analyze. The script is configured to look for columns with the LIE_00001 prefix (common in certain analyses) or the short metric name:

Long Column Name (Searched)

Short Column Name (Alternative)

Description

LIE_00001[EELEC]

[EELEC]

Electrostatic Energy

LIE_00001[EVDW]

[EVDW]

Van der Waals Energy

[ETOTAL]

[ETOTAL]

Total Energy (optional)

The script will first attempt to read the columns with the LIE_00001 prefix, and if they do not exist, it will look for the short column names (e.g., [ETOTAL]).

3. Code Configuration Guide
The main options you need to modify are located at the beginning of the script.

A. Global Section: 0. GLOBAL CONFIGURATION
Here you control what is plotted and how it looks.

Variable

Type

Description

Where to Modify (Example)

LIGANDS

List[str]

Names of the primary groups (e.g., ligand or metal) for legend grouping.

['Fe', 'Ga']

METRICS_TO_PLOT

List[str]

The energy metrics to include in the plot.

['[EELEC]', '[EVDW]']

Y_LIMITS

List[float] or None

Defines the Y-Axis range for the plot. Use [minimum, maximum] to set fixed limits (e.g., [-100, 0]) or None for Matplotlib to determine it automatically.

None

PLOT_TITLE

str

Title of the plot.

"Electrostatic (EELEC) & Van der Waals (EVDW) Energy Analysis"

COLORS

Dict[str, str]

Color map. The key must be the combination of ligand and metric (e.g., 'Fe[EELEC]'). Ensure all metrics defined in METRICS_TO_PLOT have an assigned color for each ligand in LIGANDS.

See example in the code

B. Aggregation Section: I. AGGREGATION PHASE FUNCTIONS
Here you define the logic for grouping the CSV files and generating the intermediate _STATS.csv files.

SEARCH_CONFIGS
This list of dictionaries is the core of the filtering process. Each dictionary in this list generates one statistics file and one bar group in the plot.

'NAME' (Key): Descriptive name for the group. This name is used for reference in the plotting phase.

'AND': A list of terms that MUST be present in the filename.

'OR_GROUPS': A list of lists. At least one term from EACH sub-list must be present. (E.g., [["_FE_", "_FEGA_"], ["104", "844"]] means the file must contain (_FE_ OR _FEGA_) AND (104 OR 844)).

⚠️ Important: Underscores (_) have been added to the ligand terms ("_FE_", "_GA_") to prevent false positives (e.g., to ensure "FE" in "FEGA" is not matched when searching for an isolated "FE").

'NOT': A list of terms that MUST NOT be present in the filename.

Aggregation Group Example:

{ 'NAME': "Fe-FeGa_ARG_HEM", 'AND': ["HW"], 'OR_GROUPS': [["_FE_", "_FEGA_"], ["104", "844"], ["1481", "1483"]], 'NOT': [] },

This searches for files containing: HW AND (_FE_ OR _FEGA_) AND (104 OR 844) AND (1481 OR 1483).

C. Main Block: --- Main Execution Block ---
Here you define the order and the final label for the groups on the X-Axis of the plot.

PLOT_GROUPS
This list defines the X-Axis labels of the chart and groups the results from the statistical files generated in the aggregation phase.

'X_LABEL': The label that will be displayed on the X-Axis (the code uses LaTeX notation (r"$\text{...}$") for academic formatting like Hisα(108)→HEM).

'CONFIG_NAMES': A list of the 'NAME' strings defined in SEARCH_CONFIGS that should appear as bars within this X-Axis group.

Plotting Group Example:

{
    'X_LABEL': r"$\text{His}\alpha\text{(108)} \rightarrow \text{Fe/Ga}$",
    'CONFIG_NAMES': ["Fe-FeGa_HIS-A_MET", "Ga-GaFe_HIS-A_MET"]
},

This will create a single label on the X-Axis and group the bars from the Fe-FeGa_HIS-A_MET and Ga-GaFe_HIS-A_MET configurations.

4. Execution and Output
A. Execution Process
Simply run the script:

python EnergyDataPlotter.py

The script will print a detailed summary of which files are included in each search group and whether the plotting phase was successful.

B. Output Files
Statistics Files (Intermediate Output):
For each configuration in SEARCH_CONFIGS, an output CSV file will be generated (e.g., AND-HW_OR1-FE_FEGA_etc_STATS.csv). This file contains all the combined data from the source files and a metadata header (# STATS:) that includes the calculated mean and standard deviation for each metric.

Bar Chart (Final Output):
An image file named Combined_Energy_Analysis_Plot.png will be generated. This chart will include:

Grouped bars according to the X-Axis label (X_LABEL).

Error bars representing the standard deviation.

A legend with a box and shadow (fancybox=True).

Y-Axis limits as set by the Y_LIMITS variable.
