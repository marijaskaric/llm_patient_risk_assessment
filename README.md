# llm_patient_risk_assessment

Evaluating LLM-based cardiometabolic risk assessment on synthetic patient data (API, Python, pandas, scikit-learn).

An LLM (Gemini or Claude) receives basic clinical data about a patient and returns a **risk level** (`LOW` / `MEDIUM` / `HIGH`), the **most likely diagnosis category**, a list of risk factors and a short recommendation. The answers are then compared with the known diagnoses in the dataset to measure how accurate the model is.

> Educational project. The data is synthetic and the model's output is not medical advice.

---

## Project structure

```
llm_patient_risk_assessment/
├── data/
│   ├── synthetic_patients.csv   # all 200 synthetic patients
│   ├── dev.csv                  # 100 patients - for developing and tuning prompts
│   └── test.csv                 # 100 patients - only for the final measurement
├── results/
│   ├── results_<version>_<split>.csv   # model answers per patient (generated, not in git)
│   ├── confusion_<version>_<split>.png # confusion matrix (generated, not in git)
│   ├── prompts/<hash>.txt              # full text of every prompt used (generated, not in git)
│   └── experiments.csv                 # log of all evaluation runs
├── src/
│   ├── config.py          # settings: provider, model, categories, paths
│   ├── prompts.py         # system prompt, few-shot examples, patient description
│   ├── analyze.py         # one patient -> Claude API -> JSON answer
│   ├── analyze_gemini.py  # one patient -> Gemini API -> JSON answer
│   ├── utils.py           # extracts and validates JSON from the model's answer
│   ├── split_data.py      # splits the data into dev and test
│   ├── run_all.py         # runs the model on a whole dataset and saves results
│   └── evaluate.py        # computes accuracy, report and confusion matrix
├── check_env.py           # checks packages, API keys and data file
└── requirements.txt
```

---

## Data

Each patient in `data/synthetic_patients.csv` has:

| Column | Meaning |
|---|---|
| `patient_id` | ID, e.g. `P001` |
| `age`, `sex` | age and sex (`M`/`F`) |
| `systolic_bp`, `diastolic_bp` | blood pressure (mmHg) |
| `cholesterol` | total cholesterol (mg/dL) |
| `bmi` | body mass index |
| `smoker`, `diabetes` | `Yes` / `No` |
| `weekly_activity_hours` | physical activity per week |
| `diagnosis` | the true diagnosis (hidden from the model) |

The five diagnosis categories and their share in the data:

| Diagnosis | Patients | Share |
|---|---|---|
| Healthy | 70 | 35.0% |
| Heart disease | 45 | 22.5% |
| Hypertension | 35 | 17.5% |
| Diabetes | 25 | 12.5% |
| Hypertension + Diabetes | 25 | 12.5% |

### Dev / test split

`split_data.py` splits the 200 patients into two halves of 100 (`dev.csv` and `test.csv`), **stratified** by diagnosis so both halves have the same proportions of each category (`random_state=42`, so the split is always the same).

- **dev** is used while developing: changing the prompt, comparing versions v1, v2, ...
- **test** is used **only once at the end**, on the final version.

This way the final result is not "tuned" to the patients the prompt was developed on.

---

## How the model gets its answer

For each patient (`run_all.py` → `analyze_gemini.py` or `analyze.py`):

1. **Patient description** (`prompts.describe_patient`): the row from the CSV becomes text (age, sex, blood pressure, cholesterol, BMI, smoking, diabetes, activity). The **diagnosis and patient ID are intentionally not sent**, so the model cannot copy the answer.
2. **Prompt**: the model receives
   - `SYSTEM_PROMPT`: rules and the required JSON format,
   - `FEW_SHOT_MESSAGES`: 3 **fictional** example patients (not from the CSV) with correct answers, one each for LOW, MEDIUM and HIGH,
   - the description of the current patient.
3. **Answer**: the model returns JSON, for example:
   ```json
   {"risk_level": "MEDIUM", "likely_category": "Hypertension",
    "risk_factors": ["high blood pressure", "obesity"],
    "recommendation": "Consult a doctor about blood pressure."}
   ```
4. **Validation** (`utils.extract_json`): the JSON is extracted from the text and `risk_level` must be one of `LOW`, `MEDIUM`, `HIGH`. If the answer is invalid or the API returns an error, the call is retried up to 3 times (after an API error Gemini waits 30 s, Claude 5 s). If all attempts fail, the patient gets empty values (counted as a *failed call*).
5. **Saving**: the answers are added as columns `llm_risk`, `llm_category`, `llm_factors`, `llm_recommendation` and saved to `results/results_<version>_<split>.csv`, together with a `prompt_hash` column (see below).

### Prompt tracking

Before calling the model, `run_all.py` computes a short MD5 fingerprint of the whole prompt (system prompt + few-shot examples), e.g. `8254781f`, and saves the full prompt text to `results/prompts/<hash>.txt`. Any change to the prompt, even one character, gives a new hash and a new file.

The hash is stored in every results file and copied by `evaluate.py` into `experiments.csv`. To see which prompt produced a result, open `results/prompts/<hash>.txt` (these files exist only locally; they are not in git). Because the hash is recorded when the model is run (not when it is evaluated), editing the prompt between `run_all.py` and `evaluate.py` does not mix things up.

The model is **not** given any rules such as "blood pressure > 140 means MEDIUM". It decides the risk level from its general knowledge and the three examples.

---

## Evaluation

`evaluate.py` reads a results file and computes:

- **Failed calls**: patients without a model answer. They are counted first and then removed (`dropna`), so accuracy is computed only on patients who got an answer.
- **Baseline**: the accuracy of a trivial "model" that always predicts the most frequent class (`Healthy`, 0.35). The LLM is useful only if it is clearly above this.
- **Accuracy - diagnosis category**: `llm_category` vs `diagnosis` (5 classes).
- **Accuracy - risk level**: `llm_risk` vs `true_risk` (3 classes).
- **Classification report**: precision, recall and F1 for each diagnosis.
- **Confusion matrix**: which diagnoses the model confuses with which, saved as `results/confusion_<version>_<split>.png`.

### Experiment log

Every run of `evaluate.py` appends one row to `results/experiments.csv`, so different versions can be compared side by side:

| Column | Meaning |
|---|---|
| `timestamp` | when the evaluation was run |
| `version`, `dataset` | e.g. `v1`, `dev` |
| `input_file` | the results file that was evaluated |
| `provider`, `model` | e.g. `gemini`, `gemini-3.5-flash-lite` |
| `prompt_hash` | which prompt was used; the full text is in `results/prompts/<hash>.txt` (`unknown` for results created before prompt tracking) |
| `n`, `failed` | patients evaluated, failed calls |
| `accuracy_category`, `accuracy_risk`, `baseline` | the metrics above |

Re-running the evaluation for the same version adds a new row; the `timestamp` shows which one is the latest.

The per-patient results (`results_*.csv`), the saved prompts (`results/prompts/`) and the figures (`*.png`) are excluded from git (`.gitignore`); they are created locally by the commands below. Only `experiments.csv` is kept in git.

### Assumption: true risk level

The dataset contains a diagnosis but **no true risk level**. To evaluate `llm_risk`, the true risk is derived from the diagnosis with a fixed mapping (`RISK_MAP` in `evaluate.py`):

| Diagnosis | True risk |
|---|---|
| Healthy | LOW |
| Hypertension | MEDIUM |
| Diabetes | MEDIUM |
| Hypertension + Diabetes | HIGH |
| Heart disease | HIGH |

This is a **simplifying assumption of this project**, not a clinical standard. In reality, risk also depends on age, smoking, cholesterol and other factors (e.g. hypertension in an older smoker can be high risk). Changing this mapping changes the risk accuracy even if the model's answers stay the same.

Risk accuracy is usually higher than category accuracy because risk is a coarser division: if the model says *Hypertension + Diabetes* for a patient with *Heart disease*, the category is wrong but the risk (`HIGH`) is still correct.

---

## Setup

1. Create the conda environment and install packages:
   ```
   conda create -n llm-risk python
   conda activate llm-risk
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with your API key(s):
   ```
   GEMINI_API_KEY=...
   ANTHROPIC_API_KEY=...
   ```
3. Choose the provider in `src/config.py`: `PROVIDER = "gemini"` or `"claude"`.
4. Check that everything is in place:
   ```
   python check_env.py
   ```

> **Common error:** `ModuleNotFoundError: No module named 'pandas'` means the script was started with a Python that is not the `llm-risk` environment. Activate the environment (`conda activate llm-risk`), select it in VS Code (`Ctrl+Shift+P` → *Python: Select Interpreter* → *llm-risk*), or call its Python directly:
> ```powershell
> & "<path-to-anaconda>\envs\llm-risk\python.exe" src/run_all.py v1 3 dev
> ```

---

## Usage

```
python src/split_data.py               # once: creates data/dev.csv and data/test.csv

python src/run_all.py v1 3 dev         # quick test on 3 patients
python src/run_all.py v1 all dev       # the whole dev set
python src/evaluate.py v1 dev

python src/run_all.py v2 all test      # only at the end, with the final version
python src/evaluate.py v2 test
```

Arguments:

| Script | Arguments | Default |
|---|---|---|
| `run_all.py` | `<version> <count or "all"> <dev or test>` | `v1 all dev` |
| `evaluate.py` | `<version> <dev or test>` | `v1 dev` |

The version name (`v1`, `v2`, ...) is just a label for the output files. When the prompt changes, use a new version name so earlier results are not overwritten.

With Gemini's free tier there is a 10-second pause between calls (`GEMINI_PAUSE` in `config.py`), so 100 patients take about 20 minutes.

> **`API error (429), waiting 30s`** means the free-tier rate limit was hit. If it appears only now and then, the script waits and continues on its own. If it repeats for every patient (`-> None`), the daily quota is used up: stop the script (`Ctrl+C`) and run it again after the quota resets, otherwise all patients end up as failed calls.

The scripts can also be run in the VS Code Interactive Window (`#%%` cells). Jupyter's own `--f=...` argument is ignored.

---

## Limitations

- The data is **synthetic**; results do not show how the model would behave on real patients.
- The true risk level is **derived from the diagnosis** with an assumed mapping (see above).
- The prompt does not define what `LOW` / `MEDIUM` / `HIGH` mean (no criteria, no time horizon), so the model applies its own interpretation.
- LLM answers are not fully deterministic; repeating a run can give slightly different results.
- The model sees only 8 features; real diagnosis of heart disease requires much more information (ECG, symptoms, history...).
