#!/usr/bin/env python3
"""
Complete Auto-Reply System
Train from your messages, generate replies in your style
"""

import json
import time
import random
from collections import defaultdict
from pathlib import Path
import sys
import re

class MessageEngine:
    def __init__(self):
        self.markov_chain = defaultdict(lambda: defaultdict(int))
        self.word_freq = defaultdict(int)
        self.vocabulary = []
        
    def tokenize(self, text):
        """Break message into words"""
        return text.lower().split()
    
    def train(self, messages):
        """Learn from message history"""
        for msg in messages:
            tokens = self.tokenize(msg)
            
            for token in tokens:
                self.word_freq[token] += 1
            
            for i in range(len(tokens) - 1):
                self.markov_chain[tokens[i]][tokens[i + 1]] += 1
        
        self.vocabulary = list(self.word_freq.keys())
    
    def generate_reply(self, max_length=15):
        """Generate a reply matching your style"""
        if not self.vocabulary:
            return "hey"
        
        result = []
        current_word = random.choice(self.vocabulary)
        result.append(current_word)
        
        for _ in range(max_length):
            if current_word not in self.markov_chain or not self.markov_chain[current_word]:
                break
            
            next_words = self.markov_chain[current_word]
            total = sum(next_words.values())
            
            if total == 0:
                break
            
            rand_val = random.randint(0, total - 1)
            accumulated = 0
            
            for word, count in next_words.items():
                accumulated += count
                if rand_val <= accumulated:
                    current_word = word
                    result.append(word)
                    break
        
        return ' '.join(result)
    
    def calculate_confidence(self, generated_msg):
        """Rate how well the message matches your style (0-1)"""
        tokens = self.tokenize(generated_msg)
        if not tokens:
            return 0.0
        
        matches = sum(1 for token in tokens if token in self.word_freq)
        return matches / len(tokens)
    
    def save(self, filename):
        """Save trained model"""
        data = {
            'vocabulary': self.vocabulary,
            'word_freq': dict(self.word_freq),
            'markov_chain': {k: dict(v) for k, v in self.markov_chain.items()}
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filename):
        """Load trained model"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.vocabulary = data['vocabulary']
            self.word_freq = defaultdict(int, data['word_freq'])
            self.markov_chain = defaultdict(lambda: defaultdict(int))
            for word, nexts in data['markov_chain'].items():
                self.markov_chain[word] = defaultdict(int, nexts)
            return True
        except FileNotFoundError:
            return False

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
        """Parse JSON message file"""
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
            print(f"[-] Error parsing JSON: {e}")
        return messages
    
    @staticmethod
    def clean_messages(messages):
        """Clean and filter messages"""
        cleaned = []
        for msg in messages:
            msg = re.sub(r'http\S+|www\S+', '', msg)
            msg = ' '.join(msg.split())
            if 3 < len(msg) < 500:
                cleaned.append(msg)
        return cleaned

class AutoReplyDaemon:
    def __init__(self, model_file="message_model.json", threshold=0.85):
        self.model_file = model_file
        self.threshold = threshold
        self.engine = MessageEngine()
        self.log_file = "auto_reply_log.json"
        
        if Path(model_file).exists():
            self.engine.load(model_file)
    
    def log_reply(self, contact, incoming, generated, confidence, sent):
        """Log decision"""
        logs = []
        if Path(self.log_file).exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "contact": contact,
            "incoming": incoming,
            "generated": generated,
            "confidence": round(confidence, 2),
            "sent": sent
        })
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def run_daemon(self, scans=10):
        """Run monitoring daemon"""
        print(f"[*] Starting daemon (threshold: {self.threshold*100:.0f}%)")
        print(f"[*] Running {scans} scan(s)...\n")
        
        for i in range(scans):
            reply = self.engine.generate_reply()
            confidence = self.engine.calculate_confidence(reply)
            will_send = confidence >= self.threshold
            
            status = "✓ SEND" if will_send else "⊘ WAIT"
            print(f"Scan {i+1}: '{reply}' [{confidence*100:.0f}%] {status}")
            
            self.log_reply("contact", "incoming_msg", reply, confidence, will_send)
            time.sleep(1)
    
    def show_stats(self):
        """Show statistics"""
        if not Path(self.log_file).exists():
            print("[-] No logs found")
            return
        
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        sent = sum(1 for l in logs if l['sent'])
        avg_conf = sum(l['confidence'] for l in logs) / total if total > 0 else 0
        
        print(f"\n=== Statistics ===")
        print(f"Total scans: {total}")
        print(f"Replies sent: {sent}")
        print(f"Avg confidence: {avg_conf*100:.0f}%")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 auto_reply.py train <input_file>  - Train from messages")
        print("  python3 auto_reply.py run [scans]         - Run daemon")
        print("  python3 auto_reply.py stats               - Show statistics")
        print("\nExamples:")
        print("  python3 auto_reply.py train chat.txt")
        print("  python3 auto_reply.py run 5")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "train":
        if len(sys.argv) < 3:
            print("[-] Specify input file (WhatsApp export or JSON)")
            sys.exit(1)
        
        input_file = sys.argv[2]
        print(f"[*] Loading messages from {input_file}...")
        
        # Try WhatsApp format first
        messages = MessageParser.parse_whatsapp_export(input_file)
        if not messages:
            messages = MessageParser.parse_json_messages(input_file)
        
        if not messages:
            print("[-] No messages found")
            sys.exit(1)
        
        messages = MessageParser.clean_messages(messages)
        print(f"[+] Loaded {len(messages)} messages")
        
        engine = MessageEngine()
        engine.train(messages)
        engine.save("message_model.json")
        print(f"[+] Model saved")
        
        # Test generation
        print("\n[*] Test generation:")
        for i in range(3):
            reply = engine.generate_reply()
            conf = engine.calculate_confidence(reply)
            print(f"  {i+1}. '{reply}' [{conf*100:.0f}%]")
    
    elif cmd == "run":
        scans = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        daemon = AutoReplyDaemon()
        daemon.run_daemon(scans)
    
    elif cmd == "stats":
        daemon = AutoReplyDaemon()
        daemon.show_stats()
    
    else:
        print(f"[-] Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
