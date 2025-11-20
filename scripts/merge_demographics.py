"""Merge demographics into merged_dataset.csv."""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    script_dir = Path(__file__).parent.parent
    demo_path = script_dir / "data" / "demographics_clean.csv"
    master_path = script_dir / "data" / "merged_dataset.csv"
    
    # Backup original
    backup_path = master_path.with_suffix(f".backup_{datetime.now():%Y%m%d_%H%M%S}.csv")
    pd.read_csv(master_path).to_csv(backup_path, index=False)
    print(f"📦 Backup created: {backup_path}")
    
    # Load data
    demo_df = pd.read_csv(demo_path)
    master_df = pd.read_csv(master_path)
    
    # Merge
    merged = master_df.merge(demo_df.drop(columns=["Nombre"]), on="codigo", how="left")
    
    # Validate
    missing = merged[merged["DEM_Edad_0_19_Total"].isna()]
    if len(missing) > 0:
        print(f"⚠️  {len(missing)} municipalities missing demographics")
    
    # Export
    merged.to_csv(master_path, index=False)
    print(f"✅ Updated {master_path} with {len(demo_df.columns)-2} demographic columns")

if __name__ == "__main__":
    main()
