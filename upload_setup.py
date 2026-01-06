import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No API Key found!")

client = genai.Client(api_key=API_KEY)

print("Uploading knowledge base...")
file_ref = client.files.upload(file="knowledge_base.pdf", config={'display_name': 'My App Data'})

print(f"File Uploaded! SAVE THIS URI FOR VERCEL:")
print(f"FILE_URI: {file_ref.name}") 