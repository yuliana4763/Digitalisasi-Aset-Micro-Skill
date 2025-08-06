import streamlit as st
import pandas as pd
from firestore_utils import (
    add_asset, get_assets, delete_asset,
    add_category, delete_category, get_categories, rename_category,
    add_subcategory, delete_subcategory, get_subcategories, rename_subcategory,
    get_simple_assets,  # <-- Added missing import
    add_simple_asset,   # <-- Add this import
    delete_simple_asset # <-- Add this import if used elsewhere
)

# =========================
# Konfigurasi halaman
# =========================
st.set_page_config(
    page_title="Inventory Aset Micro Skill",
    page_icon="📂",
    layout="wide"
)

st.sidebar.image("assets/Logo Microskill Tulisan Putih.png", use_container_width=True)
st.sidebar.title("📂 Inventory Aset")

menu = st.sidebar.radio(
    "Navigasi",
    ["📑 Profil Micro Skill", "🏢 Aset Organisasi", "🗂️ Aset Micro Skill"]
)

# =========================
# Helper: buat link jadi clickable
# =========================
def make_clickable(val):
    return f'<a href="{val}" target="_blank">🔗 Link</a>'

# =========================
# Profil Micro Skill
# =========================
if menu == "📑 Profil Micro Skill":
    st.image("assets/Banner.png", use_container_width=True)
    st.markdown("## 📑 Profil Micro Skill")
    st.write("**Micro Skill** adalah platform pembelajaran digital ...")

# =========================
# Aset Organisasi (Firestore-driven)
# =========================
elif menu == "🏢 Aset Organisasi":
    st.markdown("## 🏢 Aset Organisasi")

    # --- Kelola Kategori ---
    st.subheader("📂 Kelola Kategori")
    col1, col2, col3 = st.columns(3)

    with col1:
        new_cat = st.text_input("Tambah Kategori Baru")
        if st.button("➕ Tambah Kategori"):
            add_category(new_cat)
            st.success(f"Kategori '{new_cat}' ditambahkan!")

    with col2:
        categories = get_categories()
        if categories:
            cat_to_del = st.selectbox("Hapus Kategori", categories)
            if st.button("🗑️ Hapus Kategori"):
                delete_category(cat_to_del)
                st.warning(f"Kategori '{cat_to_del}' dihapus.")

    with col3:
        if categories:
            old_cat = st.selectbox("Kategori Lama", categories)
            new_cat_name = st.text_input("Nama Baru")
            if st.button("✏️ Rename Kategori"):
                rename_category(old_cat, new_cat_name)
                st.info(f"Kategori '{old_cat}' diubah menjadi '{new_cat_name}'")

    # --- Tabs dinamis dari Firestore ---
    categories = get_categories()
    if categories:
        tabs = st.tabs(categories)
        for idx, cat in enumerate(categories):
            with tabs[idx]:
                st.subheader(f"📂 {cat}")

                # Subkategori
                subcats = get_subcategories(cat)
                sub_col1, sub_col2, sub_col3 = st.columns(3)

                with sub_col1:
                    new_sub = st.text_input(f"Tambah Subkategori ({cat})", key=f"sub_{cat}")
                    if st.button(f"➕ Tambah Sub {cat}", key=f"btn_add_sub_{cat}"):
                        add_subcategory(cat, new_sub)
                        st.success(f"Subkategori '{new_sub}' ditambahkan di {cat}")

                with sub_col2:
                    if subcats:
                        sub_to_del = st.selectbox(f"Hapus Subkategori ({cat})", subcats, key=f"del_sub_{cat}")
                        if st.button(f"🗑️ Hapus Sub {cat}", key=f"btn_del_sub_{cat}"):
                            delete_subcategory(cat, sub_to_del)
                            st.warning(f"Subkategori '{sub_to_del}' dihapus dari {cat}")

                with sub_col3:
                    if subcats:
                        old_sub = st.selectbox(f"Sub Lama ({cat})", subcats, key=f"old_sub_{cat}")
                        new_sub_name = st.text_input(f"Nama Baru Sub ({cat})", key=f"new_sub_{cat}")
                        if st.button(f"✏️ Rename Sub {cat}", key=f"btn_rename_sub_{cat}"):
                            rename_subcategory(cat, old_sub, new_sub_name)
                            st.info(f"Subkategori '{old_sub}' diubah menjadi '{new_sub_name}'")

                # Aset per subkategori
                for sub in get_subcategories(cat):
                    st.markdown(f"### 📑 Aset di {cat} / {sub}")
                    assets = get_assets(cat, sub)
                    if assets:
                        df = pd.DataFrame(assets)
                        df["link"] = df["link"].apply(make_clickable)
                        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

                        del_id = st.selectbox(f"Pilih aset untuk dihapus ({sub})", [a["id"] for a in assets], key=f"del_{cat}_{sub}")
                        if st.button(f"❌ Hapus Aset ({sub})", key=f"btn_del_asset_{cat}_{sub}"):
                            delete_asset(cat, sub, del_id)
                            st.warning("Aset dihapus.")
                    else:
                        st.info(f"Belum ada aset di {sub}")

                    with st.form(f"form_add_{cat}_{sub}", clear_on_submit=True):
                        nama = st.text_input("📌 Nama Aset", key=f"nama_{cat}_{sub}")
                        link = st.text_input("🔗 Link Aset", key=f"link_{cat}_{sub}")
                        submitted = st.form_submit_button("✅ Tambah Aset")
                        if submitted and nama and link:
                            add_asset(cat, sub, nama, link)
                            st.success(f"Aset '{nama}' ditambahkan di {cat}/{sub}")


# =========================
# III. Aset Micro Skill
# =========================
elif menu == "🗂️ Aset Micro Skill":
    st.markdown("## 🗂️ Aset Micro Skill")
    tab_materi, tab_visual = st.tabs(["Materi Micro Skill", "Visual/Infografis"])

    # --- Tab: Materi Micro Skill ---
    with tab_materi:
        st.subheader("Materi Micro Skill")
        if "materi_aset_df" not in st.session_state:
            st.session_state["materi_aset_df"] = pd.DataFrame({
                "Nama Aset": [],
                "Link Aset": []
            })
        if "show_form_materi" not in st.session_state:
            st.session_state["show_form_materi"] = False
        if "show_hapus_materi" not in st.session_state:
            st.session_state["show_hapus_materi"] = False

        st.markdown("## 📂 Manajemen Materi")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("➕ Tambah Materi", key="btn_tambah_materi"):
                st.session_state["show_form_materi"] = True
        with col2:
            if st.button("🗑️ Hapus Materi", key="btn_hapus_materi"):
                st.session_state["show_hapus_materi"] = True

        if st.session_state.get("show_form_materi", False):
            with st.form("form_tambah_materi", clear_on_submit=True):
                nama = st.text_input("📌 Nama Materi", key="materi_nama")
                link = st.text_input("🔗 Link Materi (Google Drive)", key="materi_link")
                submitted = st.form_submit_button("✅ Simpan Materi")
                if submitted and nama and link:
                    st.session_state["materi_aset_df"] = pd.concat(
                        [st.session_state["materi_aset_df"], pd.DataFrame([[nama, link]], columns=["Nama Aset", "Link Aset"])],
                        ignore_index=True
                    )
                    st.success(f"Materi **{nama}** berhasil ditambahkan!")
                    st.session_state["show_form_materi"] = False

        if st.session_state.get("show_hapus_materi", False):
            if not st.session_state["materi_aset_df"].empty:
                aset_list = st.session_state["materi_aset_df"]["Nama Aset"].tolist()
                hapus_nama = st.selectbox("Pilih materi yang ingin dihapus", aset_list, key="materi_hapus")
                if st.button("❌ Konfirmasi Hapus Materi", key="btn_konfirmasi_hapus_materi"):
                    st.session_state["materi_aset_df"] = st.session_state["materi_aset_df"][st.session_state["materi_aset_df"]["Nama Aset"] != hapus_nama]
                    st.warning(f"Materi **{hapus_nama}** sudah dihapus.")
                    st.session_state["show_hapus_materi"] = False
            else:
                st.info("Belum ada materi untuk dihapus.")
                st.session_state["show_hapus_materi"] = False

        st.markdown("### 📑 Daftar Materi")
        if not st.session_state["materi_aset_df"].empty:
            df_materi = st.session_state["materi_aset_df"].copy()
            df_materi["Link Aset"] = df_materi["Link Aset"].apply(make_clickable)
            st.markdown(df_materi.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data materi.")

    # --- Tab: Visual/Infografis ---
    with tab_visual:
        st.subheader("Visual/Infografis")
        if "visual_aset_df" not in st.session_state:
            st.session_state["visual_aset_df"] = pd.DataFrame({
                "Nama Aset": [],
                "Link Aset": []
            })
        if "show_form_visual" not in st.session_state:
            st.session_state["show_form_visual"] = False
        if "show_hapus_visual" not in st.session_state:
            st.session_state["show_hapus_visual"] = False

        st.markdown("## 📂 Manajemen Visual/Infografis")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("➕ Tambah Visual/Infografis", key="btn_tambah_visual"):
                st.session_state["show_form_visual"] = True
        with col2:
            if st.button("🗑️ Hapus Visual/Infografis", key="btn_hapus_visual"):
                st.session_state["show_hapus_visual"] = True

        if st.session_state.get("show_form_visual", False):
            with st.form("form_tambah_visual", clear_on_submit=True):
                nama = st.text_input("📌 Nama Visual/Infografis", key="visual_nama")
                link = st.text_input("🔗 Link Visual/Infografis (Google Drive)", key="visual_link")
                submitted = st.form_submit_button("✅ Simpan Visual/Infografis")
                if submitted and nama and link:
                    st.session_state["visual_aset_df"] = pd.concat(
                        [st.session_state["visual_aset_df"], pd.DataFrame([[nama, link]], columns=["Nama Aset", "Link Aset"])],
                        ignore_index=True
                    )
                    st.success(f"Visual/Infografis **{nama}** berhasil ditambahkan!")
                    st.session_state["show_form_visual"] = False

        if st.session_state.get("show_hapus_visual", False):
            if not st.session_state["visual_aset_df"].empty:
                aset_list = st.session_state["visual_aset_df"]["Nama Aset"].tolist()
                hapus_nama = st.selectbox("Pilih visual/infografis yang ingin dihapus", aset_list, key="visual_hapus")
                if st.button("❌ Konfirmasi Hapus Visual/Infografis", key="btn_konfirmasi_hapus_visual"):
                    st.session_state["visual_aset_df"] = st.session_state["visual_aset_df"][st.session_state["visual_aset_df"]["Nama Aset"] != hapus_nama]
                    st.warning(f"Visual/Infografis **{hapus_nama}** sudah dihapus.")
                    st.session_state["show_hapus_visual"] = False
            else:
                st.info("Belum ada visual/infografis untuk dihapus.")
                st.session_state["show_hapus_visual"] = False

        st.markdown("### 📑 Daftar Visual/Infografis")
        if not st.session_state["visual_aset_df"].empty:
            df_visual = st.session_state["visual_aset_df"].copy()
            df_visual["Link Aset"] = df_visual["Link Aset"].apply(make_clickable)
            st.markdown(df_visual.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data visual/infografis.")

# =========================
# IV. Bahan Upload
# =========================
elif menu == "☁️ Bahan Upload":
    st.markdown("## ☁️ Bahan Upload")
    tab_dokumen, tab_media = st.tabs(["Dokumen Pendukung", "Media/Gambar"])

    # --- Tab: Dokumen Pendukung ---
    with tab_dokumen:
        st.subheader("Dokumen Pendukung")
        assets = get_simple_assets("dokumen_aset")
        st.markdown("## 📂 Manajemen Dokumen")
        with st.form("form_tambah_dokumen", clear_on_submit=True):
            nama = st.text_input("📌 Nama Dokumen", key="dokumen_nama")
            link = st.text_input("🔗 Link Dokumen (Google Drive)", key="dokumen_link")
            submitted = st.form_submit_button("✅ Simpan Dokumen")
            if submitted and nama and link:
                add_simple_asset("dokumen_aset", nama, link)
                st.success(f"Dokumen **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih dokumen yang ingin dihapus", aset_list, key="dokumen_hapus")
            if st.button("❌ Konfirmasi Hapus Dokumen", key="btn_konfirmasi_hapus_dokumen"):
                delete_simple_asset("dokumen_aset", aset_id_map[hapus_nama])
                st.warning(f"Dokumen **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Dokumen")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data dokumen.")

    # --- Tab: Media/Gambar ---
    with tab_media:
        st.subheader("Media/Gambar")
        assets = get_simple_assets("media_aset")
        st.markdown("## 📂 Manajemen Media")
        with st.form("form_tambah_media", clear_on_submit=True):
            nama = st.text_input("📌 Nama Media", key="media_nama")
            link = st.text_input("🔗 Link Media (Google Drive)", key="media_link")
            submitted = st.form_submit_button("✅ Simpan Media")
            if submitted and nama and link:
                add_simple_asset("media_aset", nama, link)
                st.success(f"Media **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih media yang ingin dihapus", aset_list, key="media_hapus")
            if st.button("❌ Konfirmasi Hapus Media", key="btn_konfirmasi_hapus_media"):
                delete_simple_asset("media_aset", aset_id_map[hapus_nama])
                st.warning(f"Media **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Media")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data media.")

# =========================
# V. Formulir & Template
# =========================
elif menu == "📑 Formulir & Template":
    st.markdown("## 📑 Formulir & Template")
    tab_ppt, tab_dokumen_tpl = st.tabs(["Template PPT", "Template Dokumen"])

    # --- Tab: Template PPT ---
    with tab_ppt:
        st.subheader("Template PPT")
        assets = get_simple_assets("ppt_aset")
        st.markdown("## 📂 Manajemen PPT")
        with st.form("form_tambah_ppt", clear_on_submit=True):
            nama = st.text_input("📌 Nama PPT", key="ppt_nama")
            link = st.text_input("🔗 Link PPT (Google Drive)", key="ppt_link")
            submitted = st.form_submit_button("✅ Simpan PPT")
            if submitted and nama and link:
                add_simple_asset("ppt_aset", nama, link)
                st.success(f"PPT **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih PPT yang ingin dihapus", aset_list, key="ppt_hapus")
            if st.button("❌ Konfirmasi Hapus PPT", key="btn_konfirmasi_hapus_ppt"):
                delete_simple_asset("ppt_aset", aset_id_map[hapus_nama])
                st.warning(f"PPT **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar PPT")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data PPT.")

    # --- Tab: Template Dokumen ---
    with tab_dokumen_tpl:
        st.subheader("Template Dokumen")
        assets = get_simple_assets("dokumen_tpl_aset")
        st.markdown("## 📂 Manajemen Dokumen Template")
        with st.form("form_tambah_dokumen_tpl", clear_on_submit=True):
            nama = st.text_input("📌 Nama Dokumen Template", key="dokumen_tpl_nama")
            link = st.text_input("🔗 Link Dokumen Template (Google Drive)", key="dokumen_tpl_link")
            submitted = st.form_submit_button("✅ Simpan Dokumen Template")
            if submitted and nama and link:
                add_simple_asset("dokumen_tpl_aset", nama, link)
                st.success(f"Dokumen Template **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih dokumen template yang ingin dihapus", aset_list, key="dokumen_tpl_hapus")
            if st.button("❌ Konfirmasi Hapus Dokumen Template", key="btn_konfirmasi_hapus_dokumen_tpl"):
                delete_simple_asset("dokumen_tpl_aset", aset_id_map[hapus_nama])
                st.warning(f"Dokumen Template **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Dokumen Template")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data dokumen template.")

# =========================
# VI. Tema Micro Skill
# =========================
elif menu == "📘 Tema Micro Skill":
    st.markdown("## 📘 Tema Micro Skill")
    tab_tema, tab_pelatihan = st.tabs(["Daftar Tema", "Tema Pelatihan"])

    # --- Tab: Daftar Tema ---
    with tab_tema:
        st.subheader("Daftar Tema")
        assets = get_simple_assets("tema_aset")
        st.markdown("## 📂 Manajemen Tema")
        with st.form("form_tambah_tema", clear_on_submit=True):
            nama = st.text_input("📌 Nama Tema", key="tema_nama")
            link = st.text_input("🔗 Link Tema (Google Drive)", key="tema_link")
            submitted = st.form_submit_button("✅ Simpan Tema")
            if submitted and nama and link:
                add_simple_asset("tema_aset", nama, link)
                st.success(f"Tema **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih tema yang ingin dihapus", aset_list, key="tema_hapus")
            if st.button("❌ Konfirmasi Hapus Tema", key="btn_konfirmasi_hapus_tema"):
                delete_simple_asset("tema_aset", aset_id_map[hapus_nama])
                st.warning(f"Tema **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Tema")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data tema.")

    # --- Tab: Tema Pelatihan ---
    with tab_pelatihan:
        st.subheader("Tema Pelatihan")
        assets = get_simple_assets("tema_pelatihan_aset")
        st.markdown("## 📂 Manajemen Tema Pelatihan")
        with st.form("form_tambah_tema_pelatihan", clear_on_submit=True):
            nama = st.text_input("📌 Nama Tema Pelatihan", key="tema_pelatihan_nama")
            link = st.text_input("🔗 Link Tema Pelatihan (Google Drive)", key="tema_pelatihan_link")
            submitted = st.form_submit_button("✅ Simpan Tema Pelatihan")
            if submitted and nama and link:
                add_simple_asset("tema_pelatihan_aset", nama, link)
                st.success(f"Tema Pelatihan **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih tema pelatihan yang ingin dihapus", aset_list, key="tema_pelatihan_hapus")
            if st.button("❌ Konfirmasi Hapus Tema Pelatihan", key="btn_konfirmasi_hapus_tema_pelatihan"):
                delete_simple_asset("tema_pelatihan_aset", aset_id_map[hapus_nama])
                st.warning(f"Tema Pelatihan **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Tema Pelatihan")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data tema pelatihan.")

# =========================
# VII. Pengajuan Tema
# =========================
elif menu == "📝 Pengajuan Tema":
    st.markdown("## 📝 Pengajuan Tema")
    tab_form, tab_status = st.tabs(["Form Pengajuan", "Status Pengajuan"])

    # --- Tab: Form Pengajuan ---
    with tab_form:
        st.subheader("Form Pengajuan")
        assets = get_simple_assets("form_pengajuan_aset")
        st.markdown("## 📂 Manajemen Form Pengajuan")
        with st.form("form_tambah_pengajuan", clear_on_submit=True):
            nama = st.text_input("📌 Nama Form Pengajuan", key="pengajuan_nama")
            link = st.text_input("🔗 Link Form Pengajuan (Google Drive)", key="pengajuan_link")
            submitted = st.form_submit_button("✅ Simpan Form Pengajuan")
            if submitted and nama and link:
                add_simple_asset("form_pengajuan_aset", nama, link)
                st.success(f"Form Pengajuan **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih form pengajuan yang ingin dihapus", aset_list, key="pengajuan_hapus")
            if st.button("❌ Konfirmasi Hapus Form Pengajuan", key="btn_konfirmasi_hapus_pengajuan"):
                delete_simple_asset("form_pengajuan_aset", aset_id_map[hapus_nama])
                st.warning(f"Form Pengajuan **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Form Pengajuan")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data form pengajuan.")

    # --- Tab: Status Pengajuan ---
    with tab_status:
        st.subheader("Status Pengajuan")
        assets = get_simple_assets("status_pengajuan_aset")
        st.markdown("## 📂 Manajemen Status Pengajuan")
        with st.form("form_tambah_status_pengajuan", clear_on_submit=True):
            nama = st.text_input("📌 Nama Status Pengajuan", key="status_pengajuan_nama")
            link = st.text_input("🔗 Link Status Pengajuan (Google Drive)", key="status_pengajuan_link")
            submitted = st.form_submit_button("✅ Simpan Status Pengajuan")
            if submitted and nama and link:
                add_simple_asset("status_pengajuan_aset", nama, link)
                st.success(f"Status Pengajuan **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih status pengajuan yang ingin dihapus", aset_list, key="status_pengajuan_hapus")
            if st.button("❌ Konfirmasi Hapus Status Pengajuan", key="btn_konfirmasi_hapus_status_pengajuan"):
                delete_simple_asset("status_pengajuan_aset", aset_id_map[hapus_nama])
                st.warning(f"Status Pengajuan **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Status Pengajuan")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data status pengajuan.")

# =========================
# VIII. Kegiatan
# =========================
elif menu == "📅 Kegiatan":
    st.markdown("## 📅 Kegiatan")
    tab_jadwal, tab_dokumentasi = st.tabs(["Jadwal Kegiatan", "Dokumentasi"])

    # --- Tab: Jadwal Kegiatan ---
    with tab_jadwal:
        st.subheader("Jadwal Kegiatan")
        assets = get_simple_assets("jadwal_aset")
        st.markdown("## 📂 Manajemen Jadwal")
        with st.form("form_tambah_jadwal", clear_on_submit=True):
            nama = st.text_input("📌 Nama Jadwal", key="jadwal_nama")
            link = st.text_input("🔗 Link Jadwal (Google Drive)", key="jadwal_link")
            submitted = st.form_submit_button("✅ Simpan Jadwal")
            if submitted and nama and link:
                add_simple_asset("jadwal_aset", nama, link)
                st.success(f"Jadwal **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih jadwal yang ingin dihapus", aset_list, key="jadwal_hapus")
            if st.button("❌ Konfirmasi Hapus Jadwal", key="btn_konfirmasi_hapus_jadwal"):
                delete_simple_asset("jadwal_aset", aset_id_map[hapus_nama])
                st.warning(f"Jadwal **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Jadwal")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data jadwal.")

    # --- Tab: Dokumentasi ---
    with tab_dokumentasi:
        st.subheader("Dokumentasi")
        assets = get_simple_assets("dokumentasi_aset")
        st.markdown("## 📂 Manajemen Dokumentasi")
        with st.form("form_tambah_dokumentasi", clear_on_submit=True):
            nama = st.text_input("📌 Nama Dokumentasi", key="dokumentasi_nama")
            link = st.text_input("🔗 Link Dokumentasi (Google Drive)", key="dokumentasi_link")
            submitted = st.form_submit_button("✅ Simpan Dokumentasi")
            if submitted and nama and link:
                add_simple_asset("dokumentasi_aset", nama, link)
                st.success(f"Dokumentasi **{nama}** berhasil ditambahkan!")

        if assets:
            aset_list = [a["Nama Aset"] for a in assets]
            aset_id_map = {a["Nama Aset"]: a["id"] for a in assets}
            hapus_nama = st.selectbox("Pilih dokumentasi yang ingin dihapus", aset_list, key="dokumentasi_hapus")
            if st.button("❌ Konfirmasi Hapus Dokumentasi", key="btn_konfirmasi_hapus_dokumentasi"):
                delete_simple_asset("dokumentasi_aset", aset_id_map[hapus_nama])
                st.warning(f"Dokumentasi **{hapus_nama}** sudah dihapus.")

        st.markdown("### 📑 Daftar Dokumentasi")
        if assets:
            df = pd.DataFrame(assets)
            df["Link Aset"] = df["Link Aset"].apply(make_clickable)
            st.markdown(df[["Nama Aset", "Link Aset"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("Belum ada data dokumentasi.")

# =========================
# IX. Dashboard
# =========================
elif menu == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")
    st.write("📈 Ringkasan data dan analitik Micro Skill akan ditampilkan di sini.")

# =========================
# Footer
# =========================
st.markdown(
    """
    <hr>
    <center>
    <p style="color:gray; font-size:14px;">
    © 2025 | Aplikasi ini dibuat oleh <b>Yuliana</b>
    </p>
    </center>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: #004aad;
    }
    [data-testid="stSidebar"] * {
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
