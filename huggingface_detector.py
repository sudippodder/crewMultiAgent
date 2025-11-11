import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/openai-community/roberta-base-openai-detector"

def detect_ai_generated(text: str, max_chars: int = 2000):
    if not HF_API_TOKEN:
        return {"error": "HF_API_TOKEN not set in .env file"}
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": text[:max_chars]}

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if resp.status_code == 410:
            return {"error": "Detection model endpoint is no longer available (410 Gone). Try a different model."}
        elif resp.status_code == 404:
            return {"error": "Model not found (404). Check model ID."}
        elif resp.status_code >= 400:
            return {"error": f"Hugging Face API error: {resp.status_code} {resp.reason}"}

        result = resp.json()
        if isinstance(result, list):
            scores = {item["label"]: item["score"] for item in result}
            # adapt keys for this model – may use 'Real'/'Fake' or 'Human'/'AI'
            ai_score = scores.get("Fake", 0.0) or scores.get("AI", 0.0)
            human_score = scores.get("Real", 0.0) or scores.get("Human", 0.0)
            verdict = "AI-generated" if ai_score > human_score else "Human-like"
            return {"ai_score": ai_score, "human_score": human_score, "verdict": verdict}

        if isinstance(result, dict) and result.get("error"):
            return {"error": result["error"]}

        return {"error": "Unexpected response format", "details": result}

    except Exception as e:
        return {"error": str(e)}
