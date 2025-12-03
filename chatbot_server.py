# chatbot_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from gemini_chatbot import (
    load_key,
    save_data,
    ask_initial_details,
    generate_response,
    ENCRYPTED_FILE
)

app = Flask(__name__)
CORS(app)

# Load encryption key and memory
fernet = load_key()
try:
    with open(ENCRYPTED_FILE, 'rb') as f:
        decrypted = fernet.decrypt(f.read()).decode('utf-8')
        all_user_data = json.loads(decrypted)
except Exception:
    all_user_data = {}

# Routes
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        if not username:
            return jsonify({"error": "Username is required"}), 400

        if username not in all_user_data:
            all_user_data[username] = {
                "name": data.get("name"),
                "education": data.get("education"),
                "business": data.get("business"),
                "interests": data.get("interests")
            }
            save_data(all_user_data, fernet)

        return jsonify({"status": "registered"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        username = data.get("username")
        user_message = data.get("message")

        if not username or not user_message:
            return jsonify({"error": "Missing username or message"}), 400

        user_data = all_user_data.get(username)
        if not user_data:
            return jsonify({"error": "User not found."}), 404

        # Add context
        intro = f"This user is named {user_data.get('name', 'Anonymous')}"
        if 'education' in user_data:
            intro += f", studying {user_data['education']}"
        if 'business' in user_data:
            intro += f", runs a business called {user_data['business']}"
        if 'interests' in user_data:
            intro += f", and is interested in {user_data['interests']}"

        full_prompt = intro + f"\nUser asked: {user_message}"

        # Generate response
        chat_history = []
        response = generate_response(full_prompt, chat_history)

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


