import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import traceback

# ======================
# Helper logging ke sidebar
# ======================
def log_to_sidebar(msg, level="info"):
    if "logs" not in st.session_state:
        st.session_state["logs"] = []
    st.session_state["logs"].append((level, msg))

def show_logs():
    st.sidebar.markdown("### 🪵 Debug Logs")
    if "logs" in st.session_state:
        for level, msg in st.session_state["logs"]:
            if level == "error":
                st.sidebar.error(msg)
            elif level == "warning":
                st.sidebar.warning(msg)
            else:
                st.sidebar.info(msg)

# ======================
# Inisialisasi Firestore
# ======================
def init_firestore():
    try:
        # Cek apakah pakai root-level atau [firebase]
        if "project_id" in st.secrets:
            log_to_sidebar("🔑 Secrets menggunakan root-level", "info")
            cred_dict = dict(st.secrets)
        elif "firebase" in st.secrets:
            log_to_sidebar("🔑 Secrets menggunakan section [firebase]", "info")
            cred_dict = dict(st.secrets["firebase"])
        else:
            raise ValueError("Secrets Firebase tidak ditemukan")

        # Convert jadi Credentials
        cred = credentials.Certificate(cred_dict)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            log_to_sidebar("✅ Firebase Admin initialized", "info")

        return firestore.client()

    except Exception as e:
        log_to_sidebar(f"❌ Error init Firestore: {e}", "error")
        log_to_sidebar(traceback.format_exc(), "error")
        st.error("Gagal inisialisasi Firestore. Cek log di sidebar.")
        return None

# ======================
# UI Utama
# ======================
st.title("🔥 Debug Firestore + Secrets")

db = init_firestore()

if db:
    try:
        # Tes write
        doc_ref = db.collection("debug_test").document("hello")
        doc_ref.set({"msg": "Hello from Streamlit!"})
        log_to_sidebar("✅ Berhasil menulis dokumen ke Firestore", "info")

        # Tes read
        doc = doc_ref.get()
        if doc.exists:
            st.success(f"Firestore OK. Data: {doc.to_dict()}")
            log_to_sidebar(f"📄 Baca dokumen: {doc.to_dict()}", "info")
        else:
            st.warning("Dokumen tidak ditemukan di Firestore.")
            log_to_sidebar("⚠️ Dokumen tidak ditemukan", "warning")

    except Exception as e:
        log_to_sidebar(f"❌ Error Firestore CRUD: {e}", "error")
        log_to_sidebar(traceback.format_exc(), "error")
        st.error("Gagal melakukan operasi Firestore.")

# ======================
# Sidebar Logs
# ======================
show_logs()
