# firestore_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ==============================
# 1. Init Firebase (pakai st.secrets)
# ==============================
@st.cache_resource
def init_firestore():
    if not firebase_admin._apps:
        cred_dict = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        }

        # Tambahkan universe_domain kalau ada di secrets
        if "universe_domain" in st.secrets["firebase"]:
            cred_dict["universe_domain"] = st.secrets["firebase"]["universe_domain"]

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firestore()

# ==============================
# 2. CRUD Functions
# ==============================

def add_category(category_name: str):
    """Tambah kategori baru"""
    try:
        db.collection("categories").document(category_name).set({"name": category_name})
        return True
    except Exception as e:
        st.error(f"Gagal menambah kategori: {e}")
        return False

def delete_category(category_name: str):
    """Hapus kategori (beserta subcollectionnya)"""
    try:
        db.collection("categories").document(category_name).delete()
        return True
    except Exception as e:
        st.error(f"Gagal menghapus kategori: {e}")
        return False

def add_subcategory(category: str, subcategory: str):
    """Tambah subkategori"""
    try:
        db.collection("categories").document(category).collection("subcategories").document(subcategory).set(
            {"name": subcategory}
        )
        return True
    except Exception as e:
        st.error(f"Gagal menambah subkategori: {e}")
        return False

def delete_subcategory(category: str, subcategory: str):
    """Hapus subkategori"""
    try:
        db.collection("categories").document(category).collection("subcategories").document(subcategory).delete()
        return True
    except Exception as e:
        st.error(f"Gagal menghapus subkategori: {e}")
        return False

def add_asset(category: str, subcategory: str, nama: str, link: str):
    """Tambah aset ke dalam subkategori"""
    try:
        db.collection("categories").document(category).collection("subcategories").document(subcategory).collection("assets").add(
            {"nama": nama, "link": link}
        )
        return True
    except Exception as e:
        st.error(f"Gagal menambah aset: {e}")
        return False

def get_assets(category: str, subcategory: str):
    """Ambil semua aset dari subkategori"""
    try:
        docs = db.collection("categories").document(category).collection("subcategories").document(subcategory).collection("assets").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        st.error(f"Gagal mengambil aset: {e}")
        return []

def delete_asset(category: str, subcategory: str, asset_id: str):
    """Hapus aset berdasarkan id"""
    try:
        db.collection("categories").document(category).collection("subcategories").document(subcategory).collection("assets").document(asset_id).delete()
        return True
    except Exception as e:
        st.error(f"Gagal menghapus aset: {e}")
        return False
