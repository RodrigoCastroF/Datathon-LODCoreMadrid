# scripts/clean_ine_demographics.py

"""Clean INE demographics data and prepare for merge."""

import pandas as pd
from pathlib import Path

# Age group mappings (INE bracket → our group)
AGE_GROUPS = {
    "0-19": ["De 0 a 4 años", "De 5 a 9 años", "De 10 a 14 años", "De 15 a 19 años"],
    "20-39": ["De 20 a 24 años", "De 25 a 29 años", "De 30 a 34 años", "De 35 a 39 años"],
    "40-59": ["De 40 a 44 años", "De 45 a 49 años", "De 50 a 54 años", "De 55 a 59 años"],
    "60-79": ["De 60 a 64 años", "De 65 a 69 años", "De 70 a 74 años", "De 75 a 79 años"],
    "80+": ["De 80 a 84 años", "De 85 a 89 años", "De 90 a 94 años", "De 95 a 99 años", "100 y más años"],
}

def parse_ine_number(value):
    """Parse INE number format (dots as thousand separators)."""
    if pd.isna(value):
        return 0
    return int(str(value).replace(".", ""))

def main():
    script_dir = Path(__file__).parent.parent
    input_path = script_dir / "data" / "population_by_age_and_gender.csv"
    output_path = script_dir / "data" / "demographics_clean.csv"
    
    # Load INE data
    df = pd.read_csv(input_path, sep="\t", dtype={"Total": str})
    
    # Parse Total column
    df["Total"] = df["Total"].apply(parse_ine_number)
    
    # Filter: 2022 data only, municipality level
    df = df[df["Periodo"] == "1 de enero de 2022"].copy()
    df = df[df["Municipios"].notna()].copy()
    
    # Extract codigo from "Municipios" column (format: "28001 Acebeda, La")
    df["codigo"] = df["Municipios"].str.extract(r"^(\d+)")[0].astype(int)
    df["Nombre"] = df["Municipios"].str.extract(r"^\d+\s+(.+)$")[0]
    
    # Pivot: rows=municipios, cols=age_group+gender
    result = []
    
    for codigo in df["codigo"].unique():
        muni_data = df[df["codigo"] == codigo]
        nombre = muni_data["Nombre"].iloc[0]
        
        row = {"codigo": codigo, "Nombre": nombre}
        
        for group_name, ine_brackets in AGE_GROUPS.items():
            for gender in ["Total", "Hombres", "Mujeres"]:
                col_name = f"DEM_Edad_{group_name.replace('-', '_').replace('+', 'Plus')}_{gender}"
                
                # Sum across INE brackets
                mask = (muni_data["Sexo"] == gender) & (muni_data["Edad (grupos quinquenales)"].isin(ine_brackets))
                total = muni_data[mask]["Total"].sum()
                
                row[col_name] = int(total)
        
        result.append(row)
    
    # Create DataFrame
    demo_df = pd.DataFrame(result)
    print(f"DEBUG - Columns created: {list(demo_df.columns)}")


    # Filter: municipalities < 50k (sum all age group totals)
    total_pop = (demo_df["DEM_Edad_0_19_Total"] + demo_df["DEM_Edad_20_39_Total"] + 
                demo_df["DEM_Edad_40_59_Total"] + demo_df["DEM_Edad_60_79_Total"] + 
                demo_df["DEM_Edad_80Plus_Total"])
    demo_df = demo_df[total_pop < 50000]

    
    # Export
    demo_df.to_csv(output_path, index=False)
    print(f"✅ Exported {len(demo_df)} municipalities to {output_path}")
    print(f"Columns: {list(demo_df.columns)}")

if __name__ == "__main__":
    main()
