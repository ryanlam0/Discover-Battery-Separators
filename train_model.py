"""
Part 3: Training the KNN Model and Screening Polymers

Step 1: Load training data and set up features/labels
Step 2: Build pipeline (StandardScaler + KNeighborsClassifier)
Step 3: Cross-validation to evaluate model
Step 4: GridSearchCV to tune hyperparameters
Step 5: Confusion matrix, precision, recall, F1
Step 6: Screen OpenPoly polymers for new separator candidates
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import confusion_matrix, f1_score

# --- Step 1: Load training data ---
df_training = pd.read_csv("data/training_data.csv")

key_features = ["Tg (K)", "Tm (K)", "Td (K)",
                "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                "Elongation at Break (%)"]

X_train = df_training[key_features]
y_train = df_training["safety"]

print(f"Training set: {len(X_train)} polymers, {len(key_features)} features")
print(f"Labels: {y_train.value_counts().to_dict()}")

# --- Step 2: Build pipeline ---
pipeline = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5, metric="euclidean")
)

# --- Step 3: Cross-validation ---
print("\n=== Cross-Validation (k=5) ===")

# Accuracy
scores_acc = cross_val_score(
    pipeline, X_train, y_train,
    scoring="accuracy", cv=5
)
print(f"Accuracy:  {scores_acc.mean():.3f} (+/- {scores_acc.std():.3f})")

# F1 macro (better for imbalanced classes)
scores_f1 = cross_val_score(
    pipeline, X_train, y_train,
    scoring="f1_macro", cv=5
)
print(f"F1 (macro): {scores_f1.mean():.3f} (+/- {scores_f1.std():.3f})")

# --- Step 4: GridSearchCV to find best k ---
print("\n=== Hyperparameter Tuning ===")

grid_cv = GridSearchCV(
    pipeline,
    param_grid={
        "kneighborsclassifier__n_neighbors": range(1, 12),
        "kneighborsclassifier__metric": ["euclidean", "manhattan"],
    },
    scoring="f1_macro",
    cv=5
)

grid_cv.fit(X_train, y_train)
print(f"Best params: {grid_cv.best_params_}")
print(f"Best F1 (macro): {grid_cv.best_score_:.3f}")

# Plot validation scores for different k values
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

results = pd.DataFrame(grid_cv.cv_results_)
fig, ax = plt.subplots()
for metric in ["euclidean", "manhattan"]:
    mask = results["param_kneighborsclassifier__metric"] == metric
    subset = results[mask].sort_values("param_kneighborsclassifier__n_neighbors")
    subset.plot.line(
        x="param_kneighborsclassifier__n_neighbors",
        y="mean_test_score",
        label=metric,
        ax=ax
    )
# Label the best F1 point
best_k = grid_cv.best_params_["kneighborsclassifier__n_neighbors"]
best_metric = grid_cv.best_params_["kneighborsclassifier__metric"]
best_f1 = grid_cv.best_score_
ax.annotate(f"Best: k={best_k}, {best_metric}\nF1 = {best_f1:.3f}",
            xy=(best_k, best_f1),
            xytext=(best_k - 2, best_f1 - 0.06),
            fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black"),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
ax.scatter([best_k], [best_f1], color="black", zorder=5, s=60)

ax.set_xlabel("k (number of neighbors)")
ax.set_ylabel("F1 Score (macro)")
ax.set_title("Model Selection: F1 vs k")
ax.legend()
fig.savefig("figures/model_selection.png", dpi=150, bbox_inches="tight")
print("Saved figures/model_selection.png")

# --- Step 5: Confusion matrix and classification report ---
print("\n=== Training Confusion Matrix (best model) ===")

# Fit the best model on all training data
best_pipeline = grid_cv.best_estimator_
y_train_pred = best_pipeline.predict(X_train)

cm = confusion_matrix(y_train, y_train_pred, labels=["safe", "unsafe"])
print(f"Labels: [safe, unsafe]")
print(cm)

# Precision and recall per class
print("\n=== Per-Class Metrics ===")
for label in ["safe", "unsafe"]:
    y_true_binary = (y_train == label)
    y_pred_binary = (y_train_pred == label)
    tp = (y_true_binary & y_pred_binary).sum()
    fp = (~y_true_binary & y_pred_binary).sum()
    fn = (y_true_binary & ~y_pred_binary).sum()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 / (1/precision + 1/recall) if (precision > 0 and recall > 0) else 0
    print(f"  {label:10s}  precision={precision:.3f}  recall={recall:.3f}  F1={f1:.3f}")

# --- Step 6: Screen OpenPoly polymers ---
print("\n=== Screening OpenPoly Polymers ===")

df_polymers = pd.read_csv("data/final_polymer_properties_fromliterature.csv")

# Get polymers with complete base features that are NOT in our training set
base_features = ["Tg (K)", "Tm (K)", "Td (K)",
                 "Tensile Strength (MPa)", "Young's Modulus (MPa)",
                 "Elongation at Break (%)"]
training_names = df_training["polymer"].str.lower().tolist()
df_screen = df_polymers.dropna(subset=base_features).copy()
df_screen = df_screen[~df_screen["Name"].str.lower().isin(training_names)]

print(f"Polymers available to screen: {len(df_screen)}")

X_screen = df_screen[key_features]
df_screen["predicted_safety"] = best_pipeline.predict(X_screen)
df_screen["predicted_proba_safe"] = best_pipeline.predict_proba(X_screen)[:,
    list(best_pipeline.classes_).index("safe")]

# Sort by probability of being safe
df_screen = df_screen.sort_values("predicted_proba_safe", ascending=False)

print("\n=== Top 20 Predicted SAFE Separator Candidates ===")
top_safe = df_screen[df_screen["predicted_safety"] == "safe"].head(20)
print(top_safe[["Name", "predicted_safety", "predicted_proba_safe"] + key_features].to_string())

print("\n=== Predicted UNSAFE Polymers (avoid as separators) ===")
fails = df_screen[df_screen["predicted_safety"] == "unsafe"]
print(fails[["Name", "predicted_safety", "predicted_proba_safe"] + key_features].to_string())

print("\n=== Screening Summary ===")
print(df_screen["predicted_safety"].value_counts())

# Save full screening results
df_screen.to_csv("data/screening_results.csv", index=False)
print("\nSaved to data/screening_results.csv")

# --- Visualization: where do candidates sit in property space? ---
import plotly.express as px

# Build combined DataFrame for plotly
df_screen_plot = df_screen[["Tg (K)", "Tm (K)", "Name", "predicted_safety"]].copy()
df_screen_plot["group"] = "Predicted " + df_screen_plot["predicted_safety"]

df_train_plot = df_training[["Tg (K)", "Tm (K)", "polymer", "safety"]].copy()
df_train_plot = df_train_plot.rename(columns={"polymer": "Name"})
df_train_plot["group"] = "Known " + df_train_plot["safety"]

df_all_plot = pd.concat([df_screen_plot, df_train_plot], ignore_index=True)

fig = px.scatter(df_all_plot, x="Tg (K)", y="Tm (K)", color="group",
                 hover_data=["Name"],
                 title="Separator Safety Prediction: Known vs. Screened Polymers",
                 color_discrete_map={
                     "Predicted safe": "lightgreen",
                     "Predicted unsafe": "lightsalmon",
                     "Known safe": "green",
                     "Known unsafe": "red",
                 })
fig.write_image("figures/screening_results.png", scale=2)
print("Saved figures/screening_results.png")
