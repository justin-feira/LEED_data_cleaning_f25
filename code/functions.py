'''
Functions for transforming LEED data from long to wide format.
Last updated: 10-27-25
Contents
- to_wide: Transforms long format data into wide format with separate potential and awarded columns for each category.
- to_wide_var: Variant of to_wide that instead has only awarded values and stores potential in the cat name
- get_building_data: Extracts data for a specific building code.
- version_data: Applies to_wide to data filtered by a specific LEED version.
- breakdown_by_version: Separates data by LEED version and saves each to a separate CSV
'''

import pandas as pd
import numpy as np
from pathlib import Path

# repository root (assumes this file lives in <repo>/code/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data_repository"

def to_wide(df, building_code=None):
    """
    Transform data from long to wide format with separate potential and awarded columns
    for each category, with integer dtypes.
    """
    ## if building code is not provided, assume we want the whole dataframe
    if building_code is not None:
        # Check if building_code is a list
        if isinstance(building_code, list):
            # Filter for multiple building codes
            data_to_process = df[df['building_code'].isin(building_code)]
            print(f"Filtered data shape for buildings {building_code}: {data_to_process.shape}")
        else:
            # Handle single building code
            building_code = str(building_code)
            data_to_process = df[df['building_code'] == building_code]
            print(f"Filtered data shape for building {building_code}: {data_to_process.shape}")
    else:
        data_to_process = df
        print(f"Using full dataframe shape: {data_to_process.shape}")
    
    if len(data_to_process) == 0:
        print(f"No data found for building code(s): {building_code}")
        return pd.DataFrame()
    
    ## select only relevant columns
    required_cols = ['building_name', 'leed_version', 'cat_and_cat_name', 'potential_points', 'awarded_points']
    data_to_process = data_to_process[required_cols]
    
    ## create separate pivot tables for potential and awarded points
    potential_wide = data_to_process.pivot_table(
        index=['building_name', 'leed_version'], 
        columns='cat_and_cat_name', 
        values='potential_points',
        aggfunc='first',
        fill_value=np.nan
    )
    
    awarded_wide = data_to_process.pivot_table(
        index=['building_name', 'leed_version'], 
        columns='cat_and_cat_name', 
        values='awarded_points',
        aggfunc='first',
        fill_value=np.nan
    )
    
    ## reset index to make building_name and leed_version regular columns
    potential_wide = potential_wide.reset_index()
    awarded_wide = awarded_wide.reset_index()
    
    ## create the final dataframe by merging potential and awarded
    result = potential_wide[['building_name', 'leed_version']].copy()
    
    ## add columns for each category with both potential and awarded
    for col in potential_wide.columns[2:]:  # skip building_name and leed_version
        # Add potential column (using nullable Int64 to preserve NaN values)
        result[f"{col}_potential"] = potential_wide[col].astype('Int64')
        # Add awarded column (using nullable Int64 to preserve NaN values)
        result[f"{col}_awarded"] = awarded_wide[col].astype('Int64')
    
    print(f"Final result shape: {result.shape}")
    return result

## slightly modified to_wide variant that uses cat_code instead of cat_and_cat_name
def to_wide_var(df, building_code=None):
    """
    Transform data from long to wide format with separate potential and awarded columns
    for each category, with integer dtypes.
    """
    ## if building code is not provided, assume we want the whole dataframe
    if building_code is not None:
        # Check if building_code is a list
        if isinstance(building_code, list):
            # Filter for multiple building codes
            data_to_process = df[df['building_code'].isin(building_code)]
            print(f"Filtered data shape for buildings {building_code}: {data_to_process.shape}")
        else:
            # Handle single building code
            building_code = str(building_code)
            data_to_process = df[df['building_code'] == building_code]
            print(f"Filtered data shape for building {building_code}: {data_to_process.shape}")
    else:
        data_to_process = df
        print(f"Using full dataframe shape: {data_to_process.shape}")
    
    if len(data_to_process) == 0:
        print(f"No data found for building code(s): {building_code}")
        return pd.DataFrame()
    
    ## select only relevant columns
    required_cols = ['building_name', 'leed_version', 'cat_and_cat_name', 'potential_points', 'awarded_points']
    data_to_process = data_to_process[required_cols]
    
    ## create separate pivot tables for potential and awarded points

    
    awarded_wide = data_to_process.pivot_table(
        index=['building_name', 'leed_version'], 
        columns='cat_and_cat_name', 
        values='awarded_points',
        aggfunc='first',
        fill_value=np.nan
    )
    
    ## reset index to make building_name and leed_version regular columns
    
    awarded_wide = awarded_wide.reset_index()
    
    ## create the final dataframe by merging potential and awarded
    result = awarded_wide[['building_name', 'leed_version']].copy()
    
    ## add columns for each category with both potential and awarded
    for col in awarded_wide.columns[2:]:  # skip building_name and leed_version
        # Add awarded column (using nullable Int64 to preserve NaN values)
        result[f"{col}"] = awarded_wide[col].astype('Int64')
    
    print(f"Final result shape: {result.shape}")
    return result

## provide a function to extract a specific building's data
def get_building_data(df, building_code):
    return df[df['building_code'] == building_code]

## provide a function to use to_wide for a specific group (eg set any category selection such as all buildings of a certain LEED version) 
## and pass it through the to_wide function
def version_data(leed_version, df, function=to_wide):
    version_df = df[df['leed_version'] == leed_version]
    return function(version_df)

## function to automatically seperate by leed_version and save each to a separate csv
def breakdown_by_version(df, function=to_wide, output_dir=None):
    """
    Split the dataframe by `leed_version` and save a wide CSV for each version.

    Parameters
    - df: pandas.DataFrame containing a 'leed_version' column
    - function: transformation function to apply to each version (default: to_wide)
    - output_dir: path-like where per-version CSVs will be written. If None, uses
      the module-level DATA_DIR. Can be a str or Path.
    """
    # Resolve output directory
    if output_dir is None:
        outdir = DATA_DIR / "final_wide_data"
    else:
        outdir = Path(output_dir)

    # Create the directory if it doesn't exist
    outdir.mkdir(parents=True, exist_ok=True)

    versions = df['leed_version'].dropna().unique()
    for version in versions:
        safe_version = str(version).replace('.', '_').replace(' ', '_')
        print(f"Processing LEED version: {version}")
        wide_df = version_data(version, df, function=function)
        outpath = outdir / f"cleaned_wide_leed_data_{safe_version}.csv"
        wide_df.to_csv(outpath, index=False)