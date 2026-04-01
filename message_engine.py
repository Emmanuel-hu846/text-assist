#!/usr/bin/env python3
"""
Message Auto-Reply Engine
Learns your texting style and generates replies using Markov chains
"""

import json
import random
from collections import defaultdict
from pathlib import Path

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
            
            # Track word frequency
            for token in tokens:
                self.word_freq[token] += 1
            
            # Build Markov chain (word -> next word frequency)
            for i in range(len(tokens) - 1):
                self.markov_chain[tokens[i]][tokens[i + 1]] += 1
        
        self.vocabulary = list(self.word_freq.keys())
        print(f"[*] Trained on {len(messages)} messages")
        print(f"[*] Vocabulary size: {len(self.vocabulary)}")
    
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
        print(f"[+] Model saved to {filename}")
    
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
            print(f"[+] Model loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"[-] Model file not found: {filename}")
            return False

if __name__ == "__main__":
    engine = MessageEngine()
    
    # Sample training data (your texting style)
    training_data = [
        "yo whats up man",
        "im down for that",
        "nah not really feeling it",
        "bruhhh that's hilarious",
        "fr fr no cap",
        "lets goooo",
        "idk man seems sus",
        "yeah okay cool",
        "lmaooo stop",
        "literally can't even",
        "ok bet ill be there",
        "nope not happening",
        "thats lowkey fire",
        "my bad i was sleeping",
        "for real though",
        "that's facts",
        "cap on god",
        "deadass though",
        "not even joking",
        "on everything"
    ]
    
    engine.train(training_data)
    engine.save("message_model.json")
    
    # Generate and score replies
    print("\n=== Generated Replies ===")
    for i in range(5):
        reply = engine.generate_reply()
        confidence = engine.calculate_confidence(reply)
        status = "✓ SEND" if confidence >= 0.85 else "⊘ WAIT"
        print(f"{i+1}. '{reply}' [{confidence*100:.0f}%] {status}")
