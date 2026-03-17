"""
Part 5: Visualizing the Top Predicted Separator Candidates

Creates a focused plot showing the top new polymer candidates
predicted as safe separators, compared to known separator polymers.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px

# --- Load data ---
df_training = pd.read_csv("data/training_data.csv")
df_screen = pd.read_csv("data/screening_results.csv")

# Get candidates predicted safe (>50% probability)
df_top = df_screen[df_screen["predicted_proba_safe"] > 0.5].copy()
df_top = df_top.sort_values("predicted_proba_safe", ascending=False)

# Split candidates by confidence level
top_high = df_top[df_top["predicted_proba_safe"] == 1.0].copy()
top_mod = df_top[df_top["predicted_proba_safe"] < 1.0].copy()

# ============================================================
# PLOT 1: Top Candidates - Tg vs Tm (plotly scatter)
# ============================================================

# Build a combined DataFrame with group labels for plotly
safe_train = df_training[df_training["safety"] == "safe"][["Tg (K)", "Tm (K)", "polymer"]].copy()
safe_train = safe_train.rename(columns={"polymer": "Name"})
safe_train["group"] = "Known safe"

unsafe_train = df_training[df_training["safety"] == "unsafe"][["Tg (K)", "Tm (K)", "polymer"]].copy()
unsafe_train = unsafe_train.rename(columns={"polymer": "Name"})
unsafe_train["group"] = "Known unsafe"

top_high_plot = top_high[["Tg (K)", "Tm (K)", "Name"]].copy()
top_high_plot["group"] = "Top candidates (100% safe)"

top_mod_plot = top_mod[["Tg (K)", "Tm (K)", "Name"]].copy()
top_mod_plot["group"] = "Candidates (50-99% safe)"

df_plot = pd.concat([safe_train, unsafe_train, top_high_plot, top_mod_plot],
                    ignore_index=True)

fig = px.scatter(df_plot, x="Tg (K)", y="Tm (K)", color="group",
                 hover_data=["Name"],
                 title="Top Predicted Safe Separator Polymer Candidates",
                 color_discrete_map={
                     "Known safe": "green",
                     "Known unsafe": "red",
                     "Top candidates (100% safe)": "dodgerblue",
                     "Candidates (50-99% safe)": "lightskyblue",
                 })
# Label a curated set of top candidates with custom offsets to avoid overlap
label_offsets = {
    "PEKK":      (30, -25),
    "PEN":       (25, 15),
    "PGA":       (-60, -25),
    "polyimides": (30, 10),
    "PA 6":      (-55, 20),
    "PHB":       (-50, -20),
    "P(3HB)":    (30, -15),
    "PLLA":      (-55, 15),
    "PBO":       (25, 20),
    "nylon 6":   (30, -10),
}

for _, row in top_high.iterrows():
    if row["Name"] in label_offsets:
        ax_off, ay_off = label_offsets[row["Name"]]
        fig.add_annotation(
            x=row["Tg (K)"], y=row["Tm (K)"],
            text=row["Name"], showarrow=True,
            arrowhead=0, ax=ax_off, ay=ay_off,
            font=dict(size=10),
            bgcolor="white", bordercolor="gray", borderpad=2,
        )

fig.update_layout(width=900, height=650)
fig.update_xaxes(title_text="Glass Transition Temperature (K)")
fig.update_yaxes(title_text="Melting Temperature (K)")
fig.write_image("figures/top_candidates.png", scale=2)
print("Saved figures/top_candidates.png")

# ============================================================
# PLOT 2: Bar chart of top candidates ranked by key properties
# ============================================================

# Only use 100% safe candidates (all 7 neighbors voted safe)
top_100 = top_high[top_high["predicted_proba_safe"] == 1.0]
top_for_bar = top_100.drop_duplicates(subset="Name").copy()
top_for_bar = top_for_bar.set_index("Name")

# 6 real material properties (porosity & conductivity excluded — they are
# imputed medians for screening candidates, so every bar is identical)
properties = [
    ("Tg (K)", "Glass Transition Temp"),
    ("Tm (K)", "Melting Temp"),
    ("Td (K)", "Decomposition Temp"),
    ("Tensile Strength (MPa)", "Tensile Strength"),
    ("Young's Modulus (MPa)", "Young's Modulus"),
    ("Elongation at Break (%)", "Elongation at Break"),
]

# Also load known separator data for shared axes
key_separators = ["PP", "PVDF", "PAN", "PET", "PI", "PPS", "PEI",
                  "PA6", "PLA", "PTFE"]
known_safe = df_training[df_training["polymer"].isin(key_separators)].copy()
known_safe = known_safe.drop_duplicates(subset="polymer")
known_safe = known_safe.set_index("polymer")

# Compute shared x-axis limits across both datasets
shared_xlims = {}
for col, title in properties:
    all_vals = pd.concat([top_for_bar[col], known_safe[col]])
    shared_xlims[col] = (0, all_vals.max() * 1.1)

# --- Plot 2a: Candidate properties ---
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for i, (col, title) in enumerate(properties):
    ax = top_for_bar[[col]].plot.barh(ax=axes[i], legend=False)
    ax.set_title(title)
    ax.set_ylabel("")
    ax.set_xlim(shared_xlims[col])
    ax.invert_yaxis()

fig.suptitle("Top Predicted Safe Separator Candidates (100% confidence): Material Properties",
             fontsize=15, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/candidate_properties.png", dpi=150, bbox_inches="tight")
print("Saved figures/candidate_properties.png")

# --- Plot 2b: Known separator properties (same axes) ---
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for i, (col, title) in enumerate(properties):
    ax = known_safe[[col]].plot.barh(ax=axes[i], legend=False)
    ax.set_title(title)
    ax.set_ylabel("")
    ax.set_xlim(shared_xlims[col])
    ax.invert_yaxis()

fig.suptitle("Common Battery Separator Polymers: Material Properties",
             fontsize=15, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/known_separator_properties.png", dpi=150, bbox_inches="tight")
print("Saved figures/known_separator_properties.png")

# ============================================================
# PLOT 3: Radar chart — top candidates vs common separators
# ============================================================

radar_features = ["Tg (K)", "Tm (K)", "Td (K)",
                  "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                  "Elongation at Break (%)"]
radar_labels = ["Glass Transition Temp", "Melting Temp",
                "Decomposition Temp", "Tensile Strength",
                "Young's Modulus", "Elongation at Break"]

# Polymers to show: top 5 candidates + PI as baseline
candidate_names = ["polyimides", "PEKK", "PGA", "PEN", "PA 6"]

# Build a combined DataFrame of raw values
radar_rows = []
for name in candidate_names:
    if name in top_for_bar.index:
        row = top_for_bar.loc[name, radar_features]
        radar_rows.append({"polymer": name, **row.to_dict()})

# Add PI and PAN as known safe baselines
pi = df_training[df_training["polymer"] == "polyimide"].iloc[0]
radar_rows.append({"polymer": "PI (Known Separator)",
                   **{f: pi[f] for f in radar_features}})

pan = df_training[df_training["polymer"] == "PAN"].iloc[0]
radar_rows.append({"polymer": "PAN (Known Separator)",
                   **{f: pan[f] for f in radar_features}})

df_radar = pd.DataFrame(radar_rows)

# Normalize each feature to 0-1 range so they're comparable on the same axes
for f in radar_features:
    fmin = df_radar[f].min()
    fmax = df_radar[f].max()
    df_radar[f] = (df_radar[f] - fmin) / (fmax - fmin) if fmax > fmin else 0.5

# Reshape to long format for plotly (same pattern as px.scatter)
df_radar_long = df_radar.melt(id_vars="polymer", value_vars=radar_features,
                              var_name="property", value_name="value")

# Replace column names with readable labels
label_map = dict(zip(radar_features, radar_labels))
df_radar_long["property"] = df_radar_long["property"].map(label_map)

fig = px.line_polar(df_radar_long, r="value", theta="property",
                    color="polymer", line_close=True,
                    color_discrete_map={
                        "PI (Known Separator)": "#404040",
                        "PAN (Known Separator)": "#a0a0a0",
                    },
                    title="Top Candidates vs. Current Separators (Normalized)")
fig.update_traces(fill="toself", opacity=0.6, marker=dict(size=8))
fig.update_layout(width=900, height=650,
                  polar=dict(radialaxis=dict(visible=False),
                             angularaxis=dict(tickfont=dict(size=14))),
                  legend=dict(y=1.15, x=1.15, xanchor="left", font=dict(size=13)),
                  title_font_size=16)
fig.write_image("figures/radar_candidates.png", scale=2)
print("Saved figures/radar_candidates.png")
