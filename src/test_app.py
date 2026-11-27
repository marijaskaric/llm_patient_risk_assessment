import requests

patient = {
    "age": 64, "sex": "M", "systolic_bp": 163, "diastolic_bp": 101,
    "cholesterol": 268, "bmi": 32.8, "smoker": "Yes", "diabetes": "No",
    "weekly_activity_hours": 1,
}
respond = requests.post("http://127.0.0.1:8000/assess", json=patient)
print(respond.json())