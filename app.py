import os
import json
import random
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

lemmatizer = WordNetLemmatizer()

model = load_model(os.path.join(BASE_DIR, "model.h5"))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    intents = json.load(f)

with open(os.path.join(BASE_DIR, "texts.pkl"), "rb") as f:
    words = pickle.load(f)

with open(os.path.join(BASE_DIR, "labels.pkl"), "rb") as f:
    classes = pickle.load(f)

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": float(r[1])} for r in results]

def get_response(ints, intents_json):
    if not ints:
        # fallback ke noanswer
        for it in intents_json["intents"]:
            if it["tag"] == "noanswer":
                return random.choice(it["responses"]), "confused"
        return "Maaf, saya tidak mengerti.", "confused"

    tag = ints[0]["intent"]
    for it in intents_json["intents"]:
        if it["tag"] == tag:
            text = random.choice(it["responses"])
            mood = mood_from_tag(tag)
            return text, mood

    return "Maaf, saya tidak mengerti.", "confused"

def mood_from_tag(tag: str) -> str:
    # mapping intent -> ekspresi
    if tag in ("confused", "noanswer"):
        return "confused"
    if tag in ("angry",):
        return "angry"
    if tag in ("thanks",):
        return "happy"
    if tag in ("superposition", "wavefunction", "measurement", "double_slit", "uncertainty", "entanglement", "decoherence", "quantum_computing"):
        return "thinking"
    return "normal"

def chatbot_response(msg):
    ints = predict_class(msg, model)
    return get_response(ints, intents)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

# API untuk frontend (POST JSON -> balikin JSON)
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()

    if not msg:
        return jsonify({"reply": "Tulis pertanyaan dulu ya.", "mood": "confused"})

    reply, mood = chatbot_response(msg)
    return jsonify({"reply": reply, "mood": mood})

if __name__ == "__main__":
    app.run(debug=True)
