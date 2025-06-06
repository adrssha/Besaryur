import streamlit as st
import pandas as pd
import sqlite3
import os
import json
import time
from datetime import datetime

# =========================
# FUNGSI UNTUK MENGELOLA DATA USER & STOK
# =========================

# Fungsi untuk memuat data user dari file users.json
def load_users():
    import os
    default_users = {
        "admin": {"password": "admin123", "role": "admin"},
        "buyer1": {"password": "buyer123", "role": "buyer"}
    }

    file_path = "users.json"

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w") as f:
            json.dump(default_users, f, indent=4)
        return default_users

    with open(file_path, "r") as f:
        data = json.load(f)
        return data

# Fungsi untuk inisialisasi database
def init_db():
    """Inisialisasi database dengan penanganan yang lebih robust"""
    conn = sqlite3.connect('pesanan.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE pesanan
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT,
                    nomor_telepon TEXT,
                    alamat TEXT,
                    jumlah INTEGER,
                    metode TEXT,
                    total INTEGER,                       
                    tanggal_pengiriman TEXT,
                    waktu_pengiriman TEXT,
                    catatan TEXT,
                    status TEXT)''')
        conn.commit()
        c.execute("PRAGMA table_info(pesanan)")
        columns = [col[1] for col in c.fetchall()]

    except sqlite3.Error as err:
        print(f"Error inisialisasi database: {err}")
    finally:
        conn.close()

# Fungsi untuk menyimpan pesanan ke database
def save_pesanan_to_db(pesanan):
    conn = None
    try:
        conn = sqlite3.connect('pesanan.db')
        c = conn.cursor()
       
        required_columns = ['nama', 'nomor_telepon', 'alamat', 'jumlah', 'metode', 
                          'total', 'tanggal_pengiriman', 'waktu_pengiriman', 
                          'catatan', 'status']
        
        c.execute("PRAGMA table_info(pesanan)")
        existing_columns = [col[1] for col in c.fetchall()]
        for col in required_columns:
            if col not in existing_columns:
                try:
                    c.execute(f"ALTER TABLE pesanan ADD COLUMN {col} TEXT")
                    conn.commit()
                    print(f"Kolom {col} berhasil ditambahkan")
                except sqlite3.OperationalError as err:
                    print(f"Kolom {col} sudah ada atau error: {err}")
        c.execute('''INSERT INTO pesanan 
                    (nama, nomor_telepon, alamat, jumlah, metode, total,
                     tanggal_pengiriman, waktu_pengiriman, catatan, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (pesanan['Nama'], 
                 pesanan['Nomor Telepon'], 
                 pesanan['Alamat'],
                 pesanan['Jumlah'], 
                 pesanan['Metode'], 
                 pesanan['Total'],
                 pesanan['Tanggal Pengiriman'], 
                 pesanan['Waktu Pengiriman'],
                 pesanan['Catatan'], 
                 pesanan['Status']))
        conn.commit()
        return True
    except sqlite3.Error as err:
        if conn:
            conn.rollback()
        st.error(f"Database error: {err}") 
        return False
    finally:
        if conn:
            conn.close()

# Fungsi untuk membaca semua pesanan dari database
def get_all_pesanan():
    conn = sqlite3.connect('pesanan.db')
    try:
        # Pastikan hanya mengambil kolom yang diperlukan
        df = pd.read_sql_query("SELECT nama, nomor_telepon, alamat, jumlah, metode, total, tanggal_pengiriman, waktu_pengiriman, catatan, status FROM pesanan", conn)
        return df.to_dict('records')
    finally:
        conn.close()

# Panggil init_db saat aplikasi pertama kali dijalankan
init_db()

# Fungsi untuk menyimpan data user ke users.json
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Fungsi untuk memuat data stok dari file stok.json
def load_stok():
    if not os.path.exists("stok.json") or os.path.getsize("stok.json") == 0:
        return {}
    with open("stok.json", "r") as f:
        return json.load(f)

# Fungsi untuk menyimpan data stok ke file stok.json
def simpan_stok(stok_data):
    with open("stok.json", "w") as f:
        json.dump(stok_data, f, indent=4)

def init_mutasi_db():
    """Inisialisasi tabel mutasi stok"""
    with sqlite3.connect('pesanan.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS mutasi_stok (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produk TEXT NOT NULL,
                    jenis TEXT NOT NULL,
                    jumlah INTEGER NOT NULL,
                    harga_per_kilo INTEGER NOT NULL,
                    stok_sebelum INTEGER NOT NULL,
                    stok_sesudah INTEGER NOT NULL,
                    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    operator TEXT
                    )''')
        conn.commit()

def catat_mutasi(produk, jenis, jumlah, harga, stok_sebelum, operator):
    """Mencatat mutasi stok ke database"""
    stok_sesudah = stok_sebelum - jumlah if jenis == "Pengurangan" else stok_sebelum + jumlah
    with sqlite3.connect('pesanan.db') as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO mutasi_stok 
                    (produk, jenis, jumlah, harga_per_kilo, stok_sebelum, stok_sesudah, operator)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (produk, jenis, jumlah, harga, stok_sebelum, stok_sesudah, operator))
        conn.commit()

# =========================
# FUNGSI UNTUK MENGELOLA DATA LAPORAN KEUANGAN
# =========================
def init_finance_db():
    """Initialize finance database tables"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    try:
        # Jurnal Umum
        c.execute('''CREATE TABLE IF NOT EXISTS jurnal_umum
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    keterangan TEXT,
                    akun TEXT,
                    debit INTEGER,
                    kredit INTEGER)''')
        
        # Buku Besar
        c.execute('''CREATE TABLE IF NOT EXISTS buku_besar
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akun TEXT,
                    tanggal TEXT,
                    keterangan TEXT,
                    debit INTEGER,
                    kredit INTEGER,
                    saldo INTEGER)''')
        
        # Neraca Saldo
        c.execute('''CREATE TABLE IF NOT EXISTS neraca_saldo
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    akun TEXT,
                    debit INTEGER,
                    kredit INTEGER)''')
        
        # Laporan Laba Rugi
        c.execute('''CREATE TABLE IF NOT EXISTS laba_rugi
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    pendapatan INTEGER,
                    beban INTEGER,
                    laba_rugi INTEGER)''')
        
        # Neraca
        c.execute('''CREATE TABLE IF NOT EXISTS neraca
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    aset INTEGER,
                    kewajiban INTEGER,
                    ekuitas INTEGER)''')
        
        conn.commit()
    except sqlite3.Error as err:
        print(f"Error inisialisasi database keuangan: {err}")
    finally:
        conn.close()

# Panggil init_finance_db saat aplikasi pertama kali dijalankan
init_finance_db()

def save_jurnal_umum(tanggal, keterangan, akun, debit, kredit):
    """Save journal entry to database"""
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO jurnal_umum 
                    (tanggal, keterangan, akun, debit, kredit)
                    VALUES (?, ?, ?, ?, ?)''',
                (tanggal, keterangan, akun, debit, kredit))
        conn.commit()
        return True
    except sqlite3.Error as err:
        conn.rollback()
        st.error(f"Database error: {err}")
        return False
    finally:
        conn.close()

def get_jurnal_umum():
    """Get all journal entries"""
    conn = sqlite3.connect('finance.db')
    try:
        df = pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY tanggal DESC", conn)
        return df
    finally:
        conn.close()

def generate_laporan():
    """Generate all financial reports based on journal entries"""
    conn = sqlite3.connect('finance.db')
    try:
        # Generate Buku Besar
        jurnal_df = pd.read_sql_query("SELECT * FROM jurnal_umum", conn)
        
        if not jurnal_df.empty:
            # Buku Besar
            buku_besar = jurnal_df.groupby('akun').agg({
                'debit': 'sum',
                'kredit': 'sum'
            }).reset_index()
            buku_besar['saldo'] = buku_besar['debit'] - buku_besar['kredit']
            
            # Clear existing data
            c = conn.cursor()
            c.execute("DELETE FROM buku_besar")
            
            # Insert new data
            for _, row in buku_besar.iterrows():
                c.execute('''INSERT INTO buku_besar 
                            (akun, tanggal, keterangan, debit, kredit, saldo)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                        (row['akun'], datetime.now().strftime("%Y-%m-%d"), 
                         "Saldo per " + datetime.now().strftime("%d/%m/%Y"),
                         row['debit'], row['kredit'], row['saldo']))
            
            # Neraca Saldo
            c.execute("DELETE FROM neraca_saldo")
            for _, row in buku_besar.iterrows():
                c.execute('''INSERT INTO neraca_saldo 
                            (tanggal, akun, debit, kredit)
                            VALUES (?, ?, ?, ?)''',
                        (datetime.now().strftime("%Y-%m-%d"), 
                         row['akun'], row['debit'], row['kredit']))
            
            # Laporan Laba Rugi
            pendapatan = jurnal_df[jurnal_df['akun'] == 'Pendapatan Penjualan']['kredit'].sum()
            beban = jurnal_df[jurnal_df['akun'].str.startswith('Beban')]['debit'].sum()
            laba_rugi = pendapatan - beban
            
            c.execute("DELETE FROM laba_rugi")
            c.execute('''INSERT INTO laba_rugi 
                        (tanggal, pendapatan, beban, laba_rugi)
                        VALUES (?, ?, ?, ?)''',
                    (datetime.now().strftime("%Y-%m-%d"), pendapatan, beban, laba_rugi))
            
            # Neraca
            # Aset: Kas, Piutang Usaha, Persediaan, Peralatan
            akun_aset = ['Kas', 'Piutang Usaha', 'Persediaan', 'Peralatan']
            aset = jurnal_df[jurnal_df['akun'].isin(akun_aset)]['debit'].sum() - \
                   jurnal_df[jurnal_df['akun'].isin(akun_aset)]['kredit'].sum()
            
            # Kewajiban: Utang Usaha
            akun_kewajiban = ['Utang Usaha']
            kewajiban = jurnal_df[jurnal_df['akun'].isin(akun_kewajiban)]['kredit'].sum() - \
                        jurnal_df[jurnal_df['akun'].isin(akun_kewajiban)]['debit'].sum()
            
            # Ekuitas: Modal + Laba Rugi
            modal = jurnal_df[jurnal_df['akun'] == 'Modal']['kredit'].sum() - \
                    jurnal_df[jurnal_df['akun'] == 'Modal']['debit'].sum()
            ekuitas = modal + laba_rugi
            
            c.execute("DELETE FROM neraca")
            c.execute('''INSERT INTO neraca 
                        (tanggal, aset, kewajiban, ekuitas)
                        VALUES (?, ?, ?, ?)''',
                    (datetime.now().strftime("%Y-%m-%d"), aset, kewajiban, ekuitas))
            
            conn.commit()
    except sqlite3.Error as err:
        conn.rollback()
        st.error(f"Error generating reports: {err}")
    finally:
        conn.close()

def generate_neraca():
    conn = sqlite3.connect('finance.db')
    
    # Hitung total aset
    aset_query = """
        SELECT SUM(
            CASE 
                WHEN akun IN ('Kas', 'Peralatan', 'Persediaan', 'Piutang Usaha') 
                THEN debit - kredit 
                ELSE 0 
            END
        ) as total_aset
        FROM jurnal_umum
    """
    
    # Hitung total kewajiban
    kewajiban_query = """
        SELECT SUM(
            CASE 
                WHEN akun = 'Utang Usaha' 
                THEN kredit - debit 
                ELSE 0 
            END
        ) as total_kewajiban
        FROM jurnal_umum
    """
    
    # Hitung modal awal
    modal_query = "SELECT SUM(kredit) FROM jurnal_umum WHERE akun = 'Modal'"
    
    # Hitung laba bersih
    laba_query = """
        SELECT 
            SUM(CASE WHEN akun = 'Pendapatan Penjualan' THEN kredit ELSE 0 END) -
            SUM(CASE WHEN akun IN ('Beban Gaji', 'Beban Sewa', 'Beban Listrik') THEN debit ELSE 0 END)
        FROM jurnal_umum
    """
    
    # Eksekusi query
    total_aset = conn.execute(aset_query).fetchone()[0] or 0
    total_kewajiban = conn.execute(kewajiban_query).fetchone()[0] or 0
    modal = conn.execute(modal_query).fetchone()[0] or 0
    laba_bersih = conn.execute(laba_query).fetchone()[0] or 0
    
    total_ekuitas = modal + laba_bersih
    
    # Update tabel neraca
    conn.execute("DELETE FROM neraca")
    conn.execute(
        "INSERT INTO neraca (tanggal, aset, kewajiban, ekuitas) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), total_aset, total_kewajiban, total_ekuitas)
    )
    
    conn.commit()
    conn.close()

def delete_all_finance_data():
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Pastikan nama tabel sesuai dengan database
        tables = ["jurnal_umum", "buku_besar", "neraca_saldo", "laba_rugi", "neraca"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Deleted from {table}: {cursor.rowcount} rows")  # Debug
        
        conn.commit()
        return True
    except Exception as e:
        print("Error:", e)  # Debug
        return False
    finally:
        conn.close()

# =========================
# INISIALISASI STATUS LOGIN SAAT APLIKASI DIMULAI
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.show_register = False

# =========================
# HALAMAN LOGIN
# =========================
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    users = load_users()  # Untuk mengmbil data user dari file

    if st.button("Login"):
        user = users.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Selamat datang, {username}!")
            st.rerun()
        else:
            st.error("Username atau password salah!")

# =========================
# HALAMAN REGISTER USER BARU
# =========================
def register_user():
    st.title("📝 Register")
    new_username = st.text_input("Buat Username")
    new_password = st.text_input("Buat Password", type="password")
    confirm_password = st.text_input("Konfirmasi Password", type="password")

    if st.button("Register"):
        users = load_users()
        if new_username in users:
            st.error("Username sudah digunakan!")
        elif new_password != confirm_password:
            st.error("Password tidak cocok!")
        else:
            # Simpan user baru sebagai buyer
            users[new_username] = {"password": new_password, "role": "buyer"}
            save_users(users)
            st.success("Registrasi berhasil! Silakan login.")
            st.session_state.show_register = False
            st.rerun()

# =========================
# LOGIKA UNTUK MENAMPILKAN LOGIN ATAU REGISTER
# =========================
if not st.session_state.logged_in:
    if st.session_state.show_register:
        register_user()
    else:
        login()
        st.button("Belum punya akun? Register", on_click=lambda: st.session_state.update(show_register=True))

# =========================
# MENU NAVIGASI SETELAH LOGIN
# =========================        
else:
    with st.sidebar:
        st.title("🌿 BESARYUR")
        role = st.session_state.role

        # Tampilkan menu berdasarkan role
        if role == "admin":
            menu = st.radio("Pilih Halaman", ["🏠Home", "📦Produk", "📥 Update Stok", "🛒Order Disini", "📊 Data Pesanan", "💰 Laporan Keuangan"], key="menu_sidebar")
        else:
            menu = st.radio("Pilih Halaman", ["🏠Home", "📦Produk", "🛒Order Disini"], key="menu_sidebar")

        # Tombol logout
        if st.sidebar.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

# =====================
# HALAMAN HOME (BERANDA)
# =====================
    if menu == "🏠Home":
        st.title("🌿 BESARYUR")
        st.subheader("Halo pecinta selada! Selamat datang di website kami 💚")
        st.markdown("BESARYUR hadir di Semarang khususnya daerah Gunung pati dan sekitarnya, kami memiliki tujuan untuk dapat memenuhi kebutuhan selada segar anda 🥬✨")

        # 4 Langkah Proses Pemesanan
        st.title("4 Langkah Proses Pemesanan")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("#### 📝 Order")
            st.caption("Order melalui klik form pemesanan.")

        with col2:
            st.markdown("#### ✅ Stok")
            st.caption("Admin akan mengecek status ketersediaan.")

        with col3:
            st.markdown("#### 🚚 Delivery")
            st.caption("Pengiriman akan segera dilakukan.")

        with col4:
            st.markdown("#### ✅ Selesai")
            st.caption("Proses selesai, tinggal menunggu pesanan.")

        # Tombol untuk menampilkan galeri foto
        if st.button("Foto Produk Kami"):
            st.write("BERSARYUR adalah aplikasi yang dikembangkan untuk membantu petani urban yang menumbuhkan selada hidroponik dengan penuh kasih sayang. Berikut adalah foto produk yang kami kembangkan:")
            st.markdown("### 📸 Galeri Kegiatan Kami")

            image_paths = [
                "image/gambar1.jpg",
                "image/gambar2.jpg",
                "image/gambar3.jpg",
                "image/gambar4.jpg",
                "image/gambar5.jpg",
                "image/gambar6.jpg"]

        # Menampilkan 3 gambar per baris
            for i in range(0, len(image_paths), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(image_paths):
                        with cols[j]:
                            st.image(image_paths[i + j], use_container_width=True)
# =====================
# HALAMAN PRODUK
# ===================== 
    elif menu == "📦Produk":
        stok_data = load_stok() # Load data stok dari file
        nama_produk = "Selada"  # Nama produk yang dijual
        stok = stok_data.get(nama_produk, {}).get("stok", 0)
        harga_per_kilo = stok_data.get(nama_produk, {}).get("harga_per_kilo", 15000)

        st.markdown(f"### {nama_produk}")
        st.write(f"**Stok tersedia:** {stok} kg")
        st.write(f"**Harga per kilo:** Rp {harga_per_kilo:,}")

        jumlah_pesanan = 0
        total_harga = 0

        # Jika stok tersedia, tampilkan form pemesanan
        if stok > 0:
            jumlah_pesanan = st.number_input(
                "Jumlah yang ingin dibeli (kg)",
                min_value=1,
                max_value=stok_data[nama_produk]["stok"],
                value=1,
                step=1)
            
            total_harga = jumlah_pesanan * harga_per_kilo
            st.write(f"**Total Harga:** Rp {total_harga:,}")

        # Simpan pilihan user ke session_state untuk dipakai di order
            if st.button("Pesan Sekarang"):
                if jumlah_pesanan > stok:
                    st.error("Jumlah pesanan melebihi stok yang tersedia.")
                else:
                    st.session_state["produk"] = {
                    "nama": nama_produk,
                    "jumlah": jumlah_pesanan,
                    "total": total_harga }

        # Tampilkan ringkasan pesanan
            if "produk" in st.session_state:
                st.subheader("📝 Review Pesanan Anda")
                st.write(f"**Produk:** {st.session_state['produk']['nama']}")
                st.write(f"**Jumlah:** {st.session_state['produk']['jumlah']} kg")
                st.write(f"**Total Harga:** Rp {st.session_state['produk']['total']:,}")

            if st.button("Edit Pesanan"):
                # Kosongkan session_state agar user bisa input ulang
                if "produk" in st.session_state:
                    del st.session_state["produk"]
                    st.rerun()
        else:
            st.warning(f"Stok tidak mencukupi. Stok tersedia hanya {stok} kg.")

# =====================
# HALAMAN ORDER FORM
# =====================
    elif menu =="🛒Order Disini":
        init_db()
        init_mutasi_db()
        if "page" not in st.session_state:
            st.session_state["page"] = "order"
        # Pastikan produk sudah dipilih sebelumnya
        if "produk" not in st.session_state:
            st.error("Silakan pilih produk dan jumlah pesanan terlebih dahulu.")
            st.stop()

    # 1. FORMULIR ORDER
        if st.session_state["page"] == "order":
            st.title("📝 Form Pemesanan")
            try:
                with open("stok.json", "r") as file:
                    stok_data = json.load(file)
            except Exception as e:
                st.error(f"Gagal memuat data stok: {str(e)}")
                st.stop()
    
            with st.form("order_form"):
                nama = st.text_input("Nama Pemesan")
                nomor_telepon = st.text_input("Nomor Telepon")
                alamat = st.text_area("Alamat Pengiriman")
                metode = st.selectbox("Metode Pembayaran", ["Transfer Bank", "QRIS"], key="metode_pembayaran_order")
                catatan = st.text_area("Catatan Tambahan (opsional)")
                tanggal_kirim = st.date_input("Tanggal Pengiriman")
                waktu_kirim = st.time_input("Waktu Pengiriman")

                # Menampilkan informasi pesanan dari session
                produk = st.session_state["produk"]
                jumlah = st.number_input("Jumlah Pesanan(kg)", value=produk["jumlah"], min_value=0, step=1, disabled=True)
                total_harga = st.text_input("Total Harga (Rp)", value=f"Rp {produk['total']:,}", disabled=True)

                submit_button = st.form_submit_button("Kirim Pesanan")

            if submit_button:
                if not all([nama, nomor_telepon, alamat]):
                    st.error("❗ Harap isi semua kolom wajib")
                else:
                    try:
                        # Buat data pesanan baru
                        pesanan_baru = {
                            "Nama": nama,
                            "Nomor Telepon": nomor_telepon,
                            "Alamat": alamat,
                            "Jumlah": jumlah,
                            "Metode": metode,
                            "Total": produk["total"],
                            "Tanggal Pengiriman": tanggal_kirim.strftime("%Y-%m-%d"),
                            "Waktu Pengiriman": waktu_kirim.strftime("%H:%M"),
                            "Catatan": catatan,
                            "Status": "Diproses"
                        }
                        # Simpan ke database
                        if save_pesanan_to_db(pesanan_baru):
                            # CATAT MUTASI STOK SEBELUM UPDATE <-- TAMBAHKAN INI
                            catat_mutasi(
                                produk=produk["nama"],
                                jenis="Pengurangan",
                                jumlah=produk["jumlah"],
                                harga=stok_data[produk["nama"]]["harga_per_kilo"],
                                stok_sebelum=stok_data[produk["nama"]]["stok"],
                                operator=nama
                            )
                            # Update stock hanya jika penyimpanan ke database berhasil
                            stok_data[produk["nama"]]["stok"] -= produk["jumlah"]
                            with open("stok.json", "w") as file:
                                json.dump(stok_data, file)

                            # Juga simpan ke session_state untuk tampilan langsung
                            st.session_state.update({
                                "page": "pembayaran",
                                "pesanan_dikirim": True,
                                "metode_pembayaran": metode,
                                "jumlah_pembayaran": produk["total"]
                            })
                            st.success("Pesanan berhasil dikirim! Terima kasih 😊")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Gagal menyimpan pesanan: {str(e)}")
                    except Exception as err:
                        st.error(f"Terjadi kesalahan: {err}")
            
        # 2. HALAMAN PEMBAYARAN
        elif st.session_state.get("page") == "pembayaran":
            st.subheader("Konfirmasi Pembayaran")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Pembayaran", f"Rp {st.session_state.jumlah_pembayaran:,.0f}")
                # Upload bukti pembayaran
                bukti = st.file_uploader("Upload Bukti Pembayaran", type=["jpg", "jpeg", "png", "pdf"], key="file_upload_bukti")
                if bukti is not None:
                    try:
                        os.makedirs("bukti_pembayaran", exist_ok=True)
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        file_ext = bukti.name.split('.')[-1]
                        filename = f"bukti_{st.session_state.username}_{timestamp}.{file_ext}"
                        filepath = os.path.join("bukti_pembayaran", filename)
                    
                        with open(filepath, "wb") as f:
                            f.write(bukti.getbuffer())
                        if bukti.type.startswith("image/"):
                            st.image(bukti, caption="Bukti Pembayaran", width=300)
                        elif bukti.type == "application/pdf":
                            st.write("📄 File PDF berhasil diunggah")
                        st.success(f"Bukti pembayaran tersimpan sebagai: {filename}")
                        st.session_state["bukti_uploaded"] = True
                    except Exception as e:
                         st.error(f"Gagal menyimpan bukti pembayaran: {str(e)}")
            with col2:
                if st.session_state.metode_pembayaran == "QRIS":
                    st.image("image/qris.jpg", caption="QRIS Payment", width=200)
                else:
                    st.write("**Transfer Bank**")
                    st.write("Bank: Mandiri")
                    st.write("No. Rek: 1234567890")
                    st.write("Nama: PT BESAYUR")
                    st.image("image/bank.png", caption="Transfer Instructions", width=200)
            
            st.divider()
            st.image("image/qr_wa.jpg", caption="Konfirmasi via WhatsApp", width=150)
            st.info("📱 Silakan konfirmasi admin setelah mengupload bukti pembayaran.")

            if st.button("Kembali ke Beranda"):
                if not st.session_state.get("bukti_uploaded"):
                    st.warning("Anda belum mengupload bukti pembayaran")
                else:
                    st.session_state.page = "order"
                    st.rerun()

    elif menu == "📊 Data Pesanan":
        st.title("📊 Data Pesanan")
        # Ambil data dari database
        try:
            all_pesanan = get_all_pesanan()
            if not all_pesanan:
                st.warning("Belum ada data pesanan")
                st.stop()

            # Clean column names and order
            df = pd.DataFrame(all_pesanan).rename(columns={
                "nama": "Nama",
                "nomor_telepon": "Telepon",
                "alamat": "Alamat",
                "jumlah": "Jumlah (kg)",
                "metode": "Pembayaran",
                "total": "Total (Rp)",
                "tanggal_pengiriman": "Tanggal",
                "waktu_pengiriman": "Waktu",
                "catatan": "Catatan",
                "status": "Status"
            })

            # Format currency
            df["Total (Rp)"] = df["Total (Rp)"].apply(lambda x: f"Rp {x:,}")
            
            # Display data
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Tanggal": st.column_config.DateColumn(format="YYYY-MM-DD"),
                    "Waktu": st.column_config.TimeColumn(format="HH:mm")
                }
            )

            # Status update section
            st.divider()
            with st.expander("Ubah Status Pesanan"):
                selected_name = st.selectbox("Pilih Pesanan", df["Nama"].unique())
                new_status = st.selectbox("Status Baru", ["Diproses", "Dikirim", "Selesai", "Dibatalkan"])
               
                if st.button("Update Status", type="primary"):
                    try:
                        with sqlite3.connect('pesanan.db') as conn:
                            c = conn.cursor()
                            c.execute(
                                "UPDATE pesanan SET status = ? WHERE nama = ?", 
                                (new_status, selected_name)
                            )
                            conn.commit()
                        st.success(f"Status pesanan {selected_name} diperbarui!")
                        time.sleep(1)
                        st.rerun()
                    except sqlite3.Error as err:
                        st.error(f"Gagal mengupdate status: {err}")
                    
        except Exception as err:
            st.error(f"Terjadi kesalahan: {err}")

# =====================
# HALAMAN UPDATE STOK (ADMIN) dengan Tabel Mutasi
# =====================
    elif menu == "📥 Update Stok":
        st.title("📥 Update Stok Produk")
        init_mutasi_db()
        # Fungsi untuk inisialisasi database mutasi stok
        def init_mutasi_db():
            with sqlite3.connect('pesanan.db') as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS mutasi_stok (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            produk TEXT NOT NULL,
                            jenis TEXT NOT NULL,
                            jumlah INTEGER NOT NULL,
                            harga_per_kilo INTEGER NOT NULL,
                            stok_sebelum INTEGER NOT NULL,
                            stok_sesudah INTEGER NOT NULL,
                            waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            operator TEXT
                            )''')
                conn.commit()
        
        # Fungsi untuk mencatat mutasi stok
        def catat_mutasi(produk, jenis, jumlah, harga, stok_sebelum, operator):
            stok_sesudah = stok_sebelum + jumlah if jenis == "Penambahan" else stok_sebelum - jumlah
            with sqlite3.connect('pesanan.db') as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO mutasi_stok 
                            (produk, jenis, jumlah, harga_per_kilo, stok_sebelum, stok_sesudah, operator)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (produk, jenis, jumlah, harga, stok_sebelum, stok_sesudah, operator))
                conn.commit()
        
        # Fungsi untuk mendapatkan semua mutasi stok
        def get_all_mutasi():
            with sqlite3.connect('pesanan.db') as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM mutasi_stok ORDER BY waktu DESC")
                return c.fetchall()
        
        # Fungsi untuk menghapus mutasi stok
        def delete_mutasi(id_mutasi):
            with sqlite3.connect('pesanan.db') as conn:
                c = conn.cursor()
                c.execute("DELETE FROM mutasi_stok WHERE id = ?", (id_mutasi,))
                conn.commit()
        
        # Inisialisasi database mutasi
        init_mutasi_db()
        
        # Baca data stok
        with open("stok.json", "r") as file:
            stok_data = json.load(file)
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("Update Stok")
            nama_produk = st.selectbox("Pilih Produk", list(stok_data.keys()), key="produk_select")
            
            # Ambil data stok dan harga dari produk yang dipilih
            stok_sekarang = stok_data[nama_produk]["stok"]
            harga_sekarang = stok_data[nama_produk]["harga_per_kilo"]
            
            # Tampilkan informasi stok
            st.metric("Stok saat ini", f"{stok_sekarang} kg")
            st.write(f"Harga per kilo saat ini: Rp {harga_sekarang:,}")
            
            tambahan_stok = st.number_input("Tambahkan Stok (kg)", min_value=0, step=1, key="tambah_stok")
            harga_baru = st.number_input("Update Harga per Kilo (opsional)", min_value=0, value=harga_sekarang, step=1000, key="harga_baru")
            
            if st.button("Simpan Perubahan"):
                # Catat penambahan stok jika ada
                if tambahan_stok > 0:
                    catat_mutasi(
                        produk=nama_produk,
                        jenis="Penambahan",
                        jumlah=tambahan_stok,
                        harga=harga_baru,
                        stok_sebelum=stok_sekarang,
                        operator=st.session_state.username
                    )
                
                # Catat perubahan harga jika ada
                if harga_baru != harga_sekarang:
                    catat_mutasi(
                        produk=nama_produk,
                        jenis="Perubahan Harga",
                        jumlah=0,
                        harga=harga_baru,
                        stok_sebelum=stok_sekarang,
                        operator=st.session_state.username
                    )
                
                # Update stok.json
                stok_data[nama_produk]["stok"] += tambahan_stok
                stok_data[nama_produk]["harga_per_kilo"] = harga_baru
                simpan_stok(stok_data)
                st.success(f"Stok untuk {nama_produk} berhasil diperbarui!")
                st.rerun()
        
        with col2:
            st.subheader("Mutasi Stok")
            
            # Tampilkan semua mutasi stok
            all_mutasi = get_all_mutasi()
            
            if all_mutasi:
                # Buat dataframe untuk tampilan
                df = pd.DataFrame(all_mutasi, columns=[
                    "ID", "Produk", "Jenis", "Jumlah", "Harga", 
                    "Stok Sebelum", "Stok Sesudah", "Waktu", "Operator"
                ])
                
                # Format kolom
                df["Harga"] = df["Harga"].apply(lambda x: f"Rp {x:,}")
                df["Jumlah"] = df.apply(lambda row: f"+{row['Jumlah']}" if row["Jenis"] == "Penambahan" else f"-{row['Jumlah']}", axis=1)
                
                # Tampilkan tabel dengan fitur filter
                st.dataframe(
                    df.drop(columns=["ID"]),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Waktu": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
                        "Jumlah": st.column_config.TextColumn("Perubahan")
                    }
                )
                
                # Fitur penghapusan data mutasi (hanya untuk admin)
                if st.session_state.username == "admin":
                    with st.expander("Hapus Data Mutasi"):
                        mutasi_to_delete = st.selectbox(
                            "Pilih Mutasi yang akan dihapus",
                            options=[f"{m[0]} - {m[1]} ({m[2]})" for m in all_mutasi],
                            key="delete_select"
                        )
                        
                        if st.button("Hapus Mutasi Terpilih", type="secondary"):
                            id_to_delete = int(mutasi_to_delete.split(" - ")[0])
                            delete_mutasi(id_to_delete)
                            st.success("Data mutasi berhasil dihapus!")
                            st.rerun()
            else:
                st.info("Belum ada data mutasi stok")

# =========================
# HALAMAN LAPORAN KEUANGAN
# =========================
    elif menu == "💰 Laporan Keuangan":
        st.title("💰 Laporan Keuangan")
        
        if st.button("🔄 Reset Semua Data Keuangan", type="primary"):
            if st.session_state.get('confirm_reset', False):
                # Eksekusi reset
                conn = sqlite3.connect('finance.db')
                cursor = conn.cursor()
                
                # Hapus semua data dari tabel terkait
                tables = ['jurnal_umum', 'buku_besar', 'neraca_saldo', 'laba_rugi', 'neraca']
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                
                conn.commit()
                conn.close()
                
                st.success("Semua data keuangan telah direset!")
                st.session_state.confirm_reset = False
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Apakah Anda yakin ingin mereset semua data keuangan? Tindakan ini tidak dapat dibatalkan!")
        
        # Jika konfirmasi reset aktif, tampilkan tombol batal
        if st.session_state.get('confirm_reset', False):
            if st.button("❌ Batalkan Reset"):
                st.session_state.confirm_reset = False
                st.rerun()

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Jurnal Umum", 
            "Buku Besar", 
            "Neraca Saldo", 
            "Laba Rugi", 
            "Neraca"
        ])
        
        with tab1:
            st.subheader("Jurnal Umum")
            
            with st.expander("Tambah Entri Jurnal"):
                with st.form("jurnal_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        tanggal = st.date_input("Tanggal")
                    with col2:
                        akun = st.selectbox("Akun", [
                            "Kas", "Piutang Usaha", "Persediaan", 
                            "Peralatan", "Utang Usaha", "Modal", 
                            "Pendapatan Penjualan", "Beban Gaji", 
                            "Beban Sewa", "Beban Listrik"
                        ])
                    
                    keterangan = st.text_input("Keterangan")
                    debit = st.number_input("Debit (Rp)", min_value=0, step=1000)
                    kredit = st.number_input("Kredit (Rp)", min_value=0, step=1000)
                    
                    if st.form_submit_button("Simpan Jurnal"):
                        if debit > 0 and kredit > 0:
                            st.error("Hanya boleh mengisi debit atau kredit, tidak keduanya")
                        elif debit == 0 and kredit == 0:
                            st.error("Harap isi debit atau kredit")
                        else:
                            if save_jurnal_umum(
                                tanggal.strftime("%Y-%m-%d"),
                                keterangan,
                                akun,
                                debit,
                                kredit
                            ):
                                generate_laporan()
                                st.success("Jurnal berhasil disimpan!")
                                time.sleep(1)
                                st.rerun()
            
            st.subheader("Data Jurnal Umum")
            jurnal_df = get_jurnal_umum()
            
            if not jurnal_df.empty:
                jurnal_df['tanggal'] = pd.to_datetime(jurnal_df['tanggal'])
                jurnal_df = jurnal_df.sort_values('tanggal', ascending=False)
                jurnal_df['debit'] = jurnal_df['debit'].apply(lambda x: f"Rp {x:,}" if x > 0 else "")
                jurnal_df['kredit'] = jurnal_df['kredit'].apply(lambda x: f"Rp {x:,}" if x > 0 else "")
                
                st.dataframe(
                    jurnal_df.drop(columns=['id']),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "tanggal": st.column_config.DateColumn(format="YYYY-MM-DD")
                    }
                )
            else:
                st.info("Belum ada data jurnal")
        
        with tab2:
            st.subheader("Buku Besar")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Tanggal Mulai", 
                                        value=pd.to_datetime("2024-01-01"),
                                        key="buku_besar_start")  # <-- Tambahkan key unik
            with col2:
                end_date = st.date_input("Tanggal Sampai", 
                                    value=pd.to_datetime("2024-12-31"),
                                    key="buku_besar_end")
            conn = sqlite3.connect('finance.db')
            buku_besar_df = pd.read_sql_query(
                f"SELECT * FROM buku_besar WHERE tanggal BETWEEN '{start_date}' AND '{end_date}'", 
                conn
            )
            conn.close()
            
            if not buku_besar_df.empty:
                buku_besar_df['debit'] = buku_besar_df['debit'].apply(lambda x: f"Rp {x:,}" if x > 0 else "")
                buku_besar_df['kredit'] = buku_besar_df['kredit'].apply(lambda x: f"Rp {x:,}" if x > 0 else "")
                buku_besar_df['saldo'] = buku_besar_df['saldo'].apply(lambda x: f"Rp {x:,}")
                
                st.dataframe(
                    buku_besar_df.drop(columns=['id']),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "tanggal": st.column_config.DateColumn(format="YYYY-MM-DD")
                    }
                )
            else:
                st.info("Belum ada data buku besar")
        
        with tab3:
            st.subheader("Neraca Saldo")
            conn = sqlite3.connect('finance.db')
            neraca_saldo_df = pd.read_sql_query("SELECT * FROM neraca_saldo", conn)
            conn.close()
            
            if not neraca_saldo_df.empty:
                neraca_saldo_df['debit'] = neraca_saldo_df['debit'].apply(lambda x: f"Rp {x:,}")
                neraca_saldo_df['kredit'] = neraca_saldo_df['kredit'].apply(lambda x: f"Rp {x:,}")
                
                st.dataframe(
                    neraca_saldo_df.drop(columns=['id']),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "tanggal": st.column_config.DateColumn(format="YYYY-MM-DD")
                    }
                )
                
                total_debit = neraca_saldo_df['debit'].str.replace("Rp ", "").str.replace(",", "").astype(float).sum()
                total_kredit = neraca_saldo_df['kredit'].str.replace("Rp ", "").str.replace(",", "").astype(float).sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Debit", f"Rp {total_debit:,.0f}")
                col2.metric("Total Kredit", f"Rp {total_kredit:,.0f}")
                
                if abs(total_debit - total_kredit) > 1:  # Allow for small rounding differences
                    st.error("Neraca tidak balance! Periksa kembali entri jurnal Anda.")
            else:
                st.info("Belum ada data neraca saldo")
        
        with tab4:
            st.subheader("Laporan Laba Rugi")
    
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Tanggal Mulai", 
                                        value=pd.to_datetime("2024-01-01"),
                                        key="laba_rugi_start")  # <-- Key berbeda
            with col2:
                end_date = st.date_input("Tanggal Sampai", 
                                    value=pd.to_datetime("2024-12-31"),
                                    key="laba_rugi_end")  # <-- Key berbeda
            
            conn = sqlite3.connect('finance.db')
            
            # Query untuk menghitung pendapatan dan beban dalam periode terpilih
            query = f"""
                SELECT 
                    SUM(CASE WHEN akun = 'Pendapatan Penjualan' THEN kredit ELSE 0 END) as pendapatan,
                    SUM(CASE WHEN akun IN ('Beban Gaji', 'Beban Sewa', 'Beban Listrik') THEN debit ELSE 0 END) as beban
                FROM jurnal_umum
                WHERE tanggal BETWEEN '{start_date}' AND '{end_date}'
            """
            report_data = pd.read_sql_query(query, conn)
            conn.close()
            
            if not report_data.empty:
                pendapatan = report_data.iloc[0]['pendapatan'] or 0
                beban = report_data.iloc[0]['beban'] or 0
                laba_bersih = pendapatan - beban
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Pendapatan", f"Rp {pendapatan:,.0f}")
                col2.metric("Total Beban", f"Rp {beban:,.0f}")
                
                if laba_bersih >= 0:
                    col3.metric("Laba Bersih", f"Rp {laba_bersih:,.0f}")
                else:
                    col3.metric("Rugi Bersih", f"Rp {abs(laba_bersih):,.0f}")
                
                st.write(f"Periode: {start_date} hingga {end_date}")
            else:
                st.info("Tidak ada transaksi dalam periode terpilih")
                
        with tab5:
            st.subheader("Neraca")
            
            # Filter tanggal
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Dari Tanggal", value=pd.to_datetime("2024-01-01"))
            with col2:
                end_date = st.date_input("Sampai Tanggal", value=datetime.now())
            
            conn = sqlite3.connect('finance.db')
            cursor = conn.cursor()
            
            # Query dengan filter tanggal
            cursor.execute("""
                SELECT tanggal, aset, kewajiban, ekuitas 
                FROM neraca 
                WHERE tanggal BETWEEN ? AND ?
                ORDER BY tanggal DESC
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            neraca_data = cursor.fetchall()
            conn.close()

            if neraca_data:
                # Ambil data terbaru dalam rentang tanggal
                latest_data = neraca_data[0]
                
                # Konversi nilai biner ke integer jika diperlukan
                def safe_convert(value):
                    if isinstance(value, bytes):
                        return int.from_bytes(value, byteorder='big')
                    return int(value) if value else 0
                    
                aset = safe_convert(latest_data[1])
                kewajiban = safe_convert(latest_data[2])
                ekuitas = safe_convert(latest_data[3])
                
                # Tampilkan hasil
                st.write(f"**Periode:** {latest_data[0]} hingga {end_date.strftime('%Y-%m-%d')}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Aset", f"Rp {aset:,}")
                col2.metric("Total Kewajiban", f"Rp {kewajiban:,}")
                col3.metric("Total Ekuitas", f"Rp {ekuitas:,}")
                
                # Validasi neraca
                if aset != (kewajiban + ekuitas):
                    st.error("⚠️ Neraca tidak balance! Periksa entri jurnal.")
                    st.write(f"**Selisih:** Rp {abs(aset - (kewajiban + ekuitas)):,}")
                else:
                    st.success("✓ Neraca balance!")
            
            if st.button("🔄 Generate Ulang Neraca", type="primary"):
                generate_neraca()  # Panggil fungsi generate yang sudah ada
                st.rerun()