from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import PROVIDER

if PROVIDER == "gemini":
    from analyze_gemini import analyze_patient
else:
    from analyze import analyze_patient


class Patient(BaseModel):
    age: int
    sex: str
    systolic_bp: int
    diastolic_bp: int
    cholesterol: int
    bmi: float
    smoker: str
    diabetes: str
    weekly_activity_hours: float


app = FastAPI(title="Patient risk assessment")


@app.post("/assess")
def assess(patient: Patient):
    result = analyze_patient(patient.model_dump())
    if result is None:
        raise HTTPException(status_code=502, detail="Model did not return a valid response")
    return result