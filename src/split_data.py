import pandas as pd
from sklearn.model_selection import train_test_split
from config import CSV_PATH, PROJECT_ROOT

df = pd.read_csv(CSV_PATH)
dev, test = train_test_split(
    df, test_size=0.5, stratify=df["diagnosis"], random_state=42
)

dev.to_csv(PROJECT_ROOT / "data" / "dev.csv", index=False)
test.to_csv(PROJECT_ROOT / "data" / "test.csv", index=False)
print(len(dev), len(test))   # očekuješ 100 100