#!/usr/bin/env python3
"""
Advanced Message Engine
Better text generation with context awareness and multi-factor confidence
"""

import json
import random
import math
from collections import defaultdict
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AdvancedMessageEngine:
    def __init__(self):
        self.markov_chain = defaultdict(lambda: defaultdict(int))
        self.word_freq = defaultdict(int)
        self.vocabulary = []
        self.training_messages = []
        self.vectorizer = None
        self.tfidf_matrix = None
        
    def tokenize(self, text):
        """Tokenize text"""
        return text.lower().split()
    
    def train(self, messages):
        """Train on message history"""
        self.training_messages = messages
        
        # Build Markov chain
        for msg in messages:
            tokens = self.tokenize(msg)
            
            for token in tokens:
                self.word_freq[token] += 1
            
            for i in range(len(tokens) - 1):
                self.markov_chain[tokens[i]][tokens[i + 1]] += 1
        
        self.vocabulary = list(self.word_freq.keys())
        
        # Build TF-IDF for similarity
        try:
            self.vectorizer = TfidfVectorizer(max_features=100)
            self.tfidf_matrix = self.vectorizer.fit_transform(messages)
        except:
            self.vectorizer = None
    
    def generate_base_reply(self, max_length=15):
        """Generate reply using Markov chain"""
        if not self.vocabulary:
            return "yeah"
        
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
    
    def calculate_token_match_score(self, generated_msg):
        """Score based on token usage (0-1)"""
        tokens = self.tokenize(generated_msg)
        if not tokens:
            return 0.0
        
        matches = sum(1 for token in tokens if token in self.word_freq)
        return matches / len(tokens)
    
    def calculate_similarity_score(self, generated_msg):
        """Score based on similarity to training messages"""
        if self.vectorizer is None or self.tfidf_matrix is None:
            return 0.5
        
        try:
            generated_vector = self.vectorizer.transform([generated_msg])
            similarities = cosine_similarity(generated_vector, self.tfidf_matrix)[0]
            
            if len(similarities) == 0:
                return 0.5
            
            # Return average similarity (can be >1 normalized)
            return min(np.mean(similarities) * 2, 1.0)
        except:
            return 0.5
    
    def calculate_length_score(self, generated_msg):
        """Penalize extremely short or long messages"""
        word_count = len(self.tokenize(generated_msg))
        
        # Optimal range: 3-15 words
        if 3 <= word_count <= 15:
            return 1.0
        elif word_count < 3:
            return word_count / 3.0
        else:
            return min(1.0, 15 / word_count)
    
    def calculate_confidence(self, generated_msg):
        """Multi-factor confidence scoring"""
        scores = {
            'token_match': self.calculate_token_match_score(generated_msg),
            'similarity': self.calculate_similarity_score(generated_msg),
            'length': self.calculate_length_score(generated_msg)
        }
        
        # Weighted average
        weights = {
            'token_match': 0.4,
            'similarity': 0.4,
            'length': 0.2
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores)
        return min(max(final_score, 0.0), 1.0)
    
    def generate_reply(self, context_messages=None):
        """Generate a contextual reply"""
        reply = self.generate_base_reply()
        
        # If context provided, can add logic to match context
        # (e.g., question detection, sentiment matching)
        if context_messages:
            # Could analyze last message for context
            pass
        
        return reply
    
    def generate_multiple(self, count=5, context_messages=None):
        """Generate multiple replies and return best one"""
        candidates = []
        
        for _ in range(count * 3):  # Generate more than needed
            reply = self.generate_reply(context_messages)
            confidence = self.calculate_confidence(reply)
            candidates.append((reply, confidence))
        
        # Return top one
        if candidates:
            best = max(candidates, key=lambda x: x[1])
            return best[0], best[1]
        
        return "hey", 0.5
    
    def save(self, filename):
        """Save model"""
        data = {
            'vocabulary': self.vocabulary,
            'word_freq': dict(self.word_freq),
            'markov_chain': {k: dict(v) for k, v in self.markov_chain.items()},
            'training_messages': self.training_messages
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filename):
        """Load model"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.vocabulary = data['vocabulary']
            self.word_freq = defaultdict(int, data['word_freq'])
            self.training_messages = data.get('training_messages', [])
            
            self.markov_chain = defaultdict(lambda: defaultdict(int))
            for word, nexts in data['markov_chain'].items():
                self.markov_chain[word] = defaultdict(int, nexts)
            
            # Re-build TF-IDF
            if self.training_messages:
                try:
                    self.vectorizer = TfidfVectorizer(max_features=100)
                    self.tfidf_matrix = self.vectorizer.fit_transform(self.training_messages)
                except:
                    pass
            
            return True
        except FileNotFoundError:
            return False

if __name__ == "__main__":
    # Test
    engine = AdvancedMessageEngine()
    messages = [
        "yo whats up",
        "im down for that",
        "nah not really",
        "bruhhh thats fire",
        "fr fr no cap",
        "lets goooo",
        "idk seems sus",
        "yeah cool",
        "lmaooo",
        "literally cant",
        "ok bet",
        "nope",
        "my bad was sleeping"
    ]
    
    engine.train(messages)
    
    print("=== Advanced Message Generation ===\n")
    for i in range(5):
        reply, conf = engine.generate_multiple(count=5)
        status = "✓" if conf >= 0.85 else "⊘"
        print(f"{i+1}. '{reply}' [{conf*100:.0f}%] {status}")
