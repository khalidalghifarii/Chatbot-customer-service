// Konfigurasi kategori FAQ
const FAQ_TOPICS = {
    'retur': {
        title: 'Retur Barang',
        questions: [
            'Bagaimana cara mengemas barang retur?',
            'Berapa lama proses retur?',
            'Biaya retur ditanggung siapa?'
        ]
    },
    'payment': {
        title: 'Pembayaran',
        questions: [
            'Apa saja metode pembayaran?',
            'Bagaimana cara bayar dengan transfer?',
            'Apakah tersedia cicilan?'
        ]
    },
    'shipping': {
        title: 'Pengiriman',
        questions: [
            'Bagaimana cara lacak pesanan?',
            'Berapa lama waktu pengiriman?',
            'Wilayah pengiriman COD'
        ]
    },
    'faq': {
        title: 'FAQ Umum',
        questions: [
            'Cara membatalkan pesanan',
            'Cara mengubah alamat',
            'Cara menghubungi CS'
        ]
    }
};

// State Management
let sessionId = null;
let lastMessageTime = new Date();

// Inisialisasi
function initializeChat() {
    sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
        sessionId = 'session_' + Date.now();
        localStorage.setItem('chatSessionId', sessionId);
    }

    // Event listener untuk tombol FAQ
    document.querySelectorAll('.faq-button').forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            showCategoryQuestions(category);
        });
    });
}

// Utility Functions
function getTimestamp() {
    return new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'block';
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'none';
}

// Message Display Functions
function addMessage(message, isUser, suggestions = []) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.textContent = message;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = getTimestamp();
    
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(timestamp);

    if (!isUser) {
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'feedback-container';
        feedbackContainer.innerHTML = `
            <button class="feedback-button" onclick="submitFeedback('${message}', true)">👍</button>
            <button class="feedback-button" onclick="submitFeedback('${message}', false)">👎</button>
        `;
        messageDiv.appendChild(feedbackContainer);

        if (suggestions.length > 0) {
            displaySuggestions(suggestions);
        }
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showCategoryQuestions(category) {
    const topic = FAQ_TOPICS[category];
    if (!topic) return;

    const questionsContainer = document.createElement('div');
    questionsContainer.className = 'quick-reply-container';
    
    topic.questions.forEach(question => {
        const button = document.createElement('button');
        button.className = 'quick-reply';
        button.textContent = question;
        button.onclick = () => sendMessage(question);
        questionsContainer.appendChild(button);
    });
    
    const chatBox = document.getElementById('chat-box');
    chatBox.appendChild(questionsContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestions-container');
    container.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.onclick = () => {
            document.getElementById('user-input').value = suggestion;
            sendMessage();
        };
        container.appendChild(chip);
    });
}

// API Interaction Functions
async function submitFeedback(message, isPositive) {
    try {
        await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                is_positive: isPositive
            })
        });
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
}

async function sendMessage(predefinedMessage = null) {
    const input = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = predefinedMessage || input.value.trim();
    
    if (message) {
        input.disabled = true;
        sendButton.disabled = true;
        
        addMessage(message, true);
        input.value = '';
        showTypingIndicator();
        
        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            setTimeout(() => {
                hideTypingIndicator();
                addMessage(data.response, false, data.suggestions || []);
            }, 500 + Math.random() * 1000);
        } catch (error) {
            hideTypingIndicator();
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = 'Maaf, terjadi kesalahan. Silakan coba lagi.';
            document.getElementById('chat-box').appendChild(errorDiv);
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        }
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById('clear-chat').addEventListener('click', async function() {
        if (confirm('Apakah Anda yakin ingin menghapus semua chat?')) {
            try {
                await fetch('/clear_chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ session_id: sessionId })
                });
                
                document.getElementById('chat-box').innerHTML = `
                    <div class="message bot-message">
                        Halo! Saya asisten layanan pelanggan. Ada yang bisa saya bantu?
                        <div class="timestamp">${getTimestamp()}</div>
                    </div>
                `;
                document.getElementById('suggestions-container').innerHTML = '';
            } catch (error) {
                console.error('Error clearing chat:', error);
            }
        }
    });
});