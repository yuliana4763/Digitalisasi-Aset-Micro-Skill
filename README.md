# 📂 Digitalisasi Aset Micro Skill

Aplikasi web berbasis **Streamlit** untuk manajemen inventaris aset Micro Skill.  
Menggunakan **Firebase Firestore** sebagai database dan **Firebase Authentication** untuk login admin.

---

## 🚀 Fitur Utama
- Login admin (Firebase Authentication)
- CRUD aset (Tambah, Baca, Update, Hapus)
- Kategori & subkategori otomatis
- Penyimpanan data permanen di Firestore (multiuser)
- UI sederhana dan responsif (Streamlit)

---

## 📂 Struktur Direktori
DIGITALISASI-ASET-MICRO-SKILL/
├── app.py # Entry point aplikasi
├── login.py # UI login (Firebase Authentication)
├── inventory_aset_microskill.py # UI inventaris aset
├── firestore_utils.py # Modul koneksi Firestore + fungsi CRUD
├── requirements.txt # Dependency Python
├── README.md # Dokumentasi project
├── .gitignore # Ignore file sensitif
├── .streamlit/
│ └── config.toml # (opsional) Custom theme Streamlit
└── .secrets/
└── secrets.toml # Firebase Service Account (LOCAL only, jangan commit!)


---

## 🔑 Konfigurasi Secrets
Buat file `.streamlit/secrets.toml` **(untuk deploy ke Streamlit Cloud)**  
atau `.secrets/secrets.toml` **(untuk lokal)** dengan isi seperti ini:

```toml
# Root level
type = "service_account"
project_id = "your-project-id"
private_key_id = "xxxx"
private_key = "-----BEGIN PRIVATE KEY-----\nXXXXX\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk@your-project-id.iam.gserviceaccount.com"
client_id = "1234567890"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "xxxx"
private_key = "-----BEGIN PRIVATE KEY-----\nXXXXX\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk@your-project-id.iam.gserviceaccount.com"
client_id = "1234567890"

▶️ Cara Menjalankan Lokal
1.Clone repo:
git clone https://github.com/your-username/digitalisasi-aset-microskill.git
cd digitalisasi-aset-microskill

2. Install depedencies:
pip install -r requirements.txt

3. Jalankan Streamlit:
streamlit run app.py

☁️ Deploy ke Streamlit Cloud
1. Push repo ke GitHub.
2. Masuk ke Streamlit Cloud.
3. Hubungkan repo ini.
4. Tambahkan Secrets di menu App Settings → Secrets (copy isi secrets.toml).
5. Klik Deploy 🚀.

⚠️ Catatan
Jangan commit file secrets.toml ke GitHub (sudah di-ignore lewat .gitignore).
Untuk multiuser, atur Firestore Security Rules di Firebase Console.

