#!/usr/bin/env python3
"""
Media Handling & Context Analysis
View images/videos and generate context-aware replies
"""

import base64
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
import json

class MediaHandler:
    """Handle images, videos, and other media in conversations"""
    
    def __init__(self):
        self.supported_media = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'video': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
            'audio': ['mp3', 'wav', 'm4a', 'aac'],
            'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt']
        }
        self.media_cache = {}
    
    def get_media_type(self, file_path: str) -> Optional[str]:
        """Detect media type from file"""
        if not file_path:
            return None
        
        ext = Path(file_path).suffix.lower().lstrip('.')
        
        for media_type, extensions in self.supported_media.items():
            if ext in extensions:
                return media_type
        
        return None
    
    def extract_image_description(self, image_path: str) -> str:
        """
        Extract description/context from image
        Uses simple file analysis (can integrate with Google Vision API)
        """
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            width, height = img.size
            
            # Basic description based on image properties
            description = f"image_{width}x{height}"
            
            # Could integrate with Google Vision API here
            # from google.cloud import vision
            # client = vision.ImageAnnotatorClient()
            # response = client.label_detection(...)
            
            return description
        except:
            return "image"
    
    def analyze_media_context(self, media_path: str) -> dict:
        """Analyze media and provide context"""
        media_type = self.get_media_type(media_path)
        
        if not media_type:
            return {'type': 'unknown', 'context': 'unknown media'}
        
        file_size = Path(media_path).stat().st_size if Path(media_path).exists() else 0
        
        if media_type == 'image':
            try:
                description = self.extract_image_description(media_path)
                context = f"shared an image ({description})"
            except:
                context = "shared an image"
        
        elif media_type == 'video':
            context = "shared a video"
        
        elif media_type == 'audio':
            context = "shared an audio message"
        
        else:
            context = f"shared a {media_type}"
        
        return {
            'type': media_type,
            'context': context,
            'size': file_size,
            'path': media_path
        }
    
    def generate_media_response(self, media_type: str) -> str:
        """Generate appropriate response to media"""
        responses = {
            'image': [
                'yo thats fire',
                'niceee',
                'let me see that',
                'thats cool',
                'yo look at that'
            ],
            'video': [
                'lemme watch that',
                'thats crazy',
                'yo send that',
                'wild'
            ],
            'audio': [
                'send it',
                'lemme hear that',
                'yo',
                'ok'
            ],
            'document': [
                'got it',
                'thanks',
                'ok',
                'ill check it out'
            ]
        }
        
        import random
        return random.choice(responses.get(media_type, ['ok']))
    
    def cache_media(self, contact: str, media_path: str, description: str):
        """Cache media info for learning"""
        if contact not in self.media_cache:
            self.media_cache[contact] = []
        
        self.media_cache[contact].append({
            'path': media_path,
            'description': description,
            'type': self.get_media_type(media_path)
        })
    
    def get_contact_media_history(self, contact: str) -> list:
        """Get media shared by contact"""
        return self.media_cache.get(contact, [])


class ContextAnalyzer:
    """Analyze conversation context for better replies"""
    
    def __init__(self):
        self.context_window = 10  # Look at last N messages
    
    def analyze_conversation_flow(self, message_history: list) -> dict:
        """Analyze conversation pattern"""
        if not message_history:
            return {'topic': 'unknown', 'flow': 'new', 'sentiment_trend': 'neutral'}
        
        recent = message_history[-self.context_window:]
        
        return {
            'message_count': len(recent),
            'avg_length': sum(len(m.split()) for m in recent) / len(recent) if recent else 0,
            'has_questions': any('?' in m for m in recent),
            'last_message': recent[-1] if recent else None,
            'conversation_active': len(recent) > 3
        }
    
    def detect_topic(self, message: str) -> str:
        """Simple topic detection"""
        keywords = {
            'plans': ['want to', 'lets', 'come over', 'hang', 'meet', 'time'],
            'help': ['help', 'can you', 'could you', 'need', 'stuck'],
            'complaint': ['hate', 'annoyed', 'frustrated', 'angry', 'mad'],
            'celebration': ['great', 'awesome', 'amazing', 'excited', 'happy'],
            'question': ['what', 'why', 'how', 'who', 'when', 'where']
        }
        
        msg_lower = message.lower()
        
        for topic, words in keywords.items():
            if any(word in msg_lower for word in words):
                return topic
        
        return 'general'
    
    def suggest_response_type(self, context: dict, topic: str) -> str:
        """Suggest what type of response is appropriate"""
        if '?' in context.get('last_message', ''):
            return 'answer'
        elif topic == 'plans':
            return 'agreement'
        elif topic == 'help':
            return 'support'
        elif topic == 'complaint':
            return 'empathy'
        elif topic == 'celebration':
            return 'excitement'
        else:
            return 'casual'


class MessageScheduler:
    """Learn and match your reply timing patterns"""
    
    def __init__(self):
        self.reply_times = defaultdict(list)  # Contact -> [times]
        self.reply_delays = defaultdict(list)  # Contact -> [delay_in_seconds]
    
    def record_reply(self, contact: str, delay_seconds: float):
        """Record when you replied"""
        from datetime import datetime
        
        self.reply_times[contact].append(datetime.now())
        self.reply_delays[contact].append(delay_seconds)
    
    def get_typical_reply_delay(self, contact: str) -> float:
        """Get your typical reply delay for a contact"""
        delays = self.reply_delays.get(contact, [])
        
        if not delays:
            return 300  # Default 5 minutes
        
        # Return median delay
        import statistics
        return statistics.median(delays)
    
    def should_reply_immediately(self, contact: str) -> bool:
        """Check if you typically reply immediately to this contact"""
        delay = self.get_typical_reply_delay(contact)
        return delay < 60  # Less than 1 minute


if __name__ == "__main__":
    from collections import defaultdict
    
    print("=== Media & Context Analysis ===\n")
    
    # Test media handling
    handler = MediaHandler()
    
    test_files = [
        "photo.jpg",
        "video.mp4",
        "document.pdf",
        "audio.mp3"
    ]
    
    print("[*] Media Type Detection:")
    for file in test_files:
        media_type = handler.get_media_type(file)
        print(f"  {file}: {media_type}")
    
    print("\n[*] Media Response Generation:")
    for media_type in ['image', 'video', 'audio', 'document']:
        response = handler.generate_media_response(media_type)
        print(f"  {media_type}: '{response}'")
    
    # Test context analysis
    print("\n[*] Context Analysis:")
    analyzer = ContextAnalyzer()
    
    test_messages = [
        "yo what are you doing?",
        "want to hang out?",
        "im so frustrated with work",
        "i just got a new job!!"
    ]
    
    for msg in test_messages:
        topic = analyzer.detect_topic(msg)
        response_type = analyzer.suggest_response_type({'last_message': msg}, topic)
        print(f"  Message: '{msg}'")
        print(f"    Topic: {topic}, Suggest: {response_type}")
