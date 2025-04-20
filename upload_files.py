import openai, glob, json, os
from dotenv import load_dotenv
load_dotenv()                  
client = openai.Client()

file_ids = []
for pdf_path in glob.glob("pdfs/*.pdf"):
    with open(pdf_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
        file_ids.append(uploaded.id)
        print(f"Uploaded {pdf_path} → {uploaded.id}")

json.dump(file_ids, open("file_ids.json", "w"))
print("Wrote file_ids.json with", len(file_ids), "entries")
