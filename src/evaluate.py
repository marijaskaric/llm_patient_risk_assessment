#%%

# src/evaluate.py
import sys
import csv, datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # save the figure to a file, don't open a window
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)
from config import CATEGORIES, PROJECT_ROOT, PROVIDER, MODEL, GEMINI_MODEL

# ASSUMPTION (document it in the README): how the true diagnosis maps to a risk level.
RISK_MAP = {
    "Healthy": "LOW",
    "Hypertension": "MEDIUM",
    "Diabetes": "MEDIUM",
    "Hypertension + Diabetes": "HIGH",
    "Heart disease": "HIGH",
}


def zapisi_eksperiment(verzija, skup, ulazni_fajl, prompt_hash, acc_cat, acc_risk,
                       baseline, n, failed):
    putanja = PROJECT_ROOT / "results" / "experiments.csv"
    novi = not putanja.exists()
    with open(putanja, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novi:
            w.writerow(["timestamp", "version", "dataset", "input_file", "provider", "model",
                        "prompt_hash", "n", "failed", "accuracy_category", "accuracy_risk",
                        "baseline"])
        w.writerow([
            datetime.datetime.now().isoformat(timespec="seconds"),
            verzija, skup, ulazni_fajl, PROVIDER,
            MODEL if PROVIDER == "claude" else GEMINI_MODEL,
            prompt_hash,
            n, failed, round(acc_cat, 3), round(acc_risk, 3), round(baseline, 3),
        ])
    return putanja


args = [a for a in sys.argv[1:] if not a.startswith("-")]  # skip Jupyter's own "--f=..." argument
version = args[0] if args else "v1"
split = args[1] if len(args) > 1 else "dev"  # "dev" or "test" - same split run_all.py used
results_dir = PROJECT_ROOT / "results"
input_file = f"results_{version}_{split}.csv"
df = pd.read_csv(results_dir / input_file)

# The hash was written by run_all.py when the model was run; the prompt text is in
# results/prompts/<hash>.txt. Older results files don't have this column.
prompt_hash = df["prompt_hash"].iloc[0] if "prompt_hash" in df.columns else "unknown"

failed = int(df[["llm_category", "llm_risk"]].isnull().any(axis=1).sum())
df = df.dropna(subset=["llm_category", "llm_risk"])
df["true_risk"] = df["diagnosis"].map(RISK_MAP)

# metrics - saved in variables so they can be printed AND logged
baseline = df["diagnosis"].value_counts(normalize=True).max()
acc_cat = accuracy_score(df["diagnosis"], df["llm_category"])
acc_risk = accuracy_score(df["true_risk"], df["llm_risk"])

print(f"Version: {version} | split: {split} | prompt: {prompt_hash} | "
      f"patients: {len(df)} | failed calls: {failed}")
print(f"Baseline (always most frequent class): {baseline:.2f}")
print(f"Accuracy - diagnosis category: {acc_cat:.2f}")
print(f"Accuracy - risk level: {acc_risk:.2f}")
print()
print(classification_report(df["diagnosis"], df["llm_category"],
                            labels=CATEGORIES, zero_division=0))

cm = confusion_matrix(df["diagnosis"], df["llm_category"], labels=CATEGORIES)
fig, ax = plt.subplots(figsize=(8, 7))
ConfusionMatrixDisplay(cm, display_labels=CATEGORIES).plot(
    ax=ax, xticks_rotation=30, colorbar=False)
ax.set_title(f"True vs predicted diagnosis ({version}, {split})")
plt.tight_layout()
out_png = results_dir / f"confusion_{version}_{split}.png"
plt.savefig(out_png, dpi=150)
print(f"Figure: {out_png}")

log_path = zapisi_eksperiment(version, split, input_file, prompt_hash, acc_cat, acc_risk,
                              baseline, len(df), failed)
print(f"Logged to: {log_path}")

# %%
