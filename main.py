#!/usr/bin/env python3
"""
Main CLI - Train and run everything
"""

import sys
import json
import re
from pathlib import Path
from advanced_engine import AdvancedMessageEngine

class MessageParser:
    @staticmethod
    def parse_whatsapp_export(file_path: str):
        """Parse WhatsApp exported chat"""
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # WhatsApp format: [HH:MM, DD/MM/YYYY] Name: Message
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
╔════════════════════════════════════════════╗
║   WhatsApp Auto-Reply System                ║
║   Learn your style. Reply automatically.    ║
╚════════════════════════════════════════════╝

Usage:
  python3 main.py train <file>      - Train from messages
  python3 main.py test              - Test generation
  python3 main.py whatsapp          - Start WhatsApp bot
  python3 main.py stats             - Show statistics

Examples:
  python3 main.py train messages.json
  python3 main.py train whatsapp_export.txt
  python3 main.py whatsapp --no-approval

Options:
  --no-approval   Don't ask before sending (risky!)
  --headless      Run browser in headless mode
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
        
        # Train
        print("[*] Training advanced engine...")
        engine = AdvancedMessageEngine()
        engine.train(messages)
        engine.save("message_model.json")
        print("[+] Model saved: message_model.json")
        
        # Test
        print("\n[*] Test generation (5 samples):")
        for i in range(5):
            reply, conf = engine.generate_multiple(count=5)
            status = "✓ GOOD" if conf >= 0.85 else "⊘ WEAK"
            print(f"  {i+1}. '{reply}' [{conf*100:.0f}%] {status}")
        
        print(f"\n[+] Ready! Run: python3 main.py whatsapp")
    
    elif cmd == "test":
        if not Path("message_model.json").exists():
            print("[-] Model not found. Train first: python3 main.py train messages.json")
            sys.exit(1)
        
        print("[*] Loading model...")
        engine = AdvancedMessageEngine()
        engine.load("message_model.json")
        
        print("\n[*] Generating 10 test replies:\n")
        for i in range(10):
            reply, conf = engine.generate_multiple(count=5)
            status = "✓" if conf >= 0.85 else "⊘"
            print(f"{i+1:2}. '{reply}' [{conf*100:5.1f}%] {status}")
    
    elif cmd == "whatsapp":
        if not Path("message_model.json").exists():
            print("[-] Model not found. Train first: python3 main.py train messages.json")
            sys.exit(1)
        
        from whatsapp_integration import WhatsAppBot
        
        no_approval = "--no-approval" in sys.argv
        headless = "--headless" in sys.argv
        
        print("""
╔════════════════════════════════════════════╗
║   WhatsApp Auto-Reply Monitoring           ║
╚════════════════════════════════════════════╝
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
        
        print("[*] Initializing WhatsApp bot...")
        bot = WhatsAppBot(headless=headless, approval_required=not no_approval)
        
        if not bot.setup_driver():
            print("[-] Failed to start browser")
            sys.exit(1)
        
        if not bot.load_whatsapp():
            print("[-] Failed to load WhatsApp Web")
            sys.exit(1)
        
        print("\n" + "="*45)
        print("Monitoring started. Press Ctrl+C to stop.")
        print("="*45 + "\n")
        
        bot.monitor_and_reply(engine, check_interval=15)
    
    elif cmd == "stats":
        from whatsapp_integration import WhatsAppBot
        
        bot = WhatsAppBot()
        bot.get_stats()
    
    else:
        print(f"[-] Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
