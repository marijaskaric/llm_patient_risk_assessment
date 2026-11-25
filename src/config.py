from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent # main project folder (one level above src/)
PROVIDER = "gemini" # "claude" or "gemini"
MODEL = "claude-sonnet-5-5"
GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_PAUSE = 10 # 7 # seconds between calls (free tier limit ~10 requests/min)
MAX_TOKENS = 600
CSV_PATH = PROJECT_ROOT / "data" / "synthetic_patients.csv" # works no matter where you run from
RISKS = ["LOW", "MEDIUM", "HIGH"]
CATEGORIES = [
"Healthy",
"Hypertension",
"Diabetes",
"Hypertension + Diabetes",
"Heart disease",
]
