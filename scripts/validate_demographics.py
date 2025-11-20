# scripts/validate_demographics.py
"""Validate demographics data consistency."""

import pandas as pd
from pathlib import Path

def main():
    script_dir = Path(__file__).parent.parent
    demo_path = script_dir / "data" / "demographics_clean.csv"
    master_path = script_dir / "data" / "merged_dataset.csv"
    
    # Load data
    demo_df = pd.read_csv(demo_path)
    master_df = pd.read_csv(master_path)
    
    print("=" * 60)
    print("DEMOGRAPHICS VALIDATION")
    print("=" * 60)
    
    # Check 1: Age groups sum to 100%
    print("\n1. Checking age group percentages sum to ~100%...")
    demo_df["total_pop"] = (demo_df["DEM_Edad_0_19_Total"] + demo_df["DEM_Edad_20_39_Total"] + 
                            demo_df["DEM_Edad_40_59_Total"] + demo_df["DEM_Edad_60_79_Total"] + 
                            demo_df["DEM_Edad_80Plus_Total"])
    
    demo_df["pct_0_19"] = demo_df["DEM_Edad_0_19_Total"] / demo_df["total_pop"] * 100
    demo_df["pct_20_39"] = demo_df["DEM_Edad_20_39_Total"] / demo_df["total_pop"] * 100
    demo_df["pct_40_59"] = demo_df["DEM_Edad_40_59_Total"] / demo_df["total_pop"] * 100
    demo_df["pct_60_79"] = demo_df["DEM_Edad_60_79_Total"] / demo_df["total_pop"] * 100
    demo_df["pct_80plus"] = demo_df["DEM_Edad_80Plus_Total"] / demo_df["total_pop"] * 100
    demo_df["pct_sum"] = demo_df[["pct_0_19", "pct_20_39", "pct_40_59", "pct_60_79", "pct_80plus"]].sum(axis=1)
    
    invalid = demo_df[abs(demo_df["pct_sum"] - 100) > 0.01]
    if len(invalid) > 0:
        print(f"   ❌ {len(invalid)} municipalities have invalid percentages:")
        print(invalid[["Nombre", "pct_sum"]])
    else:
        print(f"   ✅ All {len(demo_df)} municipalities sum to 100%")
    
    # Check 2: Missing municipalities in master
    print("\n2. Checking for missing municipalities in master dataset...")
    missing = master_df[master_df["DEM_Edad_0_19_Total"].isna()]
    if len(missing) > 0:
        print(f"   ⚠️  {len(missing)} municipalities missing demographics:")
        print(missing[["Nombre"]].to_string(index=False))
    else:
        print(f"   ✅ All {len(master_df)} municipalities have demographics")
    
    # Check 3: Gender consistency
    print("\n3. Checking gender totals match...")
    for group in ["0_19", "20_39", "40_59", "60_79", "80Plus"]:
        demo_df[f"gender_sum_{group}"] = (demo_df[f"DEM_Edad_{group}_Hombres"] + 
                                          demo_df[f"DEM_Edad_{group}_Mujeres"])
        demo_df[f"gender_diff_{group}"] = abs(demo_df[f"gender_sum_{group}"] - demo_df[f"DEM_Edad_{group}_Total"])
    
    gender_issues = demo_df[demo_df[[f"gender_diff_{g}" for g in ["0_19", "20_39", "40_59", "60_79", "80Plus"]]].max(axis=1) > 0]
    if len(gender_issues) > 0:
        print(f"   ❌ {len(gender_issues)} municipalities have gender mismatches")
    else:
        print(f"   ✅ All gender totals match")
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
