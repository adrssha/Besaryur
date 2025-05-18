import streamlit as st
import pandas as pd
from datetime import date
import os
import json
import time 

# =========================
# FUNGSI UNTUK MENGELOLA DATA USER & STOK
# =========================

# Fungsi untuk memuat data user dari file users.json
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} 

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

# Data awal pengguna default (jika file belum dibuat)
users = { "admin": {"password": "admin123", "role": "admin"},"buyer1": {"password": "buyer123", "role": "buyer"}}

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
            menu = st.radio("Pilih Halaman", ["🏠Home", "📦Produk", "📥 Update Stok", "🛒Order Disini", "📊 Data"], key="menu_sidebar")
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
        st.title("🌿 BERSARYUR")
        st.subheader("Halo pecinta selada! Selamat datang di website kami 💚")
        st.markdown("BESARYUR hadir di Semarang khususnya daerah Gunung pati dan sekitarnya, kami memiliki tujuan untuk dapat memenuhi kebutuhan selada segar anda 🥬✨")

        # Tampilan Judul Section
        st.title("Layanan Terbaik Kami")
        col1, col2, col3 = st.columns(3)

        # Menampilkan 3 layanan unggulan
        with col1:
            st.markdown("#### 🕰️ 24 Jam")
            st.caption("Pemesanan dan Pengiriman 24 jam. pagi, siang, dan malam.")

        with col2:
            st.markdown("#### 🚚 Pengiriman Cepat")
            st.caption("Pesanan segera dikirim setelah produk dipesan.")

        with col3:
            st.markdown("#### ✅ Quality Control")
            st.caption("Quality control barang yang ketat.")

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
                            st.image(image_paths[i + j], use_column_width=True)
# =====================
# HALAMAN PRODUK
# ===================== 
    elif menu == "📦Produk":
        stok_data = load_stok() # Load data stok dari file
        nama_produk = "Selada"  # Nama produk yang dijual
        stok_info = stok_data.get(nama_produk, {"stok": 0, "harga_per_kilo": 15000})
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
        if "page" not in st.session_state:
            st.session_state["page"] = "order"

    # 1. FORMULIR ORDER
        if st.session_state["page"] == "order":
            st.title("📝 Form Pemesanan")
            with open("stok.json", "r") as file:
                stok_data = json.load(file)
    
    # Form input data pelanggan
            nama = st.text_input("Nama Pemesan")
            nomor_telepon = st.text_input("Nomor Telepon")
            alamat = st.text_area("Alamat Pengiriman")
            metode = st.selectbox("Metode Pembayaran", ["Transfer Bank", "QRIS"], key="metode_pembayaran_order")
            catatan = st.text_area("Catatan Tambahan (opsional)")
            tanggal_kirim = st.date_input("Tanggal Pengiriman")
            waktu_kirim = st.time_input("Waktu Pengiriman")

            # Pastikan produk sudah dipilih sebelumnya
            if "produk" not in st.session_state:
                st.error("Silakan pilih produk dan jumlah pesanan terlebih dahulu.")
                st.stop()

            # Menampilkan informasi pesanan dari session
            produk = st.session_state["produk"]
            jumlah_default = produk["jumlah"]
            total_default = produk["total"]
            
            jumlah = st.number_input("Jumlah Pesanan(kg)", value=jumlah_default, min_value=0, step=1, disabled=True)
            total_harga = st.text_input("Total Harga (Rp)", value=f"Rp {total_default:,}", disabled=True)

            # Menyimpan pesanan ke file Excel
            if 'data_pesanan' not in st.session_state:
                if os.path.exists("data_pesanan.xlsx"):
                    st.session_state['data_pesanan'] = pd.read_excel("data_pesanan.xlsx")
                else:
                    st.session_state['data_pesanan'] = pd.DataFrame(columns=["Nama", "Nomor Telepon", "Alamat", "Jumlah", "Metode", "Total", "Tanggal Pengiriman", "Waktu Pengiriman", "Catatan", "Status"])
                    
            data_pesanan = st.session_state['data_pesanan']

            if st.button("Kirim Pesanan"):
                if nama and nomor_telepon and alamat and jumlah > 0 and metode:
                    # Buat data pesanan baru
                    data_baru = pd.DataFrame([{
                        "Nama": nama,
                        "Nomor Telepon": nomor_telepon,
                        "Alamat": alamat,
                        "Jumlah": jumlah,
                        "Metode": metode,
                        "Total": total_default,
                        "Tanggal Pengiriman": tanggal_kirim.strftime("%Y-%m-%d"),
                        "Waktu Pengiriman": waktu_kirim.strftime("%H:%M"),
                        "Catatan": catatan,
                        "Status": "Diproses"
                    }])
                    
                    st.session_state.pesanan_dikirim = True
                    st.session_state.metode_pembayaran = metode
                    st.session_state.jumlah_pembayaran = total_default
                    st.session_state.page = "pembayaran"

                    # Simpan ke Excel
                    if os.path.exists("data_pesanan.xlsx"):
                        existing_data = pd.read_excel("data_pesanan.xlsx")
                        updated_data = pd.concat([existing_data, data_baru], ignore_index=True)
                    else:
                        updated_data = data_baru
                    updated_data.to_excel("data_pesanan.xlsx", index=False)

                    # Simpan ke session_state agar bisa ditampilkan di halaman Data
                    st.session_state["data_pesanan"] = updated_data
                    data_pesanan = pd.concat([data_pesanan, data_baru], ignore_index=True)
                    st.session_state['data_pesanan'] = data_pesanan
                try:
                    data_pesanan.to_excel("data_pesanan.xlsx", index=False)
                except PermissionError:
                    st.error("⚠️ Gagal menyimpan ke Excel. Pastikan file tidak sedang dibuka!")
                data_pesanan.to_excel("data_pesanan.xlsx", index=False)

                # Kurangi stok
                with open("stok.json", "r") as file:
                    stok_data = json.load(file)
                if produk["nama"] in stok_data:
                    stok_data[produk["nama"]]["stok"] -= jumlah
                    simpan_stok(stok_data)
                    st.success("Pesanan berhasil dikirim! Terima kasih 😊")
                    
                    st.session_state.page = "pembayaran"
                    st.rerun()
            else:
                st.error("❗ Semua kolom wajib diisi dengan benar ❗")

        # 2. HALAMAN PEMBAYARAN
        elif st.session_state.get("page") == "pembayaran":
            st.subheader("Konfirmasi Pembayaran")
            st.write("Total yang harus dibayar:")
            st.success(F"Rp {st.session_state.jumlah_pembayaran:,.0f}")
            
            # Upload bukti pembayaran
            bukti = st.file_uploader("Upload Bukti Pembayaran", type=["jpg", "jpeg", "png", "pdf"], key="file_upload_bukti")

            if st.session_state.metode_pembayaran == "QRIS":
                st.image("image/qris.jpg", caption="Silakan scan QR untuk membayar")
            elif st.session_state.metode_pembayaran == "Transfer Bank":
                st.write("Bank: Mandiri")
                st.write("No. Rek: 1234567890")
                st.write("Nama: PT BESAYUR")
                st.image("image/bank.png", caption="Transfer ke rekening berikut:")
                # Tampilkan preview jika gambar
                if bukti is not None and bukti.type.startswith("image/"):
                    st.image(bukti, caption="Bukti Pembayaran", use_column_width=True)
                    st.session_state["bukti_pembayaran"] = True
                elif bukti is not None and bukti.type == "application/pdf":
                    st.write("📄 File PDF berhasil diunggah.") 
                st.markdown("---")
                st.image("image/qr_wa.jpg", caption="Scan untuk konfirmasi via WhatsApp", use_column_width=False)
                st.info("📱 Silakan konfirmasi admin untuk mengetahui status pesanan.")           
            if st.button("Kembali ke Form"):
                if "bukti_pembayaran" not in st.session_state:
                    st.error("❗ Silakan upload bukti pembayaran terlebih dahulu sebelum melanjutkan.")
                else:
                    st.session_state.page = "order"
                    st.rerun()

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


# =====================
# HALAMAN DATA KEUANGAN (ADMIN)
# =====================
    elif menu == "📊 Data":
                # Nama file data
        FILE = "data_pengeluaran.xlsx"

        # Fungsi untuk menyimpan data
        def save_data(df):
            df.to_excel(FILE, index=False, engine="openpyxl")

        # Membuat file jika belum ada
        if not os.path.exists(FILE):
            df_init = pd.DataFrame(columns=["Tanggal", "Jenis", "Nominal", "Keterangan"])
            df_init.to_excel(FILE, index=False, engine="openpyxl")

        # Membaca data
        df = pd.read_excel(FILE, engine="openpyxl")
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])

        # Halaman Data
        st.title("📊 Data Keuangan")

        # Form input data
        st.subheader("➕ Tambah Transaksi")
        with st.form("form_transaksi"):
            tgl = st.date_input("Tanggal", value=date.today())
            jenis = st.radio("Jenis", ["Pemasukan", "Pengeluaran"], horizontal=True)
            nominal = st.number_input("Nominal", min_value=0)
            ket = st.text_input("Keterangan", placeholder="Misal: Penjualan, Beli bahan...")
            submit = st.form_submit_button("Simpan")

            if submit:
                new_row = pd.DataFrame([[tgl, jenis, nominal, ket]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                df["Tanggal"] = pd.to_datetime(df["Tanggal"]) 
                st.success("✅ Transaksi berhasil disimpan.")
                st.query_params.update({"refresh": str(pd.Timestamp.now())})

        # Menampilkan dua tabel: pemasukan dan pengeluaran
        st.subheader("📋 Data Transaksi")
        col1, col2 = st.columns(2)

        with col1:
            st.write("### 📥 Data Pemasukan")
            pemasukan_df = df[df["Jenis"] == "Pemasukan"]
            st.dataframe(pemasukan_df, use_container_width=True)

        with col2:
            st.write("### 📤 Data Pengeluaran")
            pengeluaran_df = df[df["Jenis"] == "Pengeluaran"]
            df["Tanggal"] = pd.to_datetime(df["Tanggal"]) 
            st.dataframe(pengeluaran_df, use_container_width=True)

        