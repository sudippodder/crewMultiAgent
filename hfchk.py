
from crew_pipeline import run_pipeline
from zerogpt_detector import detect_ai_generated_zerogpt
from dotenv import load_dotenv


load_dotenv()

#print(detect_ai_generated("This text is likely written by AI or not."))

result = detect_ai_generated_zerogpt("Artificial intelligence helps automate repetitive tasks.")
print(result)
