from flask import Flask, request, jsonify, render_template, session
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from datetime import datetime
import logging
import uuid
import json
import os
from typing import Dict
import collections.abc

collections.Hashable = collections.abc.Hashable

# Inisialisasi Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Ganti dengan secret key yang aman

# Konfigurasi path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')

# Buat direktori jika belum ada
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'chatbot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path untuk menyimpan riwayat chat dan feedback
CHAT_HISTORY_FILE = os.path.join(DATABASE_DIR, 'chat_history.json')
FEEDBACK_FILE = os.path.join(DATABASE_DIR, 'feedback.json')

# Manajemen sesi chat
chat_sessions: Dict[str, dict] = {}

# Load chat history jika ada
if os.path.exists(CHAT_HISTORY_FILE):
    try:
        with open(CHAT_HISTORY_FILE, 'r') as f:
            chat_sessions = json.load(f)
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")

# Inisialisasi chatbot dan latih dataset
logger.info("Initializing chatbot...")
chatbot = ChatBot(
    "CustomChatBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "default_response": "Maaf, saya tidak mengerti. Bisakah Anda menjelaskan dengan cara lain?",
            "maximum_similarity_threshold": 0.90,
        }
    ],
    database_uri=f"sqlite:///{os.path.join(DATABASE_DIR, 'database.sqlite3')}",
)

trainer = ChatterBotCorpusTrainer(chatbot)
logger.info("Training chatbot with dataset...")
trainer.train(
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "payment.yml"),
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "retur.yml"),
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "shipping.yaml"),
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "conversations.yml"),
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "greetings.yml"),
    os.path.join(BASE_DIR, "chatterbot_corpus", "data", "indonesian", "trivia.yml"),
)

def get_suggested_responses(user_message: str) -> list:
    """Fungsi untuk mendapatkan suggested responses berdasarkan konteks."""
    user_message = user_message.lower()
    
    # Dictionary untuk mapping kata kunci dengan saran
    suggestions_map = {
        'retur': [
            "Bagaimana cara mengemas barang retur?",
            "Berapa lama proses retur?",
            "Biaya retur ditanggung siapa?"
        ],
        'kirim': [
            "Berapa lama estimasi pengiriman?",
            "Bagaimana cara melacak pesanan?",
            "Metode pengiriman yang tersedia?"
        ],
        'bayar': [
            "Apa saja metode pembayaran?",
            "Bagaimana cara bayar dengan transfer?",
            "Apakah tersedia cicilan?"
        ],
        'pesanan': [
            "Cara membatalkan pesanan",
            "Cara mengubah alamat",
            "Cara menghubungi CS"
        ],
        'alamat': [
            "Cara mengubah alamat pengiriman",
            "Cara menambah alamat baru",
            "Cara set alamat utama"
        ],
        'lacak': [
            "Cara melacak pesanan",
            "Cara cek status pengiriman",
            "Cara mendapatkan nomor resi"
        ],
        'cs': [
            "Cara menghubungi CS",
            "Jam operasional CS",
            "Kontak darurat CS"
        ]
    }
    
    # Cari saran berdasarkan kata kunci dalam pesan
    suggestions = []
    for keyword, responses in suggestions_map.items():
        if keyword in user_message:
            suggestions.extend(responses)
            break
    
    # Jika tidak ada kata kunci yang cocok, berikan saran umum
    if not suggestions:
        suggestions = [
            "Cara retur barang",
            "Metode pembayaran",
            "Lacak pesanan",
            "Hubungi CS"
        ]
    
    return suggestions[:3]  # Batasi maksimal 3 saran

def save_chat_state():
    """Menyimpan state chat ke file."""
    try:
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(chat_sessions, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving chat state: {str(e)}")

def save_chat_history(session_id: str, user_message: str, bot_response: str):
    """Fungsi untuk menyimpan riwayat chat."""
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'history': [],
            'start_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
    
    chat_sessions[session_id]['history'].append({
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'bot_response': bot_response
    })
    chat_sessions[session_id]['last_activity'] = datetime.now().isoformat()
    save_chat_state()

@app.route('/')
def home():
    """Menampilkan halaman utama aplikasi."""
    session['chat_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    """API endpoint untuk mendapatkan respons chatbot."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = session.get('chat_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'response': 'Pesan tidak boleh kosong'}), 400

        # Dapatkan respons dari chatbot
        bot_response = str(chatbot.get_response(user_message))
        
        # Simpan riwayat chat
        save_chat_history(session_id, user_message, bot_response)
        
        # Dapatkan suggested responses
        suggestions = get_suggested_responses(user_message)
        
        # Log interaksi
        logger.info(f"Session: {session_id} | User: {user_message} | Bot: {bot_response}")
        
        return jsonify({
            'response': bot_response,
            'suggestions': suggestions,
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Error dalam get_bot_response: {str(e)}")
        return jsonify({
            'response': 'Maaf, terjadi kesalahan. Silakan coba lagi.'
        }), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Endpoint untuk membersihkan riwayat chat."""
    try:
        session_id = session.get('chat_id')
        if session_id in chat_sessions:
            del chat_sessions[session_id]
            save_chat_state()
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Sesi tidak ditemukan'}), 404
    except Exception as e:
        logger.error(f"Error dalam clear_chat: {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan'}), 500

if __name__ == "__main__":
    app.run(debug=True)