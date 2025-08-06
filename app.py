import streamlit as st
from firestore_utils import init_firestore, test_firestore_connection

st.title("🔥 Firestore Secrets & Connection Test")

# Tampilkan secrets yg terbaca (tanpa private_key full)
st.subheader("🔑 Secrets check")
if "type" in st.secrets:
    st.write("📌 Mode: Root-level secrets")
    st.json({k: v for k, v in st.secrets.items() if k != "private_key"})
elif "firebase" in st.secrets:
    st.write("📌 Mode: Section [firebase]")
    st.json({k: v for k, v in st.secrets["firebase"].items() if k != "private_key"})
else:
    st.error("❌ Tidak menemukan secrets Firebase")

# Tes koneksi Firestore
st.subheader("🗄️ Firestore connection")
try:
    db = init_firestore()
    result = test_firestore_connection(db)
    st.success(result)
except Exception as e:
    st.error(f"Gagal koneksi Firestore: {e}")
