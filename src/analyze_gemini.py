import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from config import GEMINI_MODEL, MAX_TOKENS, GEMINI_PAUSE
from prompts import SYSTEM_PROMPT, FEW_SHOT_MESSAGES, describe_patient
from utils import extract_json
load_dotenv() # loads GEMINI_API_KEY from .env
client = genai.Client() # reads GEMINI_API_KEY (or GOOGLE_API_KEY) by itself
def _to_gemini_messages(messages):
    # Gemini calls the "assistant" role "model"
    return [
        types.Content(role="model" if m["role"] == "assistant" else "user",
                      parts=[types.Part(text=m["content"])])
        for m in messages
    ]
def analyze_patient(patient, attempts=3):
    messages = FEW_SHOT_MESSAGES + [{"role": "user", "content": describe_patient(patient)}]
    for _ in range(attempts):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=_to_gemini_messages(messages),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=MAX_TOKENS,
                    response_mime_type="application/json", # asks for pure JSON
                ),
            )
            if not response.text:
                raise ValueError("empty response")
            data = extract_json(response.text)
            time.sleep(GEMINI_PAUSE) # respect the free tier requests-per-minute limit
            return data
        except ValueError: # also covers json.JSONDecodeError
            print(" invalid response, retrying...")
        except errors.APIError as e:
            print(f" API error ({e.code}), waiting 30s (probably the rate limit)...")
            time.sleep(30)
    return None
