"""
Part 2: Building the Training Dataset

We connect separator safety data with polymer material properties
AND separator-specific performance data scraped from literature.

Step 1: Compile known separator polymers with safety labels
Step 2: Join with OpenPoly for base material properties (Tg, Tm, etc.)
Step 3: Parse scraped literature tables for separator-specific properties
        (porosity, thermal shrinkage, ionic conductivity, tensile strength)
Step 4: Merge everything into one training dataset
Step 5: Deduplicate and save
"""

import pandas as pd
import numpy as np

# --- Load data sources ---
df_polymers = pd.read_csv("data/final_polymer_properties_fromliterature.csv")

# ============================================================
# STEP 1: Compile known separator polymers with safety labels
# ============================================================

# Binary safety labels based on thermal stability from published literature:
#   "safe"   = maintains structural integrity above 150C
#   "unsafe" = loses structural integrity at or below 150C

separator_polymers = pd.DataFrame([
    # --- Polyolefins ---
    {"polymer": "PP", "shutdown_temp_C": 170, "safety": "safe"},
    {"polymer": "PE", "shutdown_temp_C": 135, "safety": "unsafe"},
    {"polymer": "UHMWPE", "shutdown_temp_C": 135, "safety": "unsafe"},
    {"polymer": "HDPE", "shutdown_temp_C": 130, "safety": "unsafe"},
    {"polymer": "LDPE", "shutdown_temp_C": 110, "safety": "unsafe"},

    # --- Fluoropolymers ---
    {"polymer": "PVDF", "shutdown_temp_C": 160, "safety": "safe"},
    {"polymer": "PTFE", "shutdown_temp_C": 327, "safety": "safe"},

    # --- High-performance polymers ---
    {"polymer": "PAN", "shutdown_temp_C": 300, "safety": "safe"},
    {"polymer": "PI", "shutdown_temp_C": 350, "safety": "safe"},
    {"polymer": "PPS", "shutdown_temp_C": 300, "safety": "safe"},
    {"polymer": "PEI", "shutdown_temp_C": 280, "safety": "safe"},
    {"polymer": "PES", "shutdown_temp_C": 220, "safety": "safe"},
    {"polymer": "PSF", "shutdown_temp_C": 185, "safety": "safe"},

    # --- Engineering polymers ---
    {"polymer": "PET", "shutdown_temp_C": 250, "safety": "safe"},
    {"polymer": "PA6", "shutdown_temp_C": 220, "safety": "safe"},
    {"polymer": "PC", "shutdown_temp_C": 230, "safety": "safe"},
    {"polymer": "POM", "shutdown_temp_C": 175, "safety": "safe"},
    {"polymer": "nylon", "shutdown_temp_C": 220, "safety": "safe"},

    # --- Hydrophilic / gel polymers ---
    {"polymer": "PVA", "shutdown_temp_C": 230, "safety": "safe"},
    {"polymer": "PMMA", "shutdown_temp_C": 105, "safety": "unsafe"},
    {"polymer": "PAA", "shutdown_temp_C": 200, "safety": "safe"},
    {"polymer": "PVP", "shutdown_temp_C": 60, "safety": "unsafe"},
    {"polymer": "PEG", "shutdown_temp_C": 60, "safety": "unsafe"},
    {"polymer": "PEO", "shutdown_temp_C": 65, "safety": "unsafe"},

    # --- Biodegradable / low-stability ---
    {"polymer": "PLA", "shutdown_temp_C": 160, "safety": "safe"},
    {"polymer": "PBS", "shutdown_temp_C": 115, "safety": "unsafe"},
    {"polymer": "PCL", "shutdown_temp_C": 60, "safety": "unsafe"},

    # --- Bio-based ---
    {"polymer": "cellulose", "shutdown_temp_C": 260, "safety": "safe"},
    {"polymer": "chitosan", "shutdown_temp_C": 200, "safety": "safe"},

    # --- Others ---
    {"polymer": "PS", "shutdown_temp_C": 100, "safety": "unsafe"},
    {"polymer": "PVC", "shutdown_temp_C": 100, "safety": "unsafe"},
    {"polymer": "PMP", "shutdown_temp_C": 235, "safety": "safe"},

    # --- Duplicate names in OpenPoly ---
    {"polymer": "polypropylene", "shutdown_temp_C": 170, "safety": "safe"},
    {"polymer": "polyethylene", "shutdown_temp_C": 135, "safety": "unsafe"},
    {"polymer": "polyimide", "shutdown_temp_C": 350, "safety": "safe"},
    {"polymer": "polycarbonate", "shutdown_temp_C": 230, "safety": "safe"},
    {"polymer": "polystyrene", "shutdown_temp_C": 100, "safety": "unsafe"},
    {"polymer": "poly(vinylidene fluoride)", "shutdown_temp_C": 160, "safety": "safe"},
    {"polymer": "polyacrylonitrile", "shutdown_temp_C": 300, "safety": "safe"},
    {"polymer": "polyethersulfone", "shutdown_temp_C": 220, "safety": "safe"},
    {"polymer": "polysulfone", "shutdown_temp_C": 185, "safety": "safe"},
    {"polymer": "cellulose acetate", "shutdown_temp_C": 230, "safety": "safe"},
])

print(f"Step 1: Compiled {len(separator_polymers)} separator polymers with safety labels")

# ============================================================
# STEP 2: Join with OpenPoly for material properties
# ============================================================

key_features = ["Tg (K)", "Tm (K)", "Td (K)",
                "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                "Elongation at Break (%)"]

df_polymer_props = df_polymers[["Name"] + key_features].copy()

# Deduplicate: keep row with most non-null features per polymer
df_polymer_props["n_features"] = df_polymer_props[key_features].notna().sum(axis=1)
df_polymer_props = df_polymer_props.sort_values("n_features", ascending=False)
df_polymer_props = df_polymer_props.drop_duplicates(subset="Name", keep="first")
df_polymer_props = df_polymer_props.drop(columns="n_features")

df_training = separator_polymers.merge(
    df_polymer_props,
    left_on="polymer",
    right_on="Name",
    how="left"
)

# Drop rows without material properties
df_training = df_training.dropna(subset=key_features)
df_training = df_training.drop(columns="Name")

print(f"Step 2: {len(df_training)} polymers after joining with OpenPoly")

# ============================================================
# STEP 3: Parse literature tables for separator-specific data
# ============================================================

print("\nStep 3: Extracting separator-specific data from literature...")

# --- PMC10534950 Table 7: Multi-polymer comparison ---
# Has: substrate material, porosity, thermal shrinkage, ionic conductivity
df_lit1 = pd.read_csv("data/literature_raw/literature_PMC10534950_table7.csv")

lit1_data = []
for _, row in df_lit1.iterrows():
    substrate = str(row.get("SubstrateMaterial", "")).strip()
    porosity = row.get("Porosity(%)", None)
    shrinkage = str(row.get("Thermal Shrinkage (%)", ""))
    conductivity = row.get("Ionic Conductivity (mS cm−1)", None)

    # Parse porosity to float
    try:
        porosity = float(porosity)
    except (ValueError, TypeError):
        porosity = None

    # Parse conductivity to float
    try:
        conductivity = float(conductivity)
    except (ValueError, TypeError):
        conductivity = None

    if substrate:
        lit1_data.append({
            "source_polymer": substrate,
            "lit_porosity": porosity,
            "lit_thermal_shrinkage": shrinkage,
            "lit_ionic_conductivity": conductivity,
            "source": "PMC10534950"
        })

df_lit1_parsed = pd.DataFrame(lit1_data)
print(f"  PMC10534950: {len(df_lit1_parsed)} rows (substrate, porosity, shrinkage, conductivity)")

# --- PMC11241740 Table 1: Cross-polymer comparison ---
# Has: materials, tensile strength, thermal stability, porosity, ionic conductivity
df_lit2 = pd.read_csv("data/literature_raw/literature_PMC11241740_table1.csv")

lit2_data = []
for _, row in df_lit2.iterrows():
    material = str(row.get("Materials", "")).strip()
    tensile = row.get("Tensile Strength (Mpa)", None)
    thermal = str(row.get("Thermal Stability (°C)", ""))
    porosity = row.get("Porosity (%)", None)
    conductivity = row.get("Ionic Conductivity (mS⋅cm−1)", None)

    try:
        porosity = float(porosity)
    except (ValueError, TypeError):
        porosity = None

    try:
        conductivity = float(conductivity)
    except (ValueError, TypeError):
        conductivity = None

    # Parse thermal stability (take first number)
    thermal_val = None
    for char_group in thermal.split():
        try:
            thermal_val = float(char_group)
            break
        except ValueError:
            continue

    if material:
        lit2_data.append({
            "source_polymer": material,
            "lit_porosity": porosity,
            "lit_thermal_stability_C": thermal_val,
            "lit_ionic_conductivity": conductivity,
            "source": "PMC11241740"
        })

df_lit2_parsed = pd.DataFrame(lit2_data)
print(f"  PMC11241740: {len(df_lit2_parsed)} rows (material, tensile, thermal stability, porosity)")

# --- PMC11511470 Tables 1-3: Electrospun PVDF variants ---
# Has: solution, porosity, electrolyte uptake, ionic conductivity, tensile strength
lit3_data = []
for tbl in ["table1", "table2", "table3"]:
    df_lit3 = pd.read_csv(f"data/literature_raw/literature_PMC11511470_{tbl}.csv")
    for _, row in df_lit3.iterrows():
        # First column is the separator name
        first_col = list(df_lit3.columns)[0]
        material = str(row.get(first_col, "")).strip()
        porosity = row.get("Porosity/%", None)
        uptake = row.get("Electrolyte Uptake/%", None)
        conductivity = row.get("IonicConductivity/(mS cm−1)", None)

        try:
            porosity = float(porosity)
        except (ValueError, TypeError):
            porosity = None

        try:
            conductivity = float(conductivity)
        except (ValueError, TypeError):
            conductivity = None

        try:
            uptake = float(uptake)
        except (ValueError, TypeError):
            uptake = None

        if material:
            lit3_data.append({
                "source_polymer": material,
                "lit_porosity": porosity,
                "lit_electrolyte_uptake": uptake,
                "lit_ionic_conductivity": conductivity,
                "source": "PMC11511470"
            })

df_lit3_parsed = pd.DataFrame(lit3_data)
print(f"  PMC11511470: {len(df_lit3_parsed)} rows (PVDF variants, porosity, uptake, conductivity)")

# --- PMC12073824 Table 0: PPS separator variants ---
df_lit4 = pd.read_csv("data/literature_raw/literature_PMC12073824_table0.csv")

lit4_data = []
for _, row in df_lit4.iterrows():
    separator = str(row.get("Separator", "")).strip()
    porosity = row.get("Porosity (%)", None)
    uptake = row.get("Electrolyte Uptake (%)", None)
    conductivity = row.get("Ionic Conductivity (mS⋅cm−1)", None)

    try:
        porosity = float(porosity)
    except (ValueError, TypeError):
        porosity = None

    try:
        conductivity = float(conductivity)
    except (ValueError, TypeError):
        conductivity = None

    try:
        uptake = float(uptake)
    except (ValueError, TypeError):
        uptake = None

    if separator:
        lit4_data.append({
            "source_polymer": separator,
            "lit_porosity": porosity,
            "lit_electrolyte_uptake": uptake,
            "lit_ionic_conductivity": conductivity,
            "source": "PMC12073824"
        })

df_lit4_parsed = pd.DataFrame(lit4_data)
print(f"  PMC12073824: {len(df_lit4_parsed)} rows (PPS variants, porosity, uptake, conductivity)")

# --- PMC6161240 Tables 2-5: PVDF separator variants ---
lit5_data = []
for tbl in ["table2", "table3", "table4", "table5"]:
    df_lit5 = pd.read_csv(f"data/literature_raw/literature_PMC6161240_{tbl}.csv")
    for _, row in df_lit5.iterrows():
        material = str(row.get("Materials", "")).strip()
        porosity_uptake = str(row.get("Porosity and Uptake (%)", ""))

        if material:
            lit5_data.append({
                "source_polymer": material,
                "lit_porosity_uptake_raw": porosity_uptake,
                "source": "PMC6161240"
            })

df_lit5_parsed = pd.DataFrame(lit5_data)
print(f"  PMC6161240: {len(df_lit5_parsed)} rows (PVDF variants, porosity/uptake)")

# ============================================================
# STEP 4: Combine all literature data into one reference table
# ============================================================

# Stack all literature data
all_lit = pd.concat([
    df_lit1_parsed[["source_polymer", "lit_porosity", "lit_ionic_conductivity", "source"]],
    df_lit2_parsed[["source_polymer", "lit_porosity", "lit_ionic_conductivity", "source"]],
    df_lit3_parsed[["source_polymer", "lit_porosity", "lit_ionic_conductivity", "source"]],
    df_lit4_parsed[["source_polymer", "lit_porosity", "lit_ionic_conductivity", "source"]],
], ignore_index=True)

print(f"\nStep 4: Combined {len(all_lit)} literature entries")

# Map literature substrate names to our training polymer names
substrate_to_polymer = {
    "PE": "PE", "PP": "PP", "UHMWPE": "UHMWPE",
    "PVDF": "PVDF", "PVDF-HFP": "PVDF", "PAN": "PAN",
    "PPS": "PPS", "PI": "PI", "PET": "PET",
    "Cellulose": "cellulose", "cellulose": "cellulose",
    "MFC": "cellulose", "BC": "cellulose",
    "PVDF/PAN": "PVDF", "PAN/PVDF": "PAN",
    "PVDF-HFP/PMIA": "PVDF",
    "PAN@PVDF-HFP": "PAN",
}

all_lit["base_polymer"] = all_lit["source_polymer"].map(substrate_to_polymer)

# Compute average literature properties per base polymer
lit_avg = all_lit.groupby("base_polymer").agg(
    lit_avg_porosity=("lit_porosity", "mean"),
    lit_avg_conductivity=("lit_ionic_conductivity", "mean"),
    lit_n_sources=("source", "count")
).reset_index()

print(f"\nLiterature averages per base polymer:")
print(lit_avg.to_string())

# ============================================================
# STEP 5: Merge literature properties into training data
# ============================================================

df_training = df_training.merge(
    lit_avg,
    left_on="polymer",
    right_on="base_polymer",
    how="left"
).drop(columns="base_polymer")

# Fill NaN for polymers without literature data
df_training["lit_avg_porosity"] = df_training["lit_avg_porosity"].fillna(
    df_training["lit_avg_porosity"].median()
)
df_training["lit_avg_conductivity"] = df_training["lit_avg_conductivity"].fillna(
    df_training["lit_avg_conductivity"].median()
)
df_training["lit_n_sources"] = df_training["lit_n_sources"].fillna(0)

print(f"\n=== Final Training Set: {len(df_training)} polymers ===")
all_features = key_features + ["lit_avg_porosity", "lit_avg_conductivity"]
print(df_training[["polymer", "shutdown_temp_C", "safety"] + all_features].to_string())

print(f"\n=== Safety Label Distribution ===")
print(df_training["safety"].value_counts())

print(f"\n=== Features ({len(all_features)}) ===")
for f in all_features:
    n_valid = df_training[f].notna().sum()
    print(f"  {f}: {n_valid}/{len(df_training)} non-null")

# Save
df_training.to_csv("data/training_data.csv", index=False)
print("\nSaved to data/training_data.csv")
