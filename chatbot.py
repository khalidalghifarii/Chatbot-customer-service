import os
import logging
import yaml
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import collections.abc
from typing import List, Dict, Any
import json
from datetime import datetime

collections.Hashable = collections.abc.Hashable

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.conversation_patterns: Dict[str, List[str]] = {}
        self.training_stats: Dict[str, Any] = {
            'total_pairs': 0,
            'successful_pairs': 0,
            'failed_pairs': 0,
            'training_start': None,
            'training_end': None
        }

    def load_yaml_conversations(self, file_path: str) -> List[List[str]]:
        """Load and validate conversation pairs from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                yaml_content = yaml.safe_load(file)
                conversations = yaml_content.get("conversations", [])
                
                valid_conversations = []
                for conv in conversations:
                    if isinstance(conv, list) and len(conv) == 2:
                        if all(isinstance(msg, str) and msg.strip() for msg in conv):
                            valid_conversations.append(conv)
                        else:
                            logger.warning(f"Skipping invalid conversation pair in {file_path}")
                
                return valid_conversations
        except Exception as e:
            logger.error(f"Error loading YAML file {file_path}: {str(e)}")
            return []

    def extract_patterns(self, conversations: List[List[str]]) -> None:
        """Extract and store common conversation patterns."""
        for pair in conversations:
            question = pair[0].lower()
            self.conversation_patterns[question] = pair[1]

    def save_training_stats(self) -> None:
        """Save training statistics to file."""
        stats_file = 'training_stats.json'
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_stats, f, indent=2)
            logger.info(f"Training statistics saved to {stats_file}")
        except Exception as e:
            logger.error(f"Error saving training stats: {str(e)}")

def initialize_and_train() -> None:
    try:
        conversation_manager = ConversationManager()
        conversation_manager.training_stats['training_start'] = datetime.now().isoformat()

        # Initialize ChatBot dengan konfigurasi yang lebih ketat
        chatbot = ChatBot(
            "CustomChatBot",
            storage_adapter="chatterbot.storage.SQLStorageAdapter",
            logic_adapters=[
                {
                    "import_path": "chatterbot.logic.BestMatch",
                    "default_response": "Maaf, saya tidak mengerti. Silakan pilih topik bantuan berikut:\n1. Retur Barang\n2. Pembayaran\n3. Pengiriman & Tracking\n4. FAQ Umum",
                    "maximum_similarity_threshold": 0.85,  # Threshold yang lebih tinggi
                }
            ],
            database_uri="sqlite:///database/database.sqlite3",
        )
        trainer = ListTrainer(chatbot)

        # Training dari corpus customer service
        cs_base_path = os.path.join("chatterbot_corpus", "data", "indonesian", "customer_service")
        if os.path.exists(cs_base_path):
            logger.info(f"Loading customer service YAML files from {cs_base_path}")
            
            for root, _, files in os.walk(cs_base_path):
                for filename in files:
                    if filename.endswith('.yml'):
                        file_path = os.path.join(root, filename)
                        logger.info(f"Processing {filename}...")
                        
                        training_pairs = conversation_manager.load_yaml_conversations(file_path)
                        conversation_manager.training_stats['total_pairs'] += len(training_pairs)
                        
                        for pair in training_pairs:
                            try:
                                trainer.train(pair)
                                conversation_manager.training_stats['successful_pairs'] += 1
                                logger.debug(f"Successfully trained: {pair[0]} -> {pair[1]}")
                            except Exception as e:
                                conversation_manager.training_stats['failed_pairs'] += 1
                                logger.error(f"Error training pair {pair}: {str(e)}")
        else:
            logger.error(f"Data folder '{cs_base_path}' tidak ditemukan!")

        # Load custom dataset
        custom_yaml_path = os.path.join("my_corpus", "customer_support.yml")
        if os.path.exists(custom_yaml_path):
            logger.info(f"Training dengan dataset kustom: {custom_yaml_path}")
            custom_training_pairs = conversation_manager.load_yaml_conversations(custom_yaml_path)
            conversation_manager.training_stats['total_pairs'] += len(custom_training_pairs)
            
            for pair in custom_training_pairs:
                try:
                    trainer.train(pair)
                    conversation_manager.training_stats['successful_pairs'] += 1
                    conversation_manager.extract_patterns([pair])
                    logger.debug(f"Successfully trained custom pair: {pair[0]} -> {pair[1]}")
                except Exception as e:
                    conversation_manager.training_stats['failed_pairs'] += 1
                    logger.error(f"Error training custom pair {pair}: {str(e)}")

        # Simpan statistik training
        conversation_manager.training_stats['training_end'] = datetime.now().isoformat()
        conversation_manager.save_training_stats()
        
        logger.info("Training selesai!")
        logger.info(f"Total pairs: {conversation_manager.training_stats['total_pairs']}")
        logger.info(f"Successful: {conversation_manager.training_stats['successful_pairs']}")
        logger.info(f"Failed: {conversation_manager.training_stats['failed_pairs']}")

    except Exception as e:
        logger.error(f"Error fatal dalam training: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_and_train()