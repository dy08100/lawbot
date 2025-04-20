import time, openai, os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

client = openai.Client()
with open("assistant_id.txt") as f:
    ASSISTANT_ID = f.read().strip()

app = Flask(__name__)
CORS(app)                      # *Everything* can call it – lock down later

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True)
    user_msg  = payload.get("message", "")
    thread_id = payload.get("thread_id")

    ############################################
    # 1.  Prepare a thread (== conversation)   #
    ############################################
    if not thread_id:
        thread_id = client.beta.threads.create().id

    ############################################
    # 2.  Add the user’s message               #
    ############################################
    client.beta.threads.messages.create(
        thread_id = thread_id,
        role      = "user",
        content   = user_msg,
    )

    ############################################
    # 3.  Run the assistant on that thread     #
    ############################################
    run = client.beta.threads.runs.create(
        thread_id    = thread_id,
        assistant_id = ASSISTANT_ID,
    )

    ############################################
    # 4.  Poll until it finishes (simple)      #
    ############################################
    while run.status not in ("completed", "failed", "cancelled"):
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(run.id)

    ############################################
    # 5.  Grab the latest assistant message    #
    ############################################
    messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    answer   = messages.data[0].content[0].text.value

    return jsonify({"answer": answer, "thread_id": thread_id})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    # Listen on all interfaces so Render can route traffic in
    app.run(host="0.0.0.0", port=port, debug=True)
