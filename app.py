"""
app.py

Flask backend for the chatbot. Receives chat messages from the front end,
forwards them to the Gemini API along with the system prompt from
chatbot_config.py, and returns the model's reply as JSON.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Add it to your .env file before running the app."
    )

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)

# Simple in-memory chat sessions, keyed by a session id sent from the browser.
chat_sessions = {}


def get_chat_session(session_id: str):
    """Return an existing Gemini chat session or start a new one."""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
    return chat_sessions[session_id]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id") or "default"

    if not user_message:
        return jsonify({"reply": "Please type a message before sending."}), 400

    try:
        chat_session = get_chat_session(session_id)
        response = chat_session.send_message(user_message)
        reply_text = response.text
    except Exception as exc:  # noqa: BLE001
        reply_text = f"Sorry, something went wrong talking to the AI: {exc}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
