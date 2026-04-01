#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import List

class MessageParser:
    @staticmethod
    def parse_whatsapp_export(file_path: str) -> List[str]:
        """Parse WhatsApp exported chat file"""
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # WhatsApp format: [HH:MM, DD/MM/YYYY] Name: Message
                    match = re.search(r']: (.+)$', line)
                    if match:
                        msg = match.group(1).strip()
                        if msg and not msg.startswith('<'):  # Skip media messages
                            messages.append(msg)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        return messages

    @staticmethod
    def parse_json_messages(file_path: str) -> List[str]:
        """Parse JSON message format"""
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
            print(f"Error parsing JSON: {e}")
        return messages

    @staticmethod
    def clean_messages(messages: List[str]) -> List[str]:
        """Clean and filter messages"""
        cleaned = []
        for msg in messages:
            # Remove URLs
            msg = re.sub(r'http\S+|www\S+', '', msg)
            # Remove extra whitespace
            msg = ' '.join(msg.split())
            if len(msg) > 3 and len(msg) < 500:  # Filter too short/long messages
                cleaned.append(msg)
        return cleaned

def train_from_file(input_file: str, output_model: str):
    """Train model from message file"""
    parser = MessageParser()
    
    # Try WhatsApp format first, then JSON
    messages = parser.parse_whatsapp_export(input_file)
    if not messages:
        messages = parser.parse_json_messages(input_file)
    
    if not messages:
        print("No messages found. Please provide valid input file.")
        print("Formats: WhatsApp export (txt) or JSON messages")
        return
    
    messages = parser.clean_messages(messages)
    print(f"Loaded {len(messages)} messages from {input_file}")
    
    # Save as JSON for C++ engine
    with open(output_model, 'w', encoding='utf-8') as f:
        json.dump({"messages": messages}, f, indent=2)
    
    print(f"Training data saved to {output_model}")
    return messages

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 train_model.py <input_file> [output_model]")
        print("Example: python3 train_model.py chat_export.txt messages.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_model = sys.argv[2] if len(sys.argv) > 2 else "training_messages.json"
    
    train_from_file(input_file, output_model)
