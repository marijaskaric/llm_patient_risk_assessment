import time
import anthropic
from dotenv import load_dotenv
from config import MODEL, MAX_TOKENS
from prompts import SYSTEM_PROMPT, FEW_SHOT_MESSAGES, describe_patient
from utils import extract_json
load_dotenv() # loads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic() # reads the key from the environment by itself
def analyze_patient(patient, attempts=3):
    messages = FEW_SHOT_MESSAGES + [{"role": "user", "content": describe_patient(patient)}]
    for _ in range(attempts):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            return extract_json(response.content[0].text)
        except ValueError: # also covers json.JSONDecodeError
            print(" invalid JSON, retrying...")
        except anthropic.APIError as e:
            print(f" API error: {e} (waiting 5s)")
            time.sleep(5)
    return None
