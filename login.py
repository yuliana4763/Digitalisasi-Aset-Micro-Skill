import streamlit as st
import requests

# ==============================
# Firebase Web API Key (dari secrets)
# ==============================
API_KEY = st.secrets["firebase_web"]["apiKey"]

# ==============================
# Fungsi login ke Firebase
# ==============================
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    return response.json()

# ==============================
# UI Login
# ==============================
def show_login_ui():
    st.title("🔑 Login - Inventory Aset Micro Skill")

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"]:
        st.success(f"✅ Logged in as {st.session_state['user']['email']}")
        if st.button("Logout"):
            st.session_state["user"] = None
            st.rerun()
    else:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                result = firebase_login(email, password)
                if "idToken" in result:
                    st.session_state["user"] = {
                        "email": result["email"],
                        "idToken": result["idToken"]
                    }
                    st.success("Login berhasil! 🚀")
                    st.rerun()
                else:
                    st.error(f"Login gagal: {result.get('error', {}).get('message', 'Unknown error')}")
