#!/usr/bin/env python3
"""
Complete WhatsApp Auto-Reply System - With All Advanced Features
- Sentiment matching
- Contact-specific models
- Media handling (images/videos)
- Context & topic analysis
- Question detection
- Multi-language support
- Message timing learning
"""

import sys
import json
import re
import time
from pathlib import Path
from advanced_whatsapp import AdvancedWhatsAppBot
from advanced_engine import AdvancedMessageEngine
from contact_models import ContactModelManager
from sentiment_analyzer import SentimentAnalyzer

class MessageParser:
    @staticmethod
    def parse_whatsapp_export(file_path: str):
        """Parse WhatsApp exported chat"""
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    match = re.search(r']: (.+)$', line)
                    if match:
                        msg = match.group(1).strip()
                        if msg and not msg.startswith('<'):
                            messages.append(msg)
        except FileNotFoundError:
            print(f"[-] File not found: {file_path}")
        return messages
    
    @staticmethod
    def parse_json_messages(file_path: str):
        """Parse JSON messages"""
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            messages.append(item)
                        elif isinstance(item, dict) and 'text' in item:
                            messages.append(item['text'])
        except Exception as e:
            print(f"[-] Error: {e}")
        return messages
    
    @staticmethod
    def clean_messages(messages):
        """Clean messages"""
        cleaned = []
        for msg in messages:
            msg = re.sub(r'http\S+|www\S+', '', msg)
            msg = ' '.join(msg.split())
            if 2 < len(msg) < 500:
                cleaned.append(msg)
        return cleaned

def main():
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║     WhatsApp Auto-Reply System - Advanced Edition               ║
║   Learn your style, reply like you, understand context          ║
╚════════════════════════════════════════════════════════════════╝

Usage:
  python3 main_advanced.py train <file>        - Train global + contact models
  python3 main_advanced.py test                 - Test generation quality
  python3 main_advanced.py whatsapp            - Start advanced monitoring
  python3 main_advanced.py stats               - Show advanced statistics
  python3 main_advanced.py contact-stats       - Contact-specific stats

Examples:
  python3 main_advanced.py train messages.json
  python3 main_advanced.py whatsapp --no-approval
  python3 main_advanced.py contact-stats

Features:
  ✓ Sentiment Analysis - Matches emotional tone
  ✓ Contact Models - Different style per contact
  ✓ Media Handling - Understands images/videos
  ✓ Context Aware - Analyzes conversation flow
  ✓ Question Detection - Handles questions properly
  ✓ Language Detection - Matches language used
  ✓ Message Timing - Learns when you reply
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "train":
        if len(sys.argv) < 3:
            print("[-] Specify input file (JSON or WhatsApp export)")
            sys.exit(1)
        
        input_file = sys.argv[2]
        print(f"[*] Loading messages from {input_file}...")
        
        # Parse
        messages = MessageParser.parse_whatsapp_export(input_file)
        if not messages:
            messages = MessageParser.parse_json_messages(input_file)
        
        if not messages:
            print("[-] No messages found")
            sys.exit(1)
        
        # Clean
        messages = MessageParser.clean_messages(messages)
        print(f"[+] Loaded {len(messages)} messages")
        
        # Train global model
        print("[*] Training advanced global model...")
        engine = AdvancedMessageEngine()
        engine.train(messages)
        engine.save("message_model.json")
        print("[+] Global model saved")
        
        # Train contact-specific models (split by sender if available)
        # For now, create a default model for all contacts
        manager = ContactModelManager()
        manager.train_contact_model("General", messages)
        print("[+] Contact model saved")
        
        # Test
        print("\n[*] Test generation (5 samples):")
        for i in range(5):
            reply, conf = engine.generate_multiple(count=5)
            status = "✓ GOOD" if conf >= 0.85 else "⊘ WEAK"
            print(f"  {i+1}. '{reply}' [{conf*100:.0f}%] {status}")
        
        # Analyze sentiment in training data
        print("\n[*] Analyzing training data sentiment...")
        analyzer = SentimentAnalyzer()
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
        for msg in messages[:20]:
            _, emotion = analyzer.analyze_sentiment(msg)
            sentiments[emotion] += 1
        print(f"  Sentiment distribution: {sentiments}")
        
        print(f"\n[+] Ready! Run: python3 main_advanced.py whatsapp")
    
    elif cmd == "test":
        if not Path("message_model.json").exists():
            print("[-] Model not found. Train first: python3 main_advanced.py train messages.json")
            sys.exit(1)
        
        print("[*] Loading model...")
        engine = AdvancedMessageEngine()
        engine.load("message_model.json")
        
        print("\n[*] Generating 10 test replies with sentiment analysis:\n")
        
        analyzer = SentimentAnalyzer()
        
        for i in range(10):
            reply, conf = engine.generate_multiple(count=5)
            polarity, emotion = analyzer.analyze_sentiment(reply)
            status = "✓" if conf >= 0.85 else "⊘"
            
            print(f"{i+1:2}. '{reply}'")
            print(f"     [{conf*100:5.1f}% conf] [{emotion:8s}] [polarity: {polarity:+.2f}] {status}")
    
    elif cmd == "whatsapp":
        if not Path("message_model.json").exists():
            print("[-] Model not found. Train first: python3 main_advanced.py train messages.json")
            sys.exit(1)
        
        no_approval = "--no-approval" in sys.argv
        headless = "--headless" in sys.argv
        
        print("""
╔════════════════════════════════════════════════════════════════╗
║     Advanced WhatsApp Auto-Reply Monitoring                    ║
╚════════════════════════════════════════════════════════════════╝

Features:
  • Sentiment Matching - Replies match emotional tone
  • Contact Models - Different style per contact
  • Media Detection - Understands images/videos
  • Context Analysis - Analyzes conversation topic
  • Question Handling - Detects and answers questions
  • Language Matching - Replies in detected language
  • Timing Analysis - Learns your reply speed
        """)
        
        if no_approval:
            print("[!] WARNING: Running without approval!")
            print("[!] Messages will be sent automatically!")
            confirm = input("[?] Continue? (type 'yes' to confirm): ")
            if confirm != "yes":
                print("[-] Cancelled")
                sys.exit(0)
        
        print("[*] Loading model...")
        engine = AdvancedMessageEngine()
        engine.load("message_model.json")
        
        print("[*] Initializing advanced WhatsApp bot...")
        bot = AdvancedWhatsAppBot(headless=headless, approval_required=not no_approval)
        
        if not bot.setup_driver():
            print("[-] Failed to start browser")
            sys.exit(1)
        
        if not bot.load_whatsapp():
            print("[-] Failed to load WhatsApp Web")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("Advanced Monitoring Started. Press Ctrl+C to stop.")
        print("="*60 + "\n")
        
        bot.monitor_and_reply_advanced(check_interval=15)
    
    elif cmd == "stats":
        bot = AdvancedWhatsAppBot()
        bot.get_advanced_stats()
    
    elif cmd == "contact-stats":
        manager = ContactModelManager()
        
        print("\n╔════════════════════════════════════════╗")
        print("║   Contact-Specific Statistics          ║")
        print("╚════════════════════════════════════════╝\n")
        
        contacts = manager.list_trained_contacts()
        
        if not contacts:
            print("[-] No trained contacts found")
            print("[*] Train models first: python3 main_advanced.py train messages.json")
            sys.exit(1)
        
        for contact in contacts:
            stats = manager.get_contact_stats(contact)
            print(f"Contact: {contact}")
            print(f"  Messages trained: {stats['messages_trained']}")
            print(f"  Recent history: {stats['recent_history_size']} messages")
            print(f"  Avg message length: {stats['avg_msg_length']:.1f} words")
            print(f"  Model exists: {stats['model_exists']}")
            print()
    
    else:
        print(f"[-] Unknown command: {cmd}")
        print("[*] Use --help for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main()
