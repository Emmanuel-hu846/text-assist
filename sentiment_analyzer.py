#!/usr/bin/env python3
"""
Sentiment Analysis & Emotion Matching
Detect emotional tone and match it in replies
"""

import re
from typing import Tuple
from textblob import TextBlob

class SentimentAnalyzer:
    """Analyze and match emotional tone of messages"""
    
    def __init__(self):
        # Sentiment lexicons
        self.positive_words = {
            'good', 'great', 'awesome', 'amazing', 'wonderful', 'excellent',
            'love', 'like', 'happy', 'excited', 'fire', 'sick', 'dope', 'lit',
            'cool', 'nice', 'sweet', 'rad', 'brilliant', 'fantastic', 'beautiful'
        }
        
        self.negative_words = {
            'bad', 'horrible', 'awful', 'terrible', 'hate', 'angry', 'sad',
            'depressed', 'annoyed', 'frustrated', 'tired', 'exhausted', 'sick',
            'mad', 'pissed', 'sucks', 'garbage', 'trash', 'disgusting'
        }
        
        self.question_markers = {'?', 'what', 'who', 'when', 'where', 'why', 'how'}
        
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text
        Returns: (polarity: -1 to 1, emotion: 'positive'|'neutral'|'negative')
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                emotion = 'positive'
            elif polarity < -0.1:
                emotion = 'negative'
            else:
                emotion = 'neutral'
            
            return polarity, emotion
        except:
            return 0.0, 'neutral'
    
    def is_question(self, text: str) -> bool:
        """Detect if text is a question"""
        text_lower = text.lower()
        
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words
        words = text_lower.split()
        if any(word in self.question_markers for word in words[:3]):
            return True
        
        return False
    
    def is_excited(self, text: str) -> bool:
        """Detect excitement (multiple exclamation marks, caps, etc)"""
        return (
            text.count('!') >= 2 or
            text.count('!') >= 1 and len(text) < 20 or
            'aaa' in text.lower() or
            'ooo' in text.lower() or
            'eee' in text.lower()
        )
    
    def is_sad_or_frustrated(self, text: str) -> bool:
        """Detect sadness or frustration"""
        text_lower = text.lower()
        return (
            '...' in text or
            text.count('.') >= 3 or
            any(word in text_lower for word in ['sad', 'mad', 'angry', 'frustrat', 'tired', 'sick'])
        )
    
    def get_emotion_category(self, text: str) -> str:
        """Get emotional category of text"""
        polarity, emotion = self.analyze_sentiment(text)
        
        if self.is_excited(text):
            return 'excited'
        elif self.is_sad_or_frustrated(text):
            return 'sad'
        elif self.is_question(text):
            return 'question'
        else:
            return emotion
    
    def match_sentiment_in_reply(self, incoming_msg: str, generated_reply: str) -> float:
        """
        Score how well generated reply matches incoming message sentiment
        Returns: 0-1 confidence adjustment
        """
        incoming_emotion = self.get_emotion_category(incoming_msg)
        
        # Check if reply matches emotion
        if incoming_emotion == 'question':
            # Question should get a real answer, not a question back
            return 1.0 if not self.is_question(generated_reply) else 0.6
        
        elif incoming_emotion == 'excited':
            # Should reply enthusiastically
            if self.is_excited(generated_reply):
                return 1.0
            elif self.is_excited(incoming_msg):
                return 0.8
            else:
                return 0.5
        
        elif incoming_emotion == 'sad':
            # Should reply with support
            if any(word in generated_reply.lower() for word in ['ok', 'there', 'gotcha', 'sorry', 'understand']):
                return 1.0
            else:
                return 0.7
        
        else:
            return 0.9  # Neutral matches most things
    
    def adjust_reply_for_emotion(self, reply: str, incoming_msg: str, intensity: float = 1.0) -> str:
        """Modify reply to match emotional tone"""
        emotion = self.get_emotion_category(incoming_msg)
        
        if emotion == 'excited' and intensity > 0.7:
            # Add excitement
            if not reply.endswith('!'):
                reply = reply + '!'
            if len(reply) > 5:
                reply = reply.replace('yeah', 'yeah!!!').replace('ok', 'ok!!!').replace('yo', 'yooo')
        
        elif emotion == 'sad' and intensity < 0.3:
            # Add empathy
            if reply.startswith('yo'):
                reply = 'yeah' + reply[2:]
        
        return reply


class QuestionDetector:
    """Detect questions and appropriate response types"""
    
    def __init__(self):
        self.question_words = {
            'what', 'who', 'when', 'where', 'why', 'how',
            'which', 'whose', 'whom', 'can', 'could', 'will',
            'would', 'should', 'do', 'does', 'did', 'is', 'are', 'am'
        }
    
    def get_question_type(self, text: str) -> str:
        """Classify type of question"""
        text_lower = text.lower()
        
        if text_lower.startswith('what'):
            return 'what_question'
        elif text_lower.startswith('who'):
            return 'who_question'
        elif text_lower.startswith('when'):
            return 'when_question'
        elif text_lower.startswith('where'):
            return 'where_question'
        elif text_lower.startswith('why'):
            return 'why_question'
        elif text_lower.startswith('how'):
            return 'how_question'
        elif '?' in text:
            return 'yes_no_question'
        else:
            return 'not_question'
    
    def is_direct_question_to_you(self, text: str) -> bool:
        """Check if question is directed at the user"""
        text_lower = text.lower()
        you_markers = {'you', 'your', 'u', 'ur', 'yourself'}
        return any(marker in text_lower for marker in you_markers)


class MultiLanguageDetector:
    """Detect language and maintain it in replies"""
    
    def __init__(self):
        self.language_patterns = {
            'spanish': ['hola', 'por', 'qué', 'eres', 'está', 'está'],
            'french': ['bonjour', 'quoi', 'pourquoi', 'comment', 'comment'],
            'hindi': ['kya', 'kaise', 'kaun', 'kaha'],
            'english': ['what', 'where', 'how', 'why', 'hello', 'hey']
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of message"""
        text_lower = text.lower()
        
        for lang, patterns in self.language_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            if matches >= 2:
                return lang
        
        return 'english'  # Default
    
    def should_reply_in_language(self, contact_history: list) -> str:
        """Determine language to use based on conversation history"""
        if not contact_history:
            return 'english'
        
        # Check last 5 messages
        recent = contact_history[-5:]
        languages = [self.detect_language(msg) for msg in recent]
        
        # Return most common language
        return max(set(languages), key=languages.count)


if __name__ == "__main__":
    # Test sentiment analysis
    analyzer = SentimentAnalyzer()
    
    test_messages = [
        "yo that's awesome!!!",
        "what are you doing?",
        "im so tired...",
        "nah not really",
        "OMG I LOVE THIS"
    ]
    
    print("=== Sentiment Analysis ===\n")
    for msg in test_messages:
        polarity, emotion = analyzer.analyze_sentiment(msg)
        category = analyzer.get_emotion_category(msg)
        print(f"Message: '{msg}'")
        print(f"  Polarity: {polarity:.2f}")
        print(f"  Emotion: {emotion}")
        print(f"  Category: {category}")
        print(f"  Is Question: {analyzer.is_question(msg)}\n")
