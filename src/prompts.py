#%%
import hashlib
SYSTEM_PROMPT = '''You are an assistant for cardiometabolic risk assessment in an educational project.
Rules:
- Respond ONLY with a valid JSON object, without any additional text.
- Do not give a final diagnosis; provide a risk assessment and the most likely category.
- Risk factors and the recommendation are in English.
- The "recommendation" field has at most 2 sentences.
Category guide (for this educational dataset):
- Healthy: normal blood pressure, cholesterol and BMI, usually younger, active.
- Hypertension: both systolic and diastolic blood pressure elevated
  (roughly systolic >= 140 and diastolic >= 90), no diabetes.
- Diabetes: diabetes = Yes, blood pressure not markedly elevated.
- Hypertension + Diabetes: diabetes = Yes AND both systolic and diastolic
  blood pressure elevated.
- Heart disease: typically older (60+), both systolic and diastolic blood
  pressure high, together with several other risk factors (high cholesterol,
  high BMI, smoking, low activity). Choose it when risk factors clearly
  accumulate, even if diabetes is not present.
  Even if diabetes = Yes, choose Heart disease when the patient is
  older (about 60+) AND blood pressure is very high (about 158/97 or more) AND
  cholesterol is very high (about 255+). Otherwise, with diabetes, choose
  Hypertension + Diabetes.
Response format:
{
"risk_level": "LOW" | "MEDIUM" | "HIGH",
"likely_category": "Healthy" | "Hypertension" | "Diabetes"
| "Hypertension + Diabetes" | "Heart disease",
"risk_factors": ["...", "..."],
"recommendation": "..."
}'''
def describe_patient(p):
    # We intentionally do NOT send the patient ID or the diagnosis.
    return (
    "Patient data:\n"
    f"- Age: {p['age']}\n"
    f"- Sex: {p['sex']}\n"
    f"- Blood pressure: {p['systolic_bp']}/{p['diastolic_bp']}\n"
    f"- Cholesterol: {p['cholesterol']}\n"
    f"- BMI: {p['bmi']}\n"
    f"- Smoker: {p['smoker']}\n"
    f"- Diabetes: {p['diabetes']}\n"
    f"- Physical activity (hours per week): {p['weekly_activity_hours']}"
    )
# Few-shot examples: FICTIONAL patients (not from the CSV), so the evaluation isn't just "copying".
_EXAMPLES = [
(
dict(age=27, sex="F", systolic_bp=114, diastolic_bp=72,
cholesterol=172, bmi=21.4, smoker="No", diabetes="No",
weekly_activity_hours=6),
'{"risk_level": "LOW", "likely_category": "Healthy", '
'"risk_factors": ["no significant risk factors"], '
'"recommendation": "Continue an active lifestyle and regular check-ups."}',
),
(
dict(age=49, sex="F", systolic_bp=134, diastolic_bp=85,
cholesterol=221, bmi=26.9, smoker="No", diabetes="Yes",
weekly_activity_hours=2),
'{"risk_level": "MEDIUM", "likely_category": "Diabetes", '
'"risk_factors": ["diabetes", "mildly elevated cholesterol", "low physical activity"], '
'"recommendation": "A check-up with a doctor and regular blood sugar monitoring are recommended."}',
),
(
dict(age=66, sex="M", systolic_bp=168, diastolic_bp=103,
cholesterol=279, bmi=34.0, smoker="Yes", diabetes="Yes",
weekly_activity_hours=0),
'{"risk_level": "HIGH", "likely_category": "Heart disease", '
'"risk_factors": ["high systolic and diastolic blood pressure", "high cholesterol", "obesity", "smoking", '
'"diabetes", "no physical activity"], '
'"recommendation": "An urgent cardiology examination is needed."}',
),
]
FEW_SHOT_MESSAGES = []
for data, answer in _EXAMPLES:
    FEW_SHOT_MESSAGES.append({"role": "user", "content": describe_patient(data)})
    FEW_SHOT_MESSAGES.append({"role": "assistant", "content": answer})

# The whole prompt (system prompt + few-shot examples) as readable text,
# and a short fingerprint of it. Any change to the prompt gives a new hash.
PROMPT_TEXT = (
    "=== SYSTEM PROMPT ===\n" + SYSTEM_PROMPT + "\n\n=== FEW-SHOT EXAMPLES ===\n"
    + "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in FEW_SHOT_MESSAGES)
)
PROMPT_HASH = hashlib.md5(PROMPT_TEXT.encode()).hexdigest()[:8]

def save_prompt(folder):
    # Saves the prompt as <folder>/<hash>.txt, so every hash can be looked up later.
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{PROMPT_HASH}.txt"
    if not path.exists():
        path.write_text(PROMPT_TEXT, encoding="utf-8")
    return path

if __name__ == "__main__":
    print(SYSTEM_PROMPT)
    print(len(FEW_SHOT_MESSAGES))
    print(describe_patient(_EXAMPLES[0][0]))
# %%
