# src/run_all.py
#%%
import sys
import pandas as pd
from config import PROVIDER, PROJECT_ROOT
from prompts import PROMPT_HASH, save_prompt
if PROVIDER == "gemini":
    from analyze_gemini import analyze_patient
else:
    from analyze import analyze_patient
args = [a for a in sys.argv[1:] if not a.startswith("-")] # skip Jupyter's own "--f=..." argument
#args = []
#for a in sys.argv[1:]:
#    if not a.startswith("-"):
#        args.append(a)

VERSION = args[0] if len(args) > 0 else "v1"
# for a quick test: python src/run_all.py v1 3   ("all" = every patient)
COUNT = int(args[1]) if len(args) > 1 and args[1] != "all" else None
#COUNT = 2
SPLIT = args[2] if len(args) > 2 else "dev" # "dev" or "test"

df = pd.read_csv(PROJECT_ROOT / "data" / f"{SPLIT}.csv")
if COUNT:
    df = df.head(COUNT)

prompt_file = save_prompt(PROJECT_ROOT / "results" / "prompts")
print(f"Prompt hash: {PROMPT_HASH} (text saved in {prompt_file})")

results = []
for i, (_, row) in enumerate(df.iterrows(), start=1):
    response = analyze_patient(row) or {}
    print(f"{i}/{len(df)} {row['patient_id']} -> {response.get('risk_level')}")
    results.append({
        "patient_id": row["patient_id"],
        "llm_risk": response.get("risk_level"),
        "llm_category": response.get("likely_category"),
        "llm_factors": "; ".join(response.get("risk_factors", [])),
        "llm_recommendation": response.get("recommendation"),
    })
output = df.merge(pd.DataFrame(results), on="patient_id")
output["prompt_hash"] = PROMPT_HASH  # which prompt produced these answers
output_path = PROJECT_ROOT / "results" / f"results_{VERSION}_{SPLIT}.csv"
output.to_csv(output_path, index=False)
print(f"Saved: {output_path}")

# %%
