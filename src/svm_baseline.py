# src/svm_baseline.py
# Classical ML comparison: an SVM trained on the SAME dev/test split as the prompt,
# so "LLM with prompt" vs "classical model" is a fair comparison.
#%%
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from config import CATEGORIES, PROJECT_ROOT

X_COLS = ["age", "sex", "systolic_bp", "diastolic_bp",
          "cholesterol", "bmi", "smoker", "diabetes", "weekly_activity_hours"]

def prepare(d):
    # SVM needs numbers, so text columns are turned into 0/1
    d = d.copy()
    d["sex"] = d["sex"].map({"M": 1, "F": 0})
    d["smoker"] = d["smoker"].map({"Yes": 1, "No": 0})
    d["diabetes"] = d["diabetes"].map({"Yes": 1, "No": 0})
    if d[X_COLS].isnull().any().any():
        raise ValueError("unexpected value in sex/smoker/diabetes column")
    return d[X_COLS]

dev = pd.read_csv(PROJECT_ROOT / "data" / "dev.csv")
test = pd.read_csv(PROJECT_ROOT / "data" / "test.csv")

# SVM is sensitive to the scale of the columns (cholesterol ~200 vs smoker 0/1),
# so StandardScaler is required; without it the result is much worse.
svm = make_pipeline(StandardScaler(), SVC())
svm.fit(prepare(dev), dev["diagnosis"])

# for comparison: the same model without scaling
svm_no_scaling = SVC().fit(prepare(dev), dev["diagnosis"])

pred = svm.predict(prepare(test))
print(f"Trained on dev ({len(dev)}), evaluated on test ({len(test)})")
print(f"Baseline (always most frequent class): {test['diagnosis'].value_counts(normalize=True).max():.2f}")
print(f"SVM without scaling - accuracy: {accuracy_score(test['diagnosis'], svm_no_scaling.predict(prepare(test))):.2f}")
print(f"SVM with scaling    - accuracy: {accuracy_score(test['diagnosis'], pred):.2f}")
print()
print(classification_report(test["diagnosis"], pred, labels=CATEGORIES, zero_division=0))
# %%
