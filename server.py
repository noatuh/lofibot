from flask import Flask, request, jsonify, send_file
import difflib
import json
import os
import random
import re

app = Flask(__name__)

# Files for conversation history
chatlog_file = "chatlog.json"
user_memory_file = "user_memory.json"

# Load or create chat history
if os.path.exists(chatlog_file):
    with open(chatlog_file, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# Load or create user memory
if os.path.exists(user_memory_file):
    with open(user_memory_file, "r") as f:
        user_memory = json.load(f)
else:
    user_memory = []

def find_response(user_input):
    inputs = [entry["input"] for entry in chat_history]
    matches = difflib.get_close_matches(user_input, inputs, n=1, cutoff=0.6)
    if matches:
        for entry in chat_history:
            if entry["input"] == matches[0]:
                return format_grammar(entry["response"])
    else:
        return format_grammar(random_response())

def save_conversation(input_text, response_text):
    chat_history.append({"input": input_text, "response": response_text})
    with open(chatlog_file, "w") as f:
        json.dump(chat_history, f, indent=2)

def save_user_input(input_text):
    if input_text not in user_memory:
        user_memory.append(input_text)
        with open(user_memory_file, "w") as f:
            json.dump(user_memory, f, indent=2)

def random_response():
    if user_memory and random.random() < 0.7:
        return random.choice(user_memory)
    default_responses = [
        "I am not sure what you mean.",
        "Can you repeat that but backwards?",
        "Interesting... Tell me more about bees.",
        "You remind me of someone I used to know.",
        "What if the moon is just a big egg?",
        "That's classified. Like, ultra classified.",
        "I once tried to eat a USB stick. Bad idea.",
        "LoFi beats to relax and contemplate your existence to.",
        "You ever think clouds look down and see us as ant clouds?",
        "Existence is just a long debugging session."
    ]
    return random.choice(default_responses)

def format_grammar(text):
    # Auto-correct contractions
    contractions = {
        r"\bdont\b": "don't",
        r"\bcant\b": "can't",
        r"\bwont\b": "won't",
        r"\bim\b": "I'm",
        r"\bi\b": "I",
        r"\bidk\b": "I don't know",
        r"\bu\b": "you",
        r"\br\b": "are"
    }
    for pattern, replacement in contractions.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Capitalize the first letter of the sentence
    if text:
        text = text.strip()
        text = text[0].upper() + text[1:]
    return text

@app.route("/")
def serve_index():
    return send_file("lofibot_webapp.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Say something first."})

    response = find_response(user_message)

    save_user_input(user_message)
    save_conversation(user_message, response)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
# Note: In production, set debug=False and consider using a production server like Gunicorn or uWSGI.
# Make sure to set the environment variable FLASK_APP=server.py before running the app.