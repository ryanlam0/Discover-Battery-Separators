"""
Part 4: K-Means Clustering and Detailed Model Evaluation

Step 1: K-Means clustering on all polymers to discover natural groupings
Step 2: Compare clusters to safety labels
Step 3: Detailed confusion matrix visualization
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, cross_val_predict
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                             precision_score, recall_score, f1_score)

# --- Load data ---
df_training = pd.read_csv("data/39known_polymers(training_data).csv")
df_polymers = pd.read_csv("data/OpenPoly_polymers.csv")

# Features used for KNN classification (only OpenPoly properties
# that are available for both training and screening polymers)
knn_features = ["Tg (K)", "Tm (K)", "Td (K)",
                "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                "Elongation at Break (%)"]

# Features for clustering (same as KNN features)
cluster_features = knn_features

# =============================================
# PART A: K-Means Clustering
# =============================================

print("=" * 50)
print("K-MEANS CLUSTERING")
print("=" * 50)

# Use all polymers with complete data (training + screening pool)
df_all = df_polymers.dropna(subset=cluster_features).copy()
X_all = df_all[cluster_features]

print(f"Clustering {len(X_all)} polymers with complete data")

# Scale the data
scaler = StandardScaler()
scaler.fit(X_all)
X_all_scaled = scaler.transform(X_all)

# --- Try different numbers of clusters ---
# Use inertia (within-cluster sum of squares) to find the "elbow"
ks = range(2, 11)
inertias = []
for k in ks:
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X_all_scaled)
    inertias.append(model.inertia_)

# Elbow plot using pandas .plot.line()
df_elbow = pd.DataFrame({"k": list(ks), "Inertia": inertias})
ax = df_elbow.plot.line(x="k", y="Inertia", marker="o", legend=False)
ax.set_xlabel("k (number of clusters)")
ax.set_ylabel("Inertia (within-cluster sum of squares)")
ax.set_title("Elbow Plot for K-Means Clustering")
ax.get_figure().savefig("figures/elbow_plot.png", dpi=150, bbox_inches="tight")
print("Saved figures/elbow_plot.png")

# --- Fit K-Means with k=3 (elbow plot suggests k=3) ---
pipeline_km = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=3, random_state=42, n_init=10)
)

pipeline_km.fit(X_all)

kmeans_model = pipeline_km.named_steps["kmeans"]
clusters = kmeans_model.labels_
df_all["cluster"] = clusters

print(f"\nCluster sizes:")
print(pd.Series(clusters).value_counts().sort_index())

# --- Visualize clusters in Tg vs Tm space (plotly) ---
df_all["Cluster"] = df_all["cluster"].astype(str)
fig = px.scatter(df_all, x="Tg (K)", y="Tm (K)", color="Cluster",
                 title="K-Means Clusters (k=3) in Thermal Property Space",
                 hover_data=["Name"])
fig.write_image("figures/kmeans_clusters.png", scale=2)
print("Saved figures/kmeans_clusters.png")

# --- Compare clusters to known safety labels ---
# Merge cluster assignments with training data
df_training_clustered = df_training.merge(
    df_all[["Name", "cluster"]],
    left_on="polymer",
    right_on="Name",
    how="left"
)

print("\n=== Cluster vs. Safety Label (known separator polymers) ===")
crosstab = pd.crosstab(df_training_clustered["cluster"],
                       df_training_clustered["safety"])
print(crosstab)

# --- Visualize clusters overlaid with known safety labels (plotly) ---
# All points colored by cluster; known polymers get a different shape
cluster_colors = {"0": "#636EFA", "1": "#EF553B", "2": "#00CC96"}

# Background: all polymers as small circles, colored by cluster
fig = px.scatter(df_all, x="Tg (K)", y="Tm (K)", color="Cluster",
                 hover_data=["Name"],
                 color_discrete_map=cluster_colors,
                 title="K-Means Clusters vs. Known Safety Labels<br>(Clustered on all 6 properties, visualized in Tg vs Tm space)")
fig.update_traces(marker=dict(size=6, opacity=0.8))
fig.update_xaxes(title_text="Glass Transition Temperature (K)")
fig.update_yaxes(title_text="Melting Temperature (K)")

# Overlay known polymers: same cluster color, different shape
shape_map = {"safe": "square", "unsafe": "x"}
for label in ["safe", "unsafe"]:
    subset = df_training_clustered[df_training_clustered["safety"] == label]
    subset = subset.dropna(subset=["cluster"])
    colors = [cluster_colors[str(int(c))] for c in subset["cluster"]]
    fig.add_scatter(
        x=subset["Tg (K)"], y=subset["Tm (K)"],
        mode="markers",
        name=f"Known {label}",
        legendgroup=f"known_{label}",
        marker=dict(size=8, color=colors,
                    symbol=shape_map[label],
                    line=dict(width=1.5, color="black")),
        text=subset["polymer"], hoverinfo="text")

# Add dummy traces for a clean legend
for label in ["safe", "unsafe"]:
    fig.add_scatter(
        x=[None], y=[None], mode="markers",
        name=f"Known {label}",
        showlegend=True,
        marker=dict(size=8, color="black",
                    symbol=shape_map[label],
                    line=dict(width=1.5, color="black")),
    )

# Hide the real known traces from the legend
for trace in fig.data:
    if "Known" in trace.name and trace.x is not None and len(trace.x) > 1:
        trace.showlegend = False

fig.update_xaxes(range=[df_all["Tg (K)"].min() - 20, 600])
fig.update_yaxes(range=[df_all["Tm (K)"].min() - 20, 650])
fig.write_image("figures/clusters_vs_safety.png", scale=2)
print("Saved figures/clusters_vs_safety.png")


# =============================================
# PART B: Confusion Matrix Visualization
# =============================================

print("\n" + "=" * 50)
print("CONFUSION MATRIX")
print("=" * 50)

# Re-train the best KNN model
X_train = df_training[knn_features]
y_train = df_training["safety"]

pipeline_knn = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier()
)

# Use GridSearchCV to confirm best params
grid_cv = GridSearchCV(
    pipeline_knn,
    param_grid={
        "kneighborsclassifier__n_neighbors": range(1, 12),
        "kneighborsclassifier__metric": ["euclidean", "manhattan"],
    },
    scoring="f1_macro",
    cv=5
)
grid_cv.fit(X_train, y_train)

best_pipeline = grid_cv.best_estimator_
y_train_pred = best_pipeline.predict(X_train)

# --- Confusion matrix using sklearn's ConfusionMatrixDisplay ---
labels = ["safe", "unsafe"]
cm = confusion_matrix(y_train, y_train_pred, labels=labels)

print(f"\nConfusion Matrix (rows=actual, cols=predicted):")
print(f"Labels: {labels}")
print(cm)

fig, (ax_cm, ax_metrics) = plt.subplots(1, 2, figsize=(12, 5),
                                        gridspec_kw={"width_ratios": [1, 0.8]})

# Left: confusion matrix heatmap
disp = ConfusionMatrixDisplay(cm, display_labels=labels)
disp.plot(ax=ax_cm, cmap="Blues", values_format="d")
ax_cm.set_title("Confusion Matrix")

# Right: precision, recall, F1 table
ax_metrics.axis("off")
metrics_data = []
for label in labels:
    p = precision_score(y_train, y_train_pred, pos_label=label)
    r = recall_score(y_train, y_train_pred, pos_label=label)
    f = f1_score(y_train, y_train_pred, pos_label=label)
    metrics_data.append([label, f"{p:.3f}", f"{r:.3f}", f"{f:.3f}"])

table = ax_metrics.table(
    cellText=metrics_data,
    colLabels=["Class", "Precision", "Recall", "F1 Score"],
    loc="center",
    cellLoc="center"
)
table.auto_set_font_size(False)
table.set_fontsize(13)
table.scale(1, 2)
ax_metrics.set_title("Per-Class Metrics (Training)", fontsize=12)

fig.suptitle("KNN Separator Safety Classifier Performance",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/confusion_matrix.png", dpi=150, bbox_inches="tight")
print("Saved figures/confusion_matrix.png")

# =============================================
# PART C: Cross-Validation Confusion Matrix
# =============================================

print("\n" + "=" * 50)
print("CROSS-VALIDATION CONFUSION MATRIX")
print("=" * 50)

# Get out-of-fold predictions for each training polymer
y_cv_pred = cross_val_predict(best_pipeline, X_train, y_train, cv=5)

cm_cv = confusion_matrix(y_train, y_cv_pred, labels=labels)
print(f"\nCV Confusion Matrix (rows=actual, cols=predicted):")
print(cm_cv)

fig, (ax_cm, ax_metrics) = plt.subplots(1, 2, figsize=(12, 5),
                                        gridspec_kw={"width_ratios": [1, 0.8]})

# Left: CV confusion matrix heatmap
disp_cv = ConfusionMatrixDisplay(cm_cv, display_labels=labels)
disp_cv.plot(ax=ax_cm, cmap="Blues", values_format="d")
ax_cm.set_title("Cross-Validation Confusion Matrix", fontsize=14)
ax_cm.set_xlabel("Predicted Label", fontsize=13)
ax_cm.set_ylabel("True Label", fontsize=13)
ax_cm.tick_params(labelsize=12)

# Right: CV precision, recall, F1 table
ax_metrics.axis("off")
cv_metrics_data = []
for label in labels:
    p = precision_score(y_train, y_cv_pred, pos_label=label)
    r = recall_score(y_train, y_cv_pred, pos_label=label)
    f = f1_score(y_train, y_cv_pred, pos_label=label)
    cv_metrics_data.append([label, f"{p:.3f}", f"{r:.3f}", f"{f:.3f}"])

table = ax_metrics.table(
    cellText=cv_metrics_data,
    colLabels=["Class", "Precision", "Recall", "F1 Score"],
    loc="center",
    cellLoc="center"
)
table.auto_set_font_size(False)
table.set_fontsize(15)
table.scale(1, 2.2)

cv_macro_f1 = f1_score(y_train, y_cv_pred, average="macro")
ax_metrics.set_title("Per-Class Metrics (CV)", fontsize=14)
ax_metrics.text(0.5, 0.15, f"Cross-Val Macro F1 = {cv_macro_f1:.3f}",
                transform=ax_metrics.transAxes,
                ha="center", fontsize=16, fontweight="bold")

fig.suptitle("KNN Separator Safety Classifier — Cross-Validation Performance",
             fontsize=16, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/confusion_matrix_cv.png", dpi=150, bbox_inches="tight")
print("Saved figures/confusion_matrix_cv.png")

# --- Key insight: for safety, recall on "unsafe" matters most ---
print("\n=== Key Insight ===")
unsafe_recall = recall_score(y_train, y_cv_pred, pos_label="unsafe")
unsafe_missed = cm_cv[1, 0]
print(f"Unsafe recall (CV): {unsafe_recall:.3f}")
print(f"Dangerous polymers missed (predicted safe but actually unsafe): {unsafe_missed}")
print("In safety-critical applications, missing a dangerous polymer is worse")
print("than rejecting a safe one. Our model catches {:.0f}% of unsafe cases.".format(
    unsafe_recall * 100))
