# Results

Results of the LLM risk assessment experiments and the comparison with a classical ML model. For how the metrics are computed, see the [README](README.md#evaluation). All LLM numbers come from [`results/experiments.csv`](results/experiments.csv); the SVM numbers come from `src/svm_baseline.py`.

---

## Prompt development (dev set, Gemini `gemini-3.5-flash-lite`)

| Version | Change | Prompt hash | n (failed) | Accuracy - category | Accuracy - risk |
|---|---|---|---|---|---|
| v1 | system prompt + 3 few-shot examples | `8254781f` | 99 (1) | 0.73 | 0.83 |
| v2 | "high systolic and diastolic blood pressure" in the HIGH example | `a6102bde` | 100 (0) | 0.74 | 0.83 |
| v3 | category guide with blood pressure thresholds and Heart disease criteria | `4545e589` | 99 (1) | 0.81 | 0.85 |
| v4 | rule separating Heart disease from Hypertension + Diabetes | `55d8c9b0` | 100 (0) | **0.83** | **0.86** |

Baseline (always the most frequent class) on dev: 0.35.

The biggest problem of v1 was that the model **never predicted *Heart disease*** (recall 0.00); it labelled those patients as *Hypertension* or *Hypertension + Diabetes* (see the v1 details below). Versions v3 and v4 add explicit descriptions of the categories, which raised category accuracy from 0.73 to 0.83.

---

## Final test: LLM vs classical model (test set, 100 patients)

| Model | Accuracy - category | Accuracy - risk |
|---|---|---|
| Baseline (most frequent class) | 0.35 | - |
| SVM without scaling | 0.57 | - |
| **SVM (StandardScaler + SVC)**, trained on dev | **0.84** | - |
| **LLM, prompt v4** | **0.84** | 0.84 |

Per diagnosis (test):

| Diagnosis | Support | LLM v4 Precision | LLM v4 Recall | LLM v4 F1 | SVM Precision | SVM Recall | SVM F1 |
|---|---|---|---|---|---|---|---|
| Healthy | 35 | 0.92 | 1.00 | 0.96 | 1.00 | 1.00 | 1.00 |
| Hypertension | 18 | 0.71 | 0.83 | 0.77 | 0.75 | 0.83 | 0.79 |
| Diabetes | 13 | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 | 0.96 |
| Hypertension + Diabetes | 12 | 0.65 | 0.92 | 0.76 | 0.70 | 0.58 | 0.64 |
| Heart disease | 22 | 0.91 | **0.45** | 0.61 | 0.65 | **0.68** | 0.67 |

On the test set the LLM found only 10 of the 22 *Heart disease* patients (6 labelled *Hypertension*, 6 *Hypertension + Diabetes*), while the SVM found 15. The LLM is better on *Hypertension + Diabetes* and *Diabetes*. All *Heart disease* patients the LLM missed still got risk level `HIGH` except one, which is why its risk accuracy stays at 0.84.

---

## Comparison

- **Same accuracy.** On the test set, the LLM with prompt v4 and the SVM both reach 0.84, well above the 0.35 baseline.
- **Overall accuracy holds on test, but not for every class.** The LLM scored 0.83 on dev and 0.84 on test, so overall the prompt generalizes. However, *Heart disease* recall dropped from 0.70 (dev) to 0.45 (test): the thresholds added in v4 (age, blood pressure, cholesterol) were chosen by looking at dev patients and fit them better than new ones.
- **What each model needs.** The SVM learns from 100 labelled dev patients. The LLM saw only 3 fictional examples plus written category rules; however, those rules were written by looking at the dev errors, so the dev set was used by both approaches.
- **Scaling matters for SVM.** Without `StandardScaler`, SVM accuracy drops from 0.84 to 0.57, because columns with large values (cholesterol, blood pressure) dominate the 0/1 columns (smoker, diabetes).
- **Cost and speed.** The SVM trains and predicts in milliseconds, locally and for free. The LLM needs an API call per patient (about 20 minutes for 100 patients on the free tier) and its answers are not fully deterministic.
- **Output.** The SVM returns only a class. The LLM also returns a risk level, the risk factors it noticed and a recommendation in natural language, which is easier for a person to read and check.

On this small, structured, synthetic dataset a classical model is just as accurate and much cheaper. The LLM's advantage is the explanation it gives with each answer, and that it needs no training data.

---

## Details per prompt version (dev set)

Precision / Recall / F1 for each diagnosis, computed from `results/results_<version>_dev.csv`.

| Diagnosis | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Healthy | 0.97 / 1.00 / 0.99 | 0.97 / 1.00 / 0.99 | 0.97 / 1.00 / 0.99 | 0.95 / 1.00 / 0.97 |
| Hypertension | 0.59 / 0.94 / 0.73 | 0.59 / 0.94 / 0.73 | 0.87 / 0.76 / 0.81 | 0.83 / 0.59 / 0.69 |
| Diabetes | 0.75 / 1.00 / 0.86 | 0.86 / 1.00 / 0.92 | 0.79 / 0.92 / 0.85 | 0.80 / 1.00 / 0.89 |
| Hypertension + Diabetes | 0.48 / 0.77 / 0.59 | 0.48 / 0.85 / 0.61 | 0.53 / 0.77 / 0.62 | 0.71 / 0.77 / 0.74 |
| Heart disease | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | 0.75 / 0.52 / 0.62 | 0.73 / 0.70 / 0.71 |

Where the 23 *Heart disease* dev patients ended up:

| Predicted as | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Heart disease | 0 | 0 | 12 | 16 |
| Hypertension | 11 | 11 | 2 | 2 |
| Hypertension + Diabetes | 11 | 12 | 8 | 4 |
| Diabetes | 1 | 0 | 1 | 1 |

- **v1 → v2:** almost no change; the model still never predicts *Heart disease*.
- **v3:** the category guide makes the model predict *Heart disease* for the first time (12 of 23), but some *Hypertension* patients are now also labelled *Heart disease* (Hypertension recall 0.94 → 0.76).
- **v4:** the extra rule moves more patients from *Hypertension + Diabetes* to *Heart disease* (16 of 23). The cost is *Hypertension*: 5 of 17 are now labelled *Heart disease* (recall 0.59).
