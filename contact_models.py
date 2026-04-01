#!/usr/bin/env python3
"""
Contact-Specific Models
Learn different reply patterns per contact
"""

import json
from pathlib import Path
from collections import defaultdict
from advanced_engine import AdvancedMessageEngine

class ContactModelManager:
    """Manage separate AI models for each contact"""
    
    def __init__(self, base_dir="contact_models"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.models = {}
        self.contact_histories = defaultdict(list)
    
    def get_contact_model_path(self, contact: str) -> Path:
        """Get path for contact-specific model"""
        safe_name = contact.replace(' ', '_').replace('/', '_').lower()
        return self.base_dir / f"{safe_name}_model.json"
    
    def load_or_create_model(self, contact: str) -> AdvancedMessageEngine:
        """Load existing contact model or create new one"""
        if contact in self.models:
            return self.models[contact]
        
        model = AdvancedMessageEngine()
        model_path = self.get_contact_model_path(contact)
        
        if model_path.exists():
            model.load(str(model_path))
            print(f"[+] Loaded model for {contact}")
        else:
            print(f"[*] Creating new model for {contact}")
        
        self.models[contact] = model
        return model
    
    def train_contact_model(self, contact: str, messages: list):
        """Train a model on messages from specific contact"""
        model = AdvancedMessageEngine()
        model.train(messages)
        
        model_path = self.get_contact_model_path(contact)
        model.save(str(model_path))
        
        self.models[contact] = model
        print(f"[+] Trained model for {contact} with {len(messages)} messages")
    
    def add_to_history(self, contact: str, message: str):
        """Add message to contact's conversation history"""
        self.contact_histories[contact].append(message)
        
        # Keep only last 50 messages in memory
        if len(self.contact_histories[contact]) > 50:
            self.contact_histories[contact] = self.contact_histories[contact][-50:]
    
    def get_contact_history(self, contact: str, count: int = 10) -> list:
        """Get recent conversation history with contact"""
        history = self.contact_histories[contact]
        return history[-count:] if history else []
    
    def generate_contact_reply(self, contact: str, context: list = None) -> Tuple[str, float]:
        """Generate reply tailored to specific contact"""
        model = self.load_or_create_model(contact)
        
        # Use contact-specific model if trained, otherwise use general
        if model.training_messages:
            reply, confidence = model.generate_multiple(count=5, context_messages=context)
        else:
            reply, confidence = model.generate_reply(), 0.5
        
        return reply, confidence
    
    def get_contact_stats(self, contact: str) -> dict:
        """Get statistics about a contact's conversation"""
        model = self.load_or_create_model(contact)
        history = self.get_contact_history(contact, count=100)
        
        return {
            'contact': contact,
            'messages_trained': len(model.training_messages),
            'recent_history_size': len(history),
            'model_exists': len(model.vocabulary) > 0,
            'avg_msg_length': sum(len(msg.split()) for msg in history) / len(history) if history else 0
        }
    
    def list_trained_contacts(self) -> list:
        """List all contacts with trained models"""
        contacts = []
        for model_file in self.base_dir.glob("*_model.json"):
            contact_name = model_file.stem.replace('_model', '').replace('_', ' ').title()
            contacts.append(contact_name)
        return contacts

if __name__ == "__main__":
    from typing import Tuple
    
    # Test contact models
    manager = ContactModelManager()
    
    # Train separate models for different contacts
    john_messages = [
        "yo whats up",
        "im down for that",
        "nah not really",
        "bruhhh that's fire",
        "lets goooo"
    ]
    
    mom_messages = [
        "Hi honey, how are you?",
        "I hope you're doing well",
        "Let me know when you're free",
        "I miss you",
        "Take care of yourself"
    ]
    
    print("=== Contact-Specific Models ===\n")
    
    manager.train_contact_model("John", john_messages)
    manager.train_contact_model("Mom", mom_messages)
    
    print("\n[*] Generating replies:\n")
    
    # Generate John reply (casual)
    reply_john, conf_john = manager.generate_contact_reply("John")
    print(f"To John: '{reply_john}' [{conf_john*100:.0f}%]")
    
    # Generate Mom reply (formal)
    reply_mom, conf_mom = manager.generate_contact_reply("Mom")
    print(f"To Mom: '{reply_mom}' [{conf_mom*100:.0f}%]")
    
    print(f"\n[*] Trained contacts: {manager.list_trained_contacts()}")
    
    print("\n[*] Contact stats:")
    for contact in ["John", "Mom"]:
        stats = manager.get_contact_stats(contact)
        print(f"  {contact}: {stats['messages_trained']} messages trained")
