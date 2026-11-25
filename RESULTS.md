# Results

Results of the LLM risk assessment experiments. For how the metrics are computed and what they mean, see the [README](README.md#evaluation). The raw log of every evaluation run is in [`results/experiments.csv`](results/experiments.csv).

---

## Initial run: v1, all 200 patients (before the dev/test split)

Gemini (`gemini-3.5-flash-lite`), 0 failed calls.

| Metric | Value |
|---|---|
| Baseline (most frequent class) | 0.35 |
| Accuracy - diagnosis category | **0.73** |
| Accuracy - risk level | **0.84** |

| Diagnosis | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Healthy | 0.99 | 1.00 | 0.99 | 70 |
| Hypertension | 0.60 | 0.97 | 0.74 | 35 |
| Diabetes | 0.81 | 0.88 | 0.85 | 25 |
| Hypertension + Diabetes | 0.47 | 0.84 | 0.60 | 25 |
| Heart disease | 0.00 | 0.00 | 0.00 | 45 |

**Observations:**
- The model is about twice as accurate as the baseline.
- *Healthy* patients are recognized almost perfectly.
- The model **never predicted *Heart disease***. Those 45 patients were assigned to other categories; the low precision of *Hypertension* (0.60) and *Hypertension + Diabetes* (0.47) suggests most of them ended up there; the dev run below confirms this. This is the main source of error and the first thing to address in the next prompt version.

---

## v1 on the dev set

Gemini (`gemini-3.5-flash-lite`), prompt `8254781f`, 99 of 100 patients evaluated (1 failed call).

| Metric | Value |
|---|---|
| Baseline (most frequent class) | 0.34 |
| Accuracy - diagnosis category | **0.73** |
| Accuracy - risk level | **0.83** |

| Diagnosis | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Healthy | 0.97 | 1.00 | 0.99 | 34 |
| Hypertension | 0.59 | 0.94 | 0.73 | 17 |
| Diabetes | 0.75 | 1.00 | 0.86 | 12 |
| Hypertension + Diabetes | 0.48 | 0.77 | 0.59 | 13 |
| Heart disease | 0.00 | 0.00 | 0.00 | 23 |

The dev results confirm the initial run. Of the 23 *Heart disease* patients, the model classified 11 as *Hypertension*, 11 as *Hypertension + Diabetes* and 1 as *Diabetes*; it never predicted *Heart disease*.

---

## Test results

*To be added after running the final prompt version on the test set.*
