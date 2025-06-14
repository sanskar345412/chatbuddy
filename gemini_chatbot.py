import os
import json
import time
import speech_recognition as sr
import pyttsx3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("\u274C API key not found. Set GOOGLE_API_KEY in .env or system environment.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# File paths
DATA_DIR = "user_data"
ENCRYPTED_FILE = os.path.join(DATA_DIR, "chat_data.enc")
KEY_FILE = os.path.join(DATA_DIR, "secret.key")
os.makedirs(DATA_DIR, exist_ok=True)

# Voice setup
recognizer = sr.Recognizer()
speaker = pyttsx3.init()
speaker.setProperty('rate', 160)

def speak(text):
    print(f"\U0001F916 Bot: {text}")
    speaker.say(text)
    speaker.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("\n\U0001F3A4 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""

def generate_response(user_input, context=[]):
    try:
        convo = ["You are a friendly and intelligent assistant. Keep your answers relevant and avoid repeating details unless asked."]
        for c in context:
            convo.append(f"User: {c['user']}")
            convo.append(f"Bot: {c['bot']}")
        convo.append(f"User: {user_input}")

        response = model.generate_content("\n".join(convo))
        return response.text.strip()
    except Exception as e:
        return "Sorry, something went wrong."

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

def load_data(username, fernet):
    if not os.path.exists(ENCRYPTED_FILE):
        return {}
    try:
        with open(ENCRYPTED_FILE, 'rb') as f:
            decrypted_data = fernet.decrypt(f.read()).decode('utf-8')
            return json.loads(decrypted_data).get(username, {})
    except Exception:
        return {}

def save_data(all_data, fernet):
    encrypted = fernet.encrypt(json.dumps(all_data).encode('utf-8'))
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted)

def ask_initial_details():
    details = {}
    speak("What's your full name?")
    details['name'] = input("Name: ")
    speak("Are you a student? If yes, mention your course and year. Otherwise say 'No'.")
    edu = input("Education: ")
    if 'no' not in edu.lower():
        details['education'] = edu
    speak("Do you have a business? If yes, mention the name. Otherwise say 'No'.")
    biz = input("Business: ")
    if 'no' not in biz.lower():
        details['business'] = biz
    speak("What are your interests?")
    details['interests'] = input("Interests: ")
    return details

# Start
fernet = load_key()
speak("Welcome! Please enter your username to continue.")
username = input("Username: ")

# Load all encrypted data
try:
    with open(ENCRYPTED_FILE, 'rb') as f:
        decrypted = fernet.decrypt(f.read()).decode('utf-8')
        all_user_data = json.loads(decrypted)
except Exception:
    all_user_data = {}

user_data = all_user_data.get(username, {})
if not user_data:
    user_data = ask_initial_details()
    all_user_data[username] = user_data
    save_data(all_user_data, fernet)

chat_history = []
speak("\U0001F916 I'm ready to chat. Type 'exit' to quit, '/reset' to clear, or '/update' to change your info.")

while True:
    try:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            save_data(all_user_data, fernet)
            speak("Goodbye!")
            break

        elif user_input.lower() == "/reset":
            user_data = ask_initial_details()
            all_user_data[username] = user_data
            save_data(all_user_data, fernet)
            chat_history = []
            speak("Your information has been reset.")
            continue

        elif user_input.lower() == "/update":
            speak("What would you like to update? name, education, business, or interests?")
            field = input("Field: ").strip().lower()
            if field in user_data:
                user_data[field] = input(f"New value for {field}: ")
                all_user_data[username] = user_data
                save_data(all_user_data, fernet)
                speak(f"Updated {field}.")
            else:
                speak("Invalid field.")
            continue

        # Inject user context into prompt
        intro = f"This user is named {user_data.get('name', 'Anonymous')}"
        if 'education' in user_data:
            intro += f", studying {user_data['education']}"
        if 'business' in user_data:
            intro += f", runs a business called {user_data['business']}"
        if 'interests' in user_data:
            intro += f", and is interested in {user_data['interests']}"

        full_prompt = intro + f"\nUser asked: {user_input}"

        response = generate_response(full_prompt, chat_history)
        chat_history.append({"user": user_input, "bot": response})
        speak(response)

    except Exception as e:
        speak(f"Error: {e}")


