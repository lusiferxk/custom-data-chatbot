# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
# import os

# from dotenv import load_dotenv
# load_dotenv()

# app = FastAPI()

# API_KEY = os.environ.get("GEMINI_API_KEY") 

# if not API_KEY:
#     raise ValueError("No API Key found! Please check your .env file.")

# client = genai.Client(api_key=API_KEY)

# print("Uploading knowledge base...")
# file_ref = client.files.upload(file="knowledge_base.pdf", config={'display_name': 'My App Data'})

# SYSTEM_INSTRUCTION = """
# You are a helpful assistant for a mobile app.
# 1. Answer ONLY using the provided file context.
# 2. If the answer is not in the file, say "I don't have that information."
# 3. Keep answers short (under 3 sentences) optimized for mobile screens.
# """

# class ChatRequest(BaseModel):
#     question: str

# @app.post("/chat")
# def chat_endpoint(request: ChatRequest):
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=[file_ref, request.question],
#             config=types.GenerateContentConfig(
#                 system_instruction=SYSTEM_INSTRUCTION,
#                 temperature=0.3
#             )
#         )
#         return {"reply": response.text}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# def health_check():
#     return {"status": "running"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")
FILE_URI = os.environ.get("GEMINI_FILE_URI")

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
            model="gemini-2.5-flash",
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "running"}