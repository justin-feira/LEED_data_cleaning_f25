'''
Purpose: Cleans original data from master spreadsheet
while still remaining in long form
Last updated: 10-27-25
'''
## import packages
import pandas as pd
import numpy as np
from pathlib import Path


# Determine repository root (assumes this file is in <repo>/code/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data_repository"

## load data (now organized under data_repository/original_data)
leed = pd.read_csv(DATA_DIR / "original_data" / "original_data.csv")

## create building_code - building dictionary
buildings_df = pd.read_csv(DATA_DIR / "original_data" / "buildings.csv")
buildings = dict(zip(buildings_df['building_code'], buildings_df['building']))
leed_versions = dict(zip(buildings_df['building_code'], buildings_df['leed_code']))

## map building names and leed versions to main dataframe
leed['building_name'] = leed['building_code'].map(buildings)
leed['leed_version'] = leed['building_code'].map(leed_versions)

## create new category called "points_earned" that shows both points awarded
## and points available (e.g. "{points_awarded}/{points_available}")
leed['points_earned'] = leed['awarded_points'].astype(str) + "/" + leed['potential_points'].astype(str)

## create new category called "cat_and_cat_name" that concatenates cat_code and cat
leed['cat_and_cat_name'] = leed['cat_code'] + " - " + leed['cat']

## ensure that building code is string, not int
leed['building_code'] = leed['building_code'].astype(str)
leed['points_earned'] = leed['points_earned'].astype(str)

## for points_earned, replace instances of 0/0 with prerequisite
leed['points_earned'] = leed['points_earned'].replace("0/0", "prerequisite")

## set leed_version to all strings
leed['leed_version'] = (leed['leed_version']
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r'^(v|leed[\s-]*)', '', regex=True)
    .str.replace(r'\.0$', '', regex=True)
    .str.replace('_', '.', regex=False)
    .str.strip()
)

# save full cleaned long-form (if desired)
leed.to_csv(DATA_DIR / "cleaned_long_data" / "wholeset_cleaned_long_data.csv", index=False)

## create a dataframe that is only with type=cat
leed_cats = leed[leed['type'] == 'cat'].copy()

## create new category called "cat_and_cat_code" that concatenates cat_code and potential_points
leed_cats['cat_and_cat_name'] = leed_cats['cat_code'].astype(str) + "(" + leed_cats['potential_points'].astype(str) + ")"  + 'v' + leed_cats['leed_version'].astype(str)
### I could add version name to the end of this if needed?

## rename columns for clarity
leed_cats['points_earned'] = leed_cats['points_earned'].astype(str)

## save cleaned data
## save cleaned category-long data to cleaned_long_data folder
leed_cats.to_csv(DATA_DIR / "cleaned_long_data" / "cleaned_data_cats.csv", index=False)