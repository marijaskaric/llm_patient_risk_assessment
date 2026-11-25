#%%
import json
from config import RISKS
def extract_json(text):
    # The model sometimes adds text around the JSON; take everything between the first { and the last }.
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON in the response")
    data = json.loads(text[start:end + 1])
    if data.get("risk_level") not in RISKS:
        raise ValueError("unexpected value for risk_level")
    return data

# %%
