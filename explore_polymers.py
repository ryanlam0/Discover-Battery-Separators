"""
Part 1b & 1c: Loading and Exploring the OpenPoly Polymer Database

OpenPoly is a dataset of 741 polymers with 26 experimentally measured
properties. This will serve as our screening pool -- polymers that have
never been tested as battery separators.
"""

import pandas as pd
import numpy as np

# Load the OpenPoly dataset
df_polymers = pd.read_csv("data/final_polymer_properties_fromliterature.csv")
print(f"Shape: {df_polymers.shape}")
print(df_polymers.head())

# Properties relevant to battery separators
separator_relevant = [
    "Name", "Tg (K)", "Tm (K)", "Td (K)",
    "Tensile Strength (MPa)", "Young's Modulus (MPa)",
    "Elongation at Break (%)", "Thermal Conductivity (W/m K)",
    "Crystallization Temperature (K)", "Water Contact Angle (deg)",
    "Water Uptake (%)", "Hardness (MPa)", "Compressive Strength (MPa)"
]

df_relevant = df_polymers[separator_relevant]

# How much data do we have for each property?
print("\nData availability per property:")
print(df_relevant.drop(columns="Name").notna().sum().sort_values(ascending=False))

# Focus on the best-covered properties for modeling
# These are the features we can use for both training and screening
key_features = ["Tg (K)", "Tm (K)", "Td (K)",
                "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                "Elongation at Break (%)"]

# How many polymers have ALL of these properties?
df_complete = df_relevant.dropna(subset=key_features)
print(f"\nPolymers with all key properties: {len(df_complete)}")
print(df_complete)

# Let's look at the known separator polymers in this dataset
known_separator_names = ["PE", "PP", "PVDF", "PAN", "HDPE", "LDPE",
                         "polypropylene", "polyethylene",
                         "poly(vinylidene fluoride)", "polyacrylonitrile",
                         "cellulose", "PLA", "PET", "nylon", "PI",
                         "polyimide", "PTFE", "PVA"]

# Search for these in the Name column (case-insensitive)
mask = df_polymers["Name"].str.lower().isin([n.lower() for n in known_separator_names])
df_known = df_polymers[mask]
print(f"\nFound {len(df_known)} known separator-relevant polymers in OpenPoly:")
print(df_known[["Name"] + key_features])

# --- Visualizations ---

# Scatter plot: Tg vs Tm for all polymers
ax = df_polymers.plot.scatter(x="Tg (K)", y="Tm (K)", alpha=0.4,
                              color="gray", label="All polymers")

# Highlight known separator polymers
df_known.plot.scatter(x="Tg (K)", y="Tm (K)", alpha=0.9,
                      color="red", label="Known separator polymers", ax=ax)

ax.set_title("Thermal Properties of Polymers")
ax.legend()
ax.get_figure().savefig("figures/thermal_properties.png", dpi=150, bbox_inches="tight")
print("\nSaved figures/thermal_properties.png")

# Scatter plot: Tensile Strength vs Young's Modulus
ax = df_polymers.plot.scatter(x="Young's Modulus (MPa)",
                              y="Tensile Strength (MPa)",
                              alpha=0.4, color="gray",
                              label="All polymers")

df_known.plot.scatter(x="Young's Modulus (MPa)",
                      y="Tensile Strength (MPa)",
                      alpha=0.9, color="red",
                      label="Known separator polymers", ax=ax)

ax.set_title("Mechanical Properties of Polymers")
ax.legend()
ax.get_figure().savefig("figures/mechanical_properties.png", dpi=150, bbox_inches="tight")
print("Saved figures/mechanical_properties.png")
