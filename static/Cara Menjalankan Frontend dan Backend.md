**Cara Menjalankan Frontend dan Backend**

Untuk menjalankan aplikasi ini dengan benar, Anda perlu menjalankan dua server secara bersamaan di dua terminal yang berbeda.

**Terminal 1: Menjalankan Server Backend (ADK Agent)**

1. Buka terminal baru.

2. Arahkan ke direktori root proyek Anda (`adk-healthcare/`).

3. Aktifkan virtual environment Anda (jika ada).

4. Jalankan perintah `adk web`. Server ini akan berjalan di `http://localhost:8000.`

```
cd adk-healthcare

source .venv/bin/activate  (jika menggunakan venv)
adk web
```

**Terminal 2: Menjalankan Server Frontend (Halaman Web)**

1. Buka terminal kedua (biarkan terminal pertama tetap berjalan).

2. Arahkan ke direktori root proyek Anda (adk-healthcare/).

3. Jalankan server web sederhana bawaan Python. Server ini akan berjalan di http://localhost:8080.

```
cd adk-healthcare
python3 -m http.server 8080
```

(Gunakan python jika python3 tidak ditemukan)

**Cara Mengakses Aplikasi**

- Buka browser Anda dan kunjungi `http://localhost:8080/static/index.html.`

- `http://localhost:8080/static/chatbot.html`

- Anda akan melihat halaman web rumah sakit. Chat popup di pojok kanan bawah akan berkomunikasi dengan server ADK yang berjalan di port 8000.