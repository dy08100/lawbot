import os, time, openai, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 1. Load env & initialize
load_dotenv()
client = openai.Client()
with open("assistant_id.txt") as f:
    ASSISTANT_ID = f.read().strip()

# 2. Create the Flask app
app = Flask(__name__)

# 3. Enable CORS for your Netlify domain (or use "*" during testing)
CORS(
    app,
    resources={
        r"/chat": {
            "origins": "https://bucolic-starship-2589fd.netlify.app"
        }
    },
    supports_credentials=True
)

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    # Handle preflight
    if request.method == "OPTIONS":
        return jsonify({}), 200

    payload   = request.get_json(force=True)
    user_msg  = payload.get("message", "")
    thread_id = payload.get("thread_id")

    # --- 1. Prepare thread
    if not thread_id:
        thread_id = client.beta.threads.create().id

    # --- 2. Add user message
    client.beta.threads.messages.create(
        thread_id = thread_id,
        role      = "user",
        content   = user_msg,
    )

    # --- 3. Run assistant
    run = client.beta.threads.runs.create(
        thread_id    = thread_id,
        assistant_id = ASSISTANT_ID,
    )

    # --- 4. Poll
    while run.status not in ("completed", "failed", "cancelled"):
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(run.id)

    # --- 5. Fetch assistant answer
    messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    answer   = messages.data[0].content[0].text.value

    return jsonify({"answer": answer, "thread_id": thread_id})

if __name__ == "__main__":
    # Bind to $PORT for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)