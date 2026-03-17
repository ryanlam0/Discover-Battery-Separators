"""
Part 2: Building the Training Dataset

Step 1: Compile known separator polymers with safety labels
        (based on published thermal stability data from literature)
Step 2: Join with OpenPoly for 6 material properties (Tg, Tm, Td,
        tensile strength, Young's modulus, elongation at break)
"""

import pandas as pd
import numpy as np

# --- Load data sources ---
df_polymers = pd.read_csv("data/OpenPoly_polymers.csv")

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
# FINAL OUTPUT
# ============================================================

print(f"\n=== Final Training Set: {len(df_training)} polymers ===")
print(df_training[["polymer", "shutdown_temp_C", "safety"] + key_features].to_string())

print(f"\n=== Safety Label Distribution ===")
print(df_training["safety"].value_counts())

print(f"\n=== Features ({len(key_features)}) ===")
for f in key_features:
    n_valid = df_training[f].notna().sum()
    print(f"  {f}: {n_valid}/{len(df_training)} non-null")

# Note: Safety labels (safe/unsafe) were assigned based on published
# thermal stability data from PMC review articles. Polymers maintaining
# structural integrity above 150C are labeled "safe"; those failing at
# or below 150C are labeled "unsafe".

# Save
df_training.to_csv("data/39known_polymers(training_data).csv", index=False)
print("\nSaved to data/39known_polymers(training_data).csv")
