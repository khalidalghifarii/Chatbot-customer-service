import json
import torch
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import pickle
import collections.abc

collections.Hashable = collections.abc.Hashable

# Example LSTM model class (simplified)
class LSTMChatbotModel(torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim):
        super(LSTMChatbotModel, self).__init__()
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim)
        self.lstm = torch.nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = torch.nn.Linear(hidden_dim, output_dim)
        self.softmax = torch.nn.Softmax(dim=1)
    
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        output = self.fc(lstm_out[:, -1, :])
        return self.softmax(output)

# Load pre-trained LSTM model
def load_lstm_model():
    model = load_model("notebooks/models/chatbot_model.h5")
    return model

# Load tokenizer
def load_tokenizer(tokenizer_path):
    with open(tokenizer_path, 'rb') as f:
        tokenizer = pickle.load(f)
    return tokenizer

# Tokenizer and model paths
QUESTION_TOKENIZER_PATH = "notebooks/models/tokenizers/question_tokenizer.pkl"
question_tokenizer = load_tokenizer(QUESTION_TOKENIZER_PATH)

# Predict function for LSTM
def predict_with_lstm(model, input_text, tokenizer, confidence_threshold=0.7):
    # Tokenize input_text using the loaded tokenizer
    tokens = tokenizer.texts_to_sequences([input_text])  # Adjust as per tokenizer format
    tokens = tokens[0] if tokens else [0]  # Handle empty tokenization
    input_tensor = torch.tensor(tokens).unsqueeze(0)
    with torch.no_grad():
        predictions = model(input_tensor)
        confidence, predicted_class = torch.max(predictions, dim=1)
        return predicted_class.item(), confidence.item()

# Initialize ChatterBot
chatterbot = ChatBot("FallbackBot")
trainer = ChatterBotCorpusTrainer(chatterbot)
trainer.train("chatterbot.corpus.indonesian")  # Train on Indonesian dataset

# Fallback function
def get_fallback_response(input_text):
    response = chatterbot.get_response(input_text)
    return str(response)

# Integrated response function
def get_combined_response(input_text, lstm_model, tokenizer):
    predicted_class, confidence = predict_with_lstm(lstm_model, input_text, tokenizer)
    if confidence >= 0.7:  # Confidence threshold
        if predicted_class == 0:  # Example class mapping
            return "LSTM Response: Informasi kelas 0"
        elif predicted_class == 1:
            return "LSTM Response: Informasi kelas 1"
    else:
        return f"ChatterBot Fallback: {get_fallback_response(input_text)}"

# Flask app integration
app = Flask(__name__)
lstm_model = load_lstm_model()

@app.route('/get_response', methods=['POST'])
def get_response():
    data = json.loads(request.data)
    input_text = data.get("message", "")
    if not input_text:
        return jsonify({"response": "Input kosong!"})
    
    response = get_combined_response(input_text, lstm_model, tokenizer=question_tokenizer)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)