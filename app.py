import os, time, openai, json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv

# ── Load env & init client ────────────────────────────────────────────────
load_dotenv()
client = openai.Client()
ASSISTANT_ID = open("assistant_id.txt").read().strip()

# ── Create app and enable CORS for all origins ─────────────────────────────
app = Flask(__name__)
# This will add Access-Control-Allow-Origin: * to every response
CORS(app, supports_credentials=True)

# ── Global after_request to ensure headers on errors too ───────────────────
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# ── The /chat endpoint ─────────────────────────────────────────────────────
@app.route("/chat", methods=["POST","OPTIONS"])
def chat():
    # handle preflight
    if request.method == "OPTIONS":
        return make_response(jsonify({}),200)

    data     = request.get_json(force=True)
    user_msg = data.get("message","")
    thread_id= data.get("thread_id")

    if not thread_id:
        thread_id = client.beta.threads.create().id

    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_msg
    )

    # --- 3. Run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=ASSISTANT_ID
    )

    # --- 4. Poll until complete (pass both IDs!)
    while run.status not in ("completed", "failed", "cancelled"):
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )


    msg = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    answer = msg.data[0].content[0].text.value
    return jsonify({"answer":answer, "thread_id":thread_id})

# ── Run on $PORT for Render ────────────────────────────────────────────────
if __name__=="__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)