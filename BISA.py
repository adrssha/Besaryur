import streamlit as st
import pandas as pd
import sqlite3
import os
import json
import time

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
            menu = st.radio("Pilih Halaman", ["🏠Home", "📦Produk", "📥 Update Stok", "🛒Order Disini", "📊 Data Pesanan"], key="menu_sidebar")
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
# HALAMAN UPDATE STOK (ADMIN)
# =====================
    elif menu == "📥 Update Stok":
        st.title("📥 Update Stok Produk")

    # Baca data stok
        with open("stok.json", "r") as file:
            stok_data = json.load(file)

        nama_produk = st.selectbox("Pilih Produk", list(stok_data.keys()))

    # Ambil data stok dan harga dari produk yang dipilih
        stok_sekarang = stok_data[nama_produk]["stok"]
        harga_sekarang = stok_data[nama_produk]["harga_per_kilo"]

    # Tampilkan informasi stok
        st.write(f"Stok saat ini: {stok_sekarang} kg")
        st.write(f"Harga per kilo saat ini: Rp {harga_sekarang:,}")

        tambahan_stok = st.number_input("Tambahkan Stok (kg)", min_value=0, step=1)
        harga_baru = st.number_input("Update Harga per Kilo (opsional)", min_value=0, value=harga_sekarang, step=1000)

        if st.button("Simpan Perubahan"):
            stok_data[nama_produk]["stok"] += tambahan_stok
            stok_data[nama_produk]["harga_per_kilo"] = harga_baru

            simpan_stok(stok_data)
            st.success(f"Stok untuk {nama_produk} berhasil diperbarui!")
