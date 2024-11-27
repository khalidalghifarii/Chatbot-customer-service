# Chatbot Customer Service

Chatbot layanan pelanggan berbasis Flask dan ChatterBot yang mendukung beberapa kategori layanan, dilengkapi dengan fitur prediksi berbasis Machine Learning.

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
- Matplotlib & Seaborn (untuk evaluasi model)
- NLTK (untuk preprocessing teks)

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

5. Buka browser dan akses `http://127.0.0.1:5000`

## Struktur Project

```
chatbot_project/
├── app.py                     # File utama aplikasi Flask
├── chatbot.py                 # Logic chatbot dan training
├── chatbot_updated.py         # Versi baru chatbot dengan fallback logic
├── requirements.txt           # Dependensi project
├── README.md                  # Dokumentasi
├── templates/                 # Template HTML
│   └── index.html
├── static/                    # Asset statis
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
├── chatterbot_corpus/         # Dataset YAML untuk chatbot
│   └── data/indonesian/
│       ├── payment.yml
│       ├── retur.yml
│       ├── shipping.yaml
│       ├── conversations.yml
│       ├── greetings.yml
│       └── trivia.yml
├── notebooks/                 # Notebook Jupyter untuk pelatihan model
│   ├── 1_data_preparation.ipynb
│   ├── 2_model_training.ipynb
│   ├── 3_model_evaluation.ipynb
│   └── 3_model_evaluation_updated.ipynb
├── model/                     # Direktori untuk model dan tokenizer
│   ├── chatbot_model.h5
│   └── tokenizers/
│       ├── question_tokenizer.pkl
│       └── answer_tokenizer.pkl
└── logs/                      # Direktori untuk log aplikasi
    └── chatbot.log
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
