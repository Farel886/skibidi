from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import re
from google import genai

app = Flask(__name__)

# === Gemini API Key ===
API_KEY = "AIzaSyCjPL-cslkpqlR_jfJOFA4n5Jm2kliUyIA"

def bersihkan_teks(teks):
    return teks.replace("***", "").strip()

def bersihkan_markdown(teks):
    # Hapus bold dan italic Markdown: **teks** dan *teks*
    teks = re.sub(r"\*\*(.*?)\*\*", r"\1", teks)
    teks = re.sub(r"\*(.*?)\*", r"\1", teks)
    return teks

# === Fungsi Generator Username dan Password ===
def generate_username():
    names = ["alpha", "neo", "cyber", "matrix", "code", "byte", "quantum", "dark", "zero", "ghost"]
    return random.choice(names) + str(random.randint(100, 999))

def generate_password():
    use_symbols =  True
    use_uppercase = True 
    use_numbers = True
    length = 12
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if use_uppercase else ""
    numbers_set = "0123456789" if use_numbers else ""
    symbols = "[]{}()*;/,._-#@!$%^&+=" if use_symbols else ""
    all_chars = lower + upper + numbers_set + symbols

    if not all_chars:
        return "", "very weak"

    password = ''.join(random.sample(all_chars, min(length, len(all_chars))))
    score = sum([use_symbols, use_uppercase, use_numbers]) + (length >= 12)
    strength = ["very weak", "weak", "moderate", "strong", "very strong"][min(score, 4)]
    return password, strength

# === ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate():
    password, strength = generate_password()
    username = generate_username()
    return jsonify({
        'password': password,
        'strength': strength,
        'username': username,
        'message': bersihkan_teks("Here is your generated credentials")
    })

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        return render_template("chat.html",
                               user=username,
                               welcome_message=bersihkan_teks("Welcome to the chat interface"))
    else:
        return redirect(url_for('index'))

@app.route('/api/chat', methods=['POST'])
def chat():
    prompt = request.json.get("message")
    if not prompt:
        return jsonify({
            "response": bersihkan_teks("No message received. Please try again.")
        })

    client = genai.Client(api_key=API_KEY)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        clean_text = bersihkan_markdown(bersihkan_teks(response.text))
        return jsonify({
            "response": clean_text,
            "status": bersihkan_teks("Successfully processed your request")
        })
    except Exception as e:
        return jsonify({
            "response": bersihkan_teks(f"An error occurred while processing your request: {e}"),
            "status": "error"
        })

if __name__ == '__main__':
    app.run(debug=True)
