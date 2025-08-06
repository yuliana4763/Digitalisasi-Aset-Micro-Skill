import streamlit as st
import pandas as pd
from login import firebase_login
from firestore_utils import (
    add_asset, get_assets, delete_asset,
    add_category, delete_category, get_categories, rename_category,
    add_subcategory, delete_subcategory, get_subcategories, rename_subcategory,
    add_simple_asset, delete_simple_asset, get_simple_assets
)

# =========================
# Konfigurasi halaman & UI Helper
# =========================
st.set_page_config(
    page_title="Inventory Aset Micro Skill",
    page_icon="📂",
    layout="wide"
)

def make_clickable(val: str) -> str:
    """Mengubah string link menjadi clickable HTML."""
    if val and isinstance(val, str):
        return f'<a href="{val}" target="_blank">🔗 Link</a>'
    return ""

# =========================
# Login & State Management
# =========================
def app_login_and_state_setup():
    """Handles the login/logout process and sets up user session state."""
    st.sidebar.image("assets/Logo Microskill Tulisan Putih.png", use_container_width=True)
    st.sidebar.title("Login")
    
    # Check if user is logged in
    if "user" not in st.session_state or st.session_state["user"] is None:
        firebase_login()
    else:
        st.sidebar.success(f"Masuk sebagai: **{st.session_state['user']['email']}**")
        if st.sidebar.button("Logout"):
            st.session_state["user"] = None
            st.rerun()

    # If not logged in, stop the app here
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.info("⚠️ Silakan login untuk mengakses aplikasi.")
        st.stop()

# =========================
# Halaman Utama
# =========================
def show_main_app():
    """Main UI for the application after successful login."""
    is_admin = st.session_state["user"]["email"] == st.secrets.get("admin_email", "")

    # Sidebar
    st.sidebar.title("📂 Inventory Aset")
    menu = st.sidebar.radio(
        "Navigasi",
        options=[
            "📑 Profil Micro Skill",
            "🏢 Aset Organisasi",
            "🗂️ Aset Micro Skill",
            "☁️ Bahan Upload",
            "📑 Formulir & Template",
            "📘 Tema Micro Skill",
            "📝 Pengajuan Tema",
            "📅 Kegiatan",
            "📊 Dashboard"
        ],
        index=0
    )

    if is_admin:
        st.sidebar.success("🔑 Anda login sebagai Admin.")
    else:
        st.sidebar.info("👤 Anda login sebagai User biasa.")

    # Render page based on menu selection
    if menu == "📑 Profil Micro Skill":
        show_profil_micro_skill()
    elif menu == "🏢 Aset Organisasi":
        show_aset_organisasi(is_admin)
    elif menu == "🗂️ Aset Micro Skill":
        show_aset_micro_skill(is_admin)
    elif menu == "☁️ Bahan Upload":
        show_bahan_upload(is_admin)
    elif menu == "📑 Formulir & Template":
        show_formulir_template(is_admin)
    elif menu == "📘 Tema Micro Skill":
        show_tema_micro_skill(is_admin)
    elif menu == "📝 Pengajuan Tema":
        show_pengajuan_tema(is_admin)
    elif menu == "📅 Kegiatan":
        show_kegiatan(is_admin)
    elif menu == "📊 Dashboard":
        show_dashboard()

# =========================
# Page Functions
# =========================

def show_profil_micro_skill():
    """UI untuk halaman Profil Micro Skill"""
    try:
        st.image("assets/Banner.png", use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Banner tidak ditemukan (cek folder assets/)")

    st.markdown("## 📑 Profil Micro Skill")
    st.write(
        """
        **Micro Skill** merupakan platform pembelajaran digital dengan sistem
        **Self Paced Learning**, yaitu sistem pembelajaran yang memungkinkan peserta
        mengerjakan pelatihan secara mandiri.

        Self Paced Learning di Micro Skill bertujuan **mempermudah peserta pelatihan
        dalam mengakses materi** pelatihan sehingga mereka dapat belajar sesuai dengan kecepatan
        dan gaya belajar masing-masing secara **fleksibel**.
        """
    )

def show_aset_organisasi(is_admin):
    """UI untuk halaman Aset Organisasi (hierarchical assets)."""
    st.markdown("## 🏢 Aset Organisasi")

    if is_admin:
        manage_categories_ui()

    categories = get_categories()
    if categories:
        tabs = st.tabs(categories)
        for idx, cat in enumerate(categories):
            with tabs[idx]:
                if is_admin:
                    manage_subcategories_ui(cat)
                
                subcategories = get_subcategories(cat)
                for sub in subcategories:
                    manage_assets_ui(cat, sub, is_admin)

def manage_categories_ui():
    """UI untuk menambah/menghapus/mengubah kategori."""
    st.subheader("📂 Kelola Kategori")
    categories = get_categories()
    col1, col2, col3 = st.columns(3)
    with col1:
        new_cat = st.text_input("Tambah Kategori Baru", key="add_cat")
        if st.button("➕ Tambah Kategori"):
            if new_cat.strip():
                add_category(new_cat)
                st.success(f"Kategori '{new_cat}' ditambahkan!")
                st.rerun()
    with col2:
        if categories:
            cat_to_del = st.selectbox("Hapus Kategori", categories, key="del_cat")
            if st.button("🗑️ Hapus Kategori"):
                delete_category(cat_to_del)
                st.warning(f"Kategori '{cat_to_del}' dihapus.")
                st.rerun()
    with col3:
        if categories:
            old_cat = st.selectbox("Kategori Lama", categories, key="old_cat")
            new_cat_name = st.text_input("Nama Baru", key="rename_cat")
            if st.button("✏️ Rename Kategori"):
                if new_cat_name.strip():
                    rename_category(old_cat, new_cat_name)
                    st.info(f"Kategori '{old_cat}' diubah jadi '{new_cat_name}'")
                    st.rerun()

def manage_subcategories_ui(cat):
    """UI untuk menambah/menghapus/mengubah subkategori."""
    st.markdown(f"**📑 Kelola Subkategori di {cat}**")
    subcats = get_subcategories(cat)
    col1, col2, col3 = st.columns(3)
    with col1:
        new_sub = st.text_input(f"Tambah Subkategori", key=f"add_sub_{cat}")
        if st.button(f"➕ Tambah Sub", key=f"btn_add_sub_{cat}"):
            if new_sub.strip():
                add_subcategory(cat, new_sub)
                st.success(f"Subkategori '{new_sub}' ditambahkan!")
                st.rerun()
    with col2:
        if subcats:
            sub_to_del = st.selectbox(f"Hapus Subkategori", subcats, key=f"del_sub_{cat}")
            if st.button(f"🗑️ Hapus Sub", key=f"btn_del_sub_{cat}"):
                delete_subcategory(cat, sub_to_del)
                st.warning(f"Subkategori '{sub_to_del}' dihapus.")
                st.rerun()
    with col3:
        if subcats:
            old_sub = st.selectbox(f"Sub Lama", subcats, key=f"old_sub_{cat}")
            new_sub_name = st.text_input(f"Nama Baru Sub", key=f"rename_sub_{cat}")
            if st.button(f"✏️ Rename Sub", key=f"btn_rename_sub_{cat}"):
                if new_sub_name.strip():
                    rename_subcategory(cat, old_sub, new_sub_name)
                    st.info(f"Subkategori '{old_sub}' diubah jadi '{new_sub_name}'")
                    st.rerun()

def manage_assets_ui(cat, sub, is_admin):
    """UI untuk menambah/menghapus aset dalam subkategori."""
    st.markdown(f"### 📦 Aset di {sub}")
    assets = get_assets(cat, sub)
    if assets:
        df = pd.DataFrame(assets)
        df["link"] = df["link"].apply(make_clickable)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(f"Belum ada aset di {sub}")
    
    if is_admin:
        with st.form(f"form_manage_{cat}_{sub}", clear_on_submit=True):
            st.markdown("#### Tambah / Hapus Aset")
            col_add, col_del = st.columns([2, 1])
            with col_add:
                nama = st.text_input("📌 Nama Aset", key=f"nama_{cat}_{sub}")
                link = st.text_input("🔗 Link Aset", key=f"link_{cat}_{sub}")
                submitted = st.form_submit_button("✅ Tambah Aset")
                if submitted and nama.strip() and link.strip():
                    add_asset(cat, sub, nama, link)
                    st.success(f"Aset '{nama}' ditambahkan!")
                    st.rerun()
            with col_del:
                if assets:
                    del_id = st.selectbox("Pilih aset untuk dihapus", [a["id"] for a in assets], key=f"del_asset_{cat}_{sub}")
                    if st.form_submit_button("❌ Hapus Aset"):
                        delete_asset(cat, sub, del_id)
                        st.warning("Aset dihapus.")
                        st.rerun()

def show_simple_asset_manager(collection_name: str, title: str, is_admin: bool):
    """Reusable UI for managing simple asset collections."""
    assets = get_simple_assets(collection_name)
    
    st.markdown(f"### 📑 Daftar {title}")
    if assets:
        df = pd.DataFrame(assets)
        df["Link Aset"] = df["Link Aset"].apply(make_clickable)
        st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(f"Belum ada data {title.lower()}.")

    if is_admin:
        st.markdown("### 📂 Manajemen Aset")
        with st.form(f"form_manage_{collection_name}", clear_on_submit=True):
            col_add, col_del = st.columns([2, 1])
            with col_add:
                nama = st.text_input(f"📌 Nama {title}", key=f"{collection_name}_nama")
                link = st.text_input(f"🔗 Link {title} (Google Drive)", key=f"{collection_name}_link")
                submitted = st.form_submit_button(f"✅ Tambah {title}")
                if submitted and nama and link:
                    add_simple_asset(collection_name, nama, link)
                    st.success(f"{title} **{nama}** berhasil ditambahkan!")
                    st.rerun()
            with col_del:
                if assets:
                    asset_list = [a["Nama Aset"] for a in assets]
                    asset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
                    hapus_nama = st.selectbox(f"Pilih {title.lower()} untuk dihapus", asset_list, key=f"{collection_name}_hapus")
                    if st.form_submit_button(f"❌ Konfirmasi Hapus"):
                        delete_simple_asset(collection_name, asset_id_map[hapus_nama])
                        st.warning(f"{title} **{hapus_nama}** sudah dihapus.")
                        st.rerun()

# =========================
# Page Renderers
# =========================
def show_aset_micro_skill(is_admin):
    st.markdown("## 🗂️ Aset Micro Skill")
    tab_materi, tab_visual = st.tabs(["Materi Micro Skill", "Visual/Infografis"])
    with tab_materi:
        show_simple_asset_manager("materi_aset", "Materi Micro Skill", is_admin)
    with tab_visual:
        show_simple_asset_manager("visual_aset", "Visual/Infografis", is_admin)

def show_bahan_upload(is_admin):
    st.markdown("## ☁️ Bahan Upload")
    tab_dokumen, tab_media = st.tabs(["Dokumen Pendukung", "Media/Gambar"])
    with tab_dokumen:
        show_simple_asset_manager("dokumen_aset", "Dokumen Pendukung", is_admin)
    with tab_media:
        show_simple_asset_manager("media_aset", "Media/Gambar", is_admin)

def show_formulir_template(is_admin):
    st.markdown("## 📑 Formulir & Template")
    tab_ppt, tab_dokumen_tpl = st.tabs(["Template PPT", "Template Dokumen"])
    with tab_ppt:
        show_simple_asset_manager("ppt_aset", "Template PPT", is_admin)
    with tab_dokumen_tpl:
        show_simple_asset_manager("dokumen_tpl_aset", "Template Dokumen", is_admin)

def show_tema_micro_skill(is_admin):
    st.markdown("## 📘 Tema Micro Skill")
    tab_tema, tab_pelatihan = st.tabs(["Daftar Tema", "Tema Pelatihan"])
    with tab_tema:
        show_simple_asset_manager("tema_aset", "Daftar Tema", is_admin)
    with tab_pelatihan:
        show_simple_asset_manager("tema_pelatihan_aset", "Tema Pelatihan", is_admin)

def show_pengajuan_tema(is_admin):
    st.markdown("## 📝 Pengajuan Tema")
    tab_form, tab_status = st.tabs(["Form Pengajuan", "Status Pengajuan"])
    with tab_form:
        show_simple_asset_manager("form_pengajuan_aset", "Form Pengajuan", is_admin)
    with tab_status:
        show_simple_asset_manager("status_pengajuan_aset", "Status Pengajuan", is_admin)

def show_kegiatan(is_admin):
    st.markdown("## 📅 Kegiatan")
    tab_jadwal, tab_dokumentasi = st.tabs(["Jadwal Kegiatan", "Dokumentasi"])
    with tab_jadwal:
        show_simple_asset_manager("jadwal_aset", "Jadwal Kegiatan", is_admin)
    with tab_dokumentasi:
        show_simple_asset_manager("dokumentasi_aset", "Dokumentasi", is_admin)

def show_dashboard():
    st.markdown("## 📊 Dashboard")
    st.write("Konten dashboard akan ditampilkan di sini.")

# =========================
# Run the App
# =========================
if __name__ == "__main__":
    try:
        app_login_and_state_setup()
        show_main_app()
    except FileNotFoundError as e:
        st.error(f"Error: {e}. Pastikan file logo dan banner ada di folder `assets/`.")