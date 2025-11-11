import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ZEROGPT_API_KEY = os.getenv("ZEROGPT_API_KEY")



ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"

def check_ai_content(text):
    headers = {
        "ApiKey": ZEROGPT_API_KEY,  # Must match exactly (case-sensitive)
        "Content-Type": "application/json",
    }

    payload = {
        "input_text": text
    }

    try:
        response = requests.post(ZEROGPT_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for non-2xx codes

        # ZeroGPT returns structured JSON
        result = response.json()
        # print("DEBUG RAW RESPONSE:", result)

        if "data" in result and result.get("success"):
            return result
        else:
            return {"error": f"Unexpected response structure: {result}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}


# Example test
if __name__ == "__main__":
    sample_text = """In the fiercely competitive global technology and business services landscape,
    India has quietly carved out a formidable edge that many outside observers often overlook..."""

    result = check_ai_content(sample_text)
    print(result)
