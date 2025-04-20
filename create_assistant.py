import openai, json
from dotenv import load_dotenv
load_dotenv()

client = openai.Client()

# ------------------------------------------------------------------
# 1.  Load the PDF file IDs we previously uploaded
# ------------------------------------------------------------------
file_ids = json.load(open("file_ids.json"))

# ------------------------------------------------------------------
# 2.  Create (or reuse) a vector‑store that indexes those PDFs
# ------------------------------------------------------------------
vector_store = client.vector_stores.create(
    name     = "LawBotStore",
    file_ids = file_ids
)
print("Vector‑store ID:", vector_store.id)

# ------------------------------------------------------------------
# 3.  Create the Assistant and point its 'file_search' tool at the store
# ------------------------------------------------------------------
assistant = client.beta.assistants.create(
    name         = "LawBot‑CrimImm",
    model        = "gpt-4.1",
    instructions = """
You are an expert paralegal specialising in U.S. criminal and immigration law.
• Cite statutes or the provided PDFs.
• If the user asks for personalised legal advice, politely refuse and suggest consulting a licensed attorney.
""",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    },
)

print("Assistant ID:", assistant.id)
open("assistant_id.txt", "w").write(assistant.id)