import os
import json
import streamlit as st
from cryptography.fernet import Fernet
import google.generativeai as genai

# --- Configure Gemini AI ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Paths ---
DATA_DIR = "user_data"
KEY_FILE = os.path.join(DATA_DIR, "secret.key")
ENC_FILE = os.path.join(DATA_DIR, "chat_data.enc")
os.makedirs(DATA_DIR, exist_ok=True)

# --- Encryption Handling ---
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

def save_data(all_data, fernet):
    encrypted = fernet.encrypt(json.dumps(all_data).encode('utf-8'))
    with open(ENC_FILE, 'wb') as f:
        f.write(encrypted)

def load_data(fernet):
    if not os.path.exists(ENC_FILE):
        return {}
    try:
        with open(ENC_FILE, 'rb') as f:
            decrypted = fernet.decrypt(f.read()).decode('utf-8')
            return json.loads(decrypted)
    except:
        return {}

# --- Generate AI Response ---
def generate_response(user_input, context=[]):
    try:
        convo = ["You are a helpful assistant. Be friendly and do not repeat known user info unless asked."]
        for chat in context:
            convo.append(f"User: {chat['user']}")
            convo.append(f"Bot: {chat['bot']}")
        convo.append(f"User: {user_input}")
        response = model.generate_content("\n".join(convo))
        return response.text.strip()
    except Exception as e:
        return f"Sorry, something went wrong: {e}"

# --- Streamlit App Start ---
st.set_page_config(page_title="Gemini AI Chatbot", layout="centered")
st.title("💬 Gemini AI Chatbot")

fernet = load_key()
all_user_data = load_data(fernet)

# --- User Login ---
username = st.text_input("🔑 Enter your username:")
if not username:
    st.stop()

if username not in all_user_data:
    st.subheader("👤 New User Setup")
    name = st.text_input("Your full name:")
    education = st.text_input("Education (e.g., BBA 2nd Year or 'No'):")
    business = st.text_input("Do you run a business? (Name or 'No'):")
    interests = st.text_input("Your interests:")

    if st.button("✅ Register"):
        all_user_data[username] = {
            "name": name,
            "education": education if "no" not in education.lower() else None,
            "business": business if "no" not in business.lower() else None,
            "interests": interests
        }
        save_data(all_user_data, fernet)
        st.success("User registered! You can now chat.")
        st.experimental_rerun()

user_data = all_user_data.get(username)
if not user_data:
    st.warning("❗ Please register first.")
    st.stop()

# --- Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Input Form ---
with st.form("chat_form"):
    user_input = st.text_input("You:", placeholder="Type your message here...")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    intro = f"This user is named {user_data['name']}"
    if user_data.get("education"):
        intro += f", studying {user_data['education']}"
    if user_data.get("business"):
        intro += f", runs a business called {user_data['business']}"
    if user_data.get("interests"):
        intro += f", and is interested in {user_data['interests']}"
    prompt = intro + f"\nUser asked: {user_input}"

    response = generate_response(prompt, st.session_state.chat_history)
    st.session_state.chat_history.append({"user": user_input, "bot": response})

# --- Chat Display ---
st.subheader("📜 Chat History")
for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")

# --- Reset Option ---
if st.button("🔁 Reset Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()

