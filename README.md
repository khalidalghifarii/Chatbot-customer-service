# Chatbot Customer Service

Chatbot untuk layanan pelanggan menggunakan ChatterBot dan Flask.

## Fitur

- Respon otomatis untuk pertanyaan pelanggan
- Penanganan FAQ umum
- Interface web yang responsif
- Mendukung beberapa kategori layanan:
  - Retur Barang
  - Pembayaran
  - Pengiriman
  - FAQ Umum

## Teknologi

- Python 3.8+
- Flask
- ChatterBot
- HTML/CSS/JavaScript

## Instalasi

1. Clone repository

```bash
git clone https://github.com/khalidalghifarii/Chatbot-customer-service.git
cd Chatbot-customer-service
```

2. Buat virtual environment

```bash
python -m venv chatbot_env
source chatbot_env/bin/activate  # Linux/Mac
# atau
chatbot_env\Scripts\activate  # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi

```bash
python app.py
```

5. Buka browser dan akses `http://localhost:5000`

## Struktur Project

```
chatbot_project/
├── app.py                     # File utama aplikasi Flask
├── chatbot.py                 # Logic chatbot dan training
├── requirements.txt           # Dependensi project
├── README.md                  # Dokumentasi
├── templates/                 # Template HTML
│   └── index.html
├── static/                    # Asset statis
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
└── my_corpus/                 # Data training
    └── customer_support.yml
```

## Penggunaan

1. Buka aplikasi di browser
2. Pilih kategori bantuan atau ketik pertanyaan
3. Chatbot akan memberikan respons sesuai dengan pertanyaan
4. Gunakan quick replies untuk pertanyaan lanjutan

## Kontribusi

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Requirements

Buat file requirements.txt dengan menjalankan:

```bash
pip freeze > requirements.txt
```

## License

[MIT License](https://choosealicense.com/licenses/mit/)
