# streamlit_app.py
import os
import json
import streamlit as st
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import google.generativeai as genai

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ API key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

def get_model():
    candidates = ["models/gemini-1.5-flash", "gemini-1.5-flash"]
    last_exc = None
    for name in candidates:
        try:
            return genai.GenerativeModel(name)
        except Exception as e:
            last_exc = e
            continue
    st.error(f"Model init failed. Tried {candidates}. Last error: {last_exc}")
    st.stop()

# Initialize model
model = get_model()

# File paths
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)
ENCRYPTED_FILE = os.path.join(DATA_DIR, "chat_data.enc")
KEY_FILE = os.path.join(DATA_DIR, "secret.key")

# Load or generate Fernet key
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

# Load encrypted user data
def load_data():
    if not os.path.exists(ENCRYPTED_FILE):
        return {}
    try:
        with open(ENCRYPTED_FILE, "rb") as f:
            return json.loads(fernet.decrypt(f.read()).decode("utf-8"))
    except Exception:
        return {}

# Save encrypted user data
def save_data(data):
    with open(ENCRYPTED_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(data).encode("utf-8")))

# Prompt user for initial details
def ask_user_details():
    details = {}
    details["name"] = st.text_input("👤 What's your full name?")
    education = st.text_input("🎓 Are you a student? Mention course/year or say 'No'")
    if "no" not in education.lower():
        details["education"] = education
    business = st.text_input("💼 Do you have a business? Mention name or say 'No'")
    if "no" not in business.lower():
        details["business"] = business
    details["interests"] = st.text_input("🎯 What are your interests?")
    return details

# Generate AI response
def generate_response(user_input, context, user_data):
    try:
        intro = f"This user is named {user_data.get('name', 'Anonymous')}"
        if "education" in user_data:
            intro += f", studying {user_data['education']}"
        if "business" in user_data:
            intro += f", runs a business called {user_data['business']}"
        if "interests" in user_data:
            intro += f", and is interested in {user_data['interests']}"
        full_prompt = intro + f"\nUser asked: {user_input}"

        convo = ["You are a helpful assistant. Be friendly and avoid repeating user details unless asked."]
        for c in context:
            convo.append(f"User: {c['user']}")
            convo.append(f"Bot: {c['bot']}")
        convo.append(f"User: {full_prompt}")
        response = model.generate_content("\n".join(convo))
        return getattr(response, "text", str(response)).strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

# ---- Streamlit UI ----
st.set_page_config(page_title="ChatBuddy", layout="centered")
st.title("💬 ChatBuddy")
st.markdown("A personalized AI chatbot with memory.")

# Session state setup
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "all_data" not in st.session_state:
    st.session_state.all_data = load_data()

# Username login screen
if not st.session_state.username:
    username_input = st.text_input("🔐 Enter your username to begin:")
    if username_input:
        st.session_state.username = username_input.strip()
        all_data = st.session_state.all_data
        if username_input not in all_data:
            st.session_state.user_data = ask_user_details()
            all_data[username_input] = st.session_state.user_data
            save_data(all_data)
        else:
            st.session_state.user_data = all_data[username_input]
        st.rerun()

# Main chat interface
else:
    st.success(f"👋 Welcome back, {st.session_state.user_data.get('name', st.session_state.username)}!")

    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["user"])
        with st.chat_message("assistant"):
            st.markdown(chat["bot"])

    user_input = st.chat_input("Type your message...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        response = generate_response(user_input, st.session_state.chat_history, st.session_state.user_data)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.chat_history.append({"user": user_input, "bot": response})

# Optional: Clear chat button
if st.button("🔄 Reset Chat"):
    st.session_state.chat_history = []
    st.rerun()
