from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")
FILE_ID = os.environ.get("GEMINI_FILE_URI") 

if FILE_ID and not FILE_ID.startswith("https://"):
    FILE_URI = f"https://generativelanguage.googleapis.com/v1beta/{FILE_ID}"
else:
    FILE_URI = FILE_ID
# -----------------------

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
You are a helpful assistant for a mobile app.
1. Answer ONLY using the provided file context.
2. If the answer is not in the file, say "I don't have that information."
3. Keep answers short (under 3 sentences) optimized for mobile screens.
"""

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Part.from_uri(file_uri=FILE_URI, mime_type="application/pdf"), 
                request.question
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3
            )
        )
        return {"reply": response.text}
    except Exception as e:
        print(f"Error: {e}") 
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def health_check():
    return {"status": "running"}