"""Merge demographics into merged_dataset.csv."""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    script_dir = Path(__file__).parent.parent
    demo_path = script_dir / "data" / "demographics_clean.csv"
    master_path = script_dir / "data" / "merged_dataset.csv"
    
    # Find most recent backup
    backup_files = sorted(master_path.parent.glob("merged_dataset.backup_*.csv"), reverse=True)
    if not backup_files:
        print("❌ No backup files found")
        return
    
    backup_to_use = backup_files[0]
    print(f"📦 Using backup: {backup_to_use}")
    
    # Load data (semicolon delimiter)
    demo_df = pd.read_csv(demo_path)
    master_df = pd.read_csv(backup_to_use, sep=",")
    
    # Remove duplicate Horcajuelo de la Sierra (keep only codigo 28071)
    master_df = master_df.drop_duplicates(subset=["codigo"], keep="first")
    print(f"✅ Removed duplicates, {len(master_df)} municipalities remaining")
    
    # Merge
    merged = master_df.merge(demo_df.drop(columns=["Nombre"]), on="codigo", how="left")
    
    # Validate
    missing = merged[merged["DEM_Edad_0_19_Total"].isna()]
    if len(missing) > 0:
        print(f"⚠️  {len(missing)} municipalities missing demographics")
    
    # Export with semicolon delimiter
    merged.to_csv(master_path, index=False, sep=";")
    print(f"✅ Updated {master_path} with {len(demo_df.columns)-2} demographic columns")

if __name__ == "__main__":
    main()
