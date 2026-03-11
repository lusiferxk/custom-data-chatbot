# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
# import os

# from dotenv import load_dotenv
# load_dotenv()

# app = FastAPI()

# # env
# API_KEY = os.environ.get("GEMINI_API_KEY")
# FILE_ID = os.environ.get("GEMINI_FILE_URI") 
# MODEL = os.environ.get("MODEL")

# if FILE_ID and not FILE_ID.startswith("https://"):
#     FILE_URI = f"https://generativelanguage.googleapis.com/v1beta/{FILE_ID}"
# else:
#     FILE_URI = FILE_ID

# client = genai.Client(api_key=API_KEY)

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
#         print(f"Using File URI: {FILE_URI}")
        
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Part.from_uri(file_uri=FILE_URI, mime_type="application/pdf"), 
#                 request.question
#             ],
#             config=types.GenerateContentConfig(
#                 system_instruction=SYSTEM_INSTRUCTION,
#                 temperature=0.3
#             )
#         )
#         return {"reply": response.text}
#     except Exception as e:
#         print(f"Error: {e}") 
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/")
# def health_check():
#     return {"status": "running"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# env
API_KEY = os.environ.get("GEMINI_API_KEY")
FILE_ID = os.environ.get("GEMINI_FILE_URI") 
MODEL = os.environ.get("MODEL")

if FILE_ID and not FILE_ID.startswith("https://"):
    FILE_URI = f"https://generativelanguage.googleapis.com/v1beta/{FILE_ID}"
else:
    FILE_URI = FILE_ID

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
You are a helpful assistant for a mobile app.
1. Answer ONLY using the provided file context.
2. If the answer is not in the file, say "I don't have that information."
3. Keep answers short (under 3 sentences) optimized for mobile screens.
"""

class ChatRequest(BaseModel):
    question: str

# @app.post("/chat")
# def chat_endpoint(request: ChatRequest):
#     try:
#         print(f"Using File URI: {FILE_URI}")
#         print(f"Using Model: {MODEL}")
        
#         response = client.models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Part.from_uri(file_uri=FILE_URI, mime_type="application/pdf"), 
#                 request.question
#             ],
#             config=types.GenerateContentConfig(
#                 system_instruction=SYSTEM_INSTRUCTION,
#                 temperature=0.3
#             )
#         )
#         return {"reply": response.text}
        
#     except Exception as e:
#         # 1. Build a comprehensive error dictionary
#         error_details = {
#             "error_type": type(e).__name__,
#             "raw_error_string": str(e),
#             "inputs_used": {
#                 "model": MODEL,
#                 "file_uri_constructed": FILE_URI,
#                 "file_id_raw": FILE_ID
#             }
#         }
        
#         # 2. Extract hidden API attributes if they exist
#         if hasattr(e, 'message'):
#             error_details["api_message"] = getattr(e, 'message')
#         if hasattr(e, 'code'):
#             error_details["api_code"] = getattr(e, 'code')
#         if hasattr(e, 'details'):
#             error_details["api_details"] = getattr(e, 'details')
            
#         # 3. Dump all other attributes safely
#         try:
#             error_details["all_attributes"] = str(vars(e))
#         except Exception as dump_error:
#             error_details["all_attributes"] = f"Could not extract: {dump_error}"

#         # 4. Print to Vercel logs and send to Postman
#         print(f"CRITICAL ERROR DETAILS: {error_details}") 
#         raise HTTPException(status_code=500, detail=error_details)

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # 1. Fetch the actual file object. This proves the file exists and hasn't expired!
        # We use FILE_ID (e.g., "files/5aecxj1ymqv6") directly.
        document = client.files.get(name=FILE_ID)
        
        # 2. Check if it's ready (PDFs take time to process)
        if document.state.name == "PROCESSING":
            raise HTTPException(status_code=425, detail="Document is still processing on Google's servers. Try again in 10 seconds.")
        elif document.state.name == "FAILED":
            raise HTTPException(status_code=500, detail="Document failed to process. You may need to re-upload it.")

        # 3. Pass the document object DIRECTLY into the contents array
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                document,  # <-- Notice we pass the object directly, no 'Part.from_uri'
                request.question
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3
            )
        )
        return {"reply": response.text}

    except Exception as e:
        # Keeping your excellent error logging just in case
        print(f"Error Details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def health_check():
    return {"status": "running"}
