import streamlit as st
import login
import inventory_aset_microskill
from firestore_utils import init_firestore, test_firestore_connection


# =====================
# Konfigurasi Halaman
# =====================
st.set_page_config(
    page_title="Inventory Aset Micro Skill",
    page_icon="📂",
    layout="wide"
)

# =====================
# Debug: Cek Secrets
# =====================
st.title("🔥 Firestore Secrets & Connection Test")

st.subheader("🔑 Secrets Check")
if "type" in st.secrets:
    st.info("📌 Mode: Root-level secrets")
    st.json({k: v for k, v in st.secrets.items() if k != "private_key"})
elif "firebase" in st.secrets:
    st.info("📌 Mode: Section [firebase]")
    st.json({k: v for k, v in st.secrets["firebase"].items() if k != "private_key"})
else:
    st.error("❌ Tidak menemukan secrets Firebase")

# Tes koneksi Firestore
st.subheader("🗄️ Firestore Connection Test")
try:
    db = init_firestore()
    result = test_firestore_connection(db)
    st.success(result)
except Exception as e:
    st.error(f"❌ Gagal koneksi Firestore: {e}")


# =====================
# Main Aplikasi
# =====================
st.sidebar.title("📂 Digitalisasi Aset Micro Skill")

# Session state login
if "user" not in st.session_state:
    st.session_state["user"] = None

# Login atau Inventory
if st.session_state["user"] is None:
    login.show_login_ui()   # modul login.py
else:
    inventory_aset_microskill.show_inventory_ui()  # modul inventory_aset_microskill.py

import streamlit as st

st.title("🔐 Cek Secrets Firebase")

if "project_id" in st.secrets:
    st.success(f"Project ID: {st.secrets['project_id']}")
    st.write(f"Client Email: {st.secrets['client_email']}")
else:
    st.error("Firebase secrets tidak ditemukan!")
