import pandas as pd
import sys
from pathlib import Path

# Make sure the current directory (code/) is on sys.path so we can import sibling modules
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
	sys.path.insert(0, str(HERE))

import functions

# Simple, script-style logic (reads cleaned category data and writes a wide CSV)
repo_root = HERE.parent
data_dir = repo_root / "data_repository"

in_path = data_dir / "cleaned_long_data" / "cleaned_data_cats.csv"
out_path = data_dir / "final_wide_data" / "cleaned_wide_data_cats.csv"

# Ensure output directory exists
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(in_path)
df_wide = functions.to_wide_var(df)
df_wide.to_csv(out_path, index=False)

# Also export per-version files into the final_wide_data folder
functions.breakdown_by_version(df, function=functions.to_wide_var, output_dir=data_dir / "final_wide_data")