import os
import json
import streamlit as st
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ API key not found. Set GOOGLE_API_KEY in secrets or .env.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# File paths
DATA_DIR = "user_data"
KEY_FILE = os.path.join(DATA_DIR, "secret.key")
ENCRYPTED_FILE = os.path.join(DATA_DIR, "chat_data.enc")
os.makedirs(DATA_DIR, exist_ok=True)

# Functions for encryption
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

def load_all_data():
    if not os.path.exists(ENCRYPTED_FILE):
        return {}
    try:
        with open(ENCRYPTED_FILE, 'rb') as f:
            data = f.read()
            return json.loads(fernet.decrypt(data).decode('utf-8'))
    except:
        return {}

def save_all_data(all_data):
    encrypted = fernet.encrypt(json.dumps(all_data).encode('utf-8'))
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted)

# UI setup
st.set_page_config(page_title="ChatBuddy", page_icon="💬", layout="centered")
st.title("💬 ChatBuddy")
st.markdown("Your smart assistant with memory and personality.")

# User login
if "username" not in st.session_state:
    username = st.text_input("Enter your username to begin:", key="login")
    if username:
        st.session_state.username = username
        st.rerun()

# Load or create user data
all_data = load_all_data()
username = st.session_state.username
user_data = all_data.get(username, {})

if not user_data:
    st.subheader("👋 Welcome! Let's get to know you.")
    name = st.text_input("What's your full name?")
    edu = st.text_input("Are you a student? If yes, mention your course and year. Else type 'No'")
    biz = st.text_input("Do you have a business? If yes, mention the name. Else type 'No'")
    interests = st.text_input("What are your interests?")
    
    if st.button("Save & Start Chat"):
        user_data['name'] = name
        if "no" not in edu.lower(): user_data['education'] = edu
        if "no" not in biz.lower(): user_data['business'] = biz
        user_data['interests'] = interests
        all_data[username] = user_data
        save_all_data(all_data)
        st.success("✅ Details saved!")
        st.rerun()

elif "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat interface
if user_data and "chat_history" in st.session_state:
    st.markdown("---")
    st.subheader(f"Hi {user_data.get('name', username)} 👋")

    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(entry["user"])
        with st.chat_message("assistant"):
            st.markdown(entry["bot"])

    user_input = st.chat_input("Type your message")
    if user_input:
        intro = f"This user is named {user_data.get('name', 'Anonymous')}"
        if 'education' in user_data:
            intro += f", studying {user_data['education']}"
        if 'business' in user_data:
            intro += f", runs a business called {user_data['business']}"
        if 'interests' in user_data:
            intro += f", and is interested in {user_data['interests']}"
        full_prompt = intro + f"\nUser asked: {user_input}"

        try:
            response = model.generate_content(full_prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = "❌ Something went wrong. Please try again later."

        st.session_state.chat_history.append({"user": user_input, "bot": reply})
        st.rerun()




