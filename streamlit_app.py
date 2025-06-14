import os
import json
import streamlit as st
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API key not found. Please set it in .env or secrets.toml.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# File paths
DATA_DIR = "user_data"
ENCRYPTED_FILE = os.path.join(DATA_DIR, "chat_data.enc")
KEY_FILE = os.path.join(DATA_DIR, "secret.key")
os.makedirs(DATA_DIR, exist_ok=True)

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

# Load all user data from encrypted file
def load_all_data():
    if not os.path.exists(ENCRYPTED_FILE):
        return {}
    try:
        with open(ENCRYPTED_FILE, "rb") as f:
            return json.loads(fernet.decrypt(f.read()).decode("utf-8"))
    except Exception:
        return {}

# Save all user data
def save_all_data(data):
    with open(ENCRYPTED_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(data).encode("utf-8")))

# Ask user details
def ask_initial_details():
    st.markdown("### Let's get to know you better.")
    name = st.text_input("👤 What's your full name?")
    education = st.text_input("🎓 Are you a student? Mention your course & year, or type 'No'.")
    business = st.text_input("💼 Do you have a business? If yes, mention the name, else type 'No'.")
    interests = st.text_input("🎯 What are your interests?")
    
    details = {
        "name": name,
        "interests": interests
    }
    if education.lower() != "no":
        details["education"] = education
    if business.lower() != "no":
        details["business"] = business
    return details

# Generate response with user context
def generate_response(user_input, user_data, chat_history):
    try:
        prompt = f"This user is named {user_data.get('name', 'Anonymous')}"
        if "education" in user_data:
            prompt += f", studying {user_data['education']}"
        if "business" in user_data:
            prompt += f", runs a business called {user_data['business']}"
        if "interests" in user_data:
            prompt += f", and is interested in {user_data['interests']}"

        prompt += f"\nUser asked: {user_input}"

        convo = [
            "You are a helpful assistant. Answer clearly and concisely. Avoid repeating known facts unless asked."
        ]
        for c in chat_history:
            convo.append(f"User: {c['user']}")
            convo.append(f"Bot: {c['bot']}")
        convo.append(f"User: {user_input}")

        response = model.generate_content("\n".join(convo))
        return response.text.strip()
    except Exception as e:
        return "⚠️ Sorry, something went wrong."

# Title
st.set_page_config(page_title="ChatBuddy 🤖", page_icon="🤖")
st.title("ChatBuddy 🤖")

# Session state setup
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.session_state.username = st.text_input("Enter your username to begin:")
    st.stop()

# Load or create user data
all_user_data = load_all_data()
user_data = all_user_data.get(st.session_state.username)

if not user_data:
    user_data = ask_initial_details()
    all_user_data[st.session_state.username] = user_data
    save_all_data(all_user_data)
    st.success("✅ Profile saved! Let's chat.")

# Load or initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat interface
st.markdown("---")
user_input = st.text_input("💬 Type your message here:", key="chat_input")
if st.button("Send", use_container_width=True) and user_input:
    reply = generate_response(user_input, user_data, st.session_state.chat_history)
    st.session_state.chat_history.append({"user": user_input, "bot": reply})

# Display chat
for chat in st.session_state.chat_history:
    st.markdown(f"👤 **You:** {chat['user']}")
    st.markdown(f"🤖 **ChatBuddy:** {chat['bot']}")

# Option to reset or update
st.markdown("---")
col1, col2 = st.columns(2)
if col1.button("🔁 Reset Info"):
    del all_user_data[st.session_state.username]
    save_all_data(all_user_data)
    st.session_state.chat_history = []
    st.session_state.username = None
    st.experimental_rerun()

if col2.button("✏️ Update Info"):
    with st.form("update_form"):
        field = st.selectbox("Which field do you want to update?", ["name", "education", "business", "interests"])
        new_value = st.text_input(f"New value for {field}:")
        submitted = st.form_submit_button("Update")
        if submitted and new_value:
            user_data[field] = new_value
            all_user_data[st.session_state.username] = user_data
            save_all_data(all_user_data)
            st.success(f"✅ Updated {field}")





