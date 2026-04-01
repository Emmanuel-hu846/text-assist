#!/usr/bin/env python3
import json
import time
from datetime import datetime
from pathlib import Path
from message_engine import MessageEngine

class IntegrationDaemon:
    def __init__(self, model_file: str = "message_model.json", confidence_threshold: float = 0.85):
        self.model_file = model_file
        self.confidence_threshold = confidence_threshold
        self.running = True
        self.message_log = "auto_reply_log.json"
        self.engine = MessageEngine()
        
        if Path(model_file).exists():
            self.engine.load(model_file)
        
    def generate_reply(self) -> str:
        """Generate reply using trained model"""
        return self.engine.generate_reply()
    
    def get_confidence(self, msg: str) -> float:
        """Get confidence score for message"""
        return self.engine.calculate_confidence(msg)
    
    def log_decision(self, contact: str, incoming_msg: str, generated_reply: str, confidence: float, approved: bool):
        """Log all auto-reply decisions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "contact": contact,
            "incoming": incoming_msg,
            "generated": generated_reply,
            "confidence": confidence,
            "approved": approved,
            "sent": approved and confidence >= self.confidence_threshold
        }
        
        logs = []
        if Path(self.message_log).exists():
            with open(self.message_log, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        with open(self.message_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def monitor_messages(self):
        """Main daemon loop - simulates message monitoring"""
        print("[*] Auto-reply daemon starting...")
        print(f"[*] Confidence threshold: {self.confidence_threshold * 100}%")
        print("[*] Model file:", self.model_file)
        print("[*] Watching for new messages...")
        
        iteration = 0
        while self.running:
            iteration += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan #{iteration}")
            
            # Generate reply
            reply = self.generate_reply()
            confidence = self.get_confidence(reply)
            
            print(f"  Generated: '{reply}'")
            print(f"  Confidence: {confidence * 100:.1f}%")
            
            if confidence >= self.confidence_threshold:
                print(f"  ✓ APPROVED - Would send auto-reply")
                self.log_decision("contact", "incoming message", reply, confidence, True)
            else:
                print(f"  ⊘ PENDING - Confidence below threshold ({self.confidence_threshold*100:.0f}% required)")
                self.log_decision("contact", "incoming message", reply, confidence, False)
            
            print(f"  Logged to: {self.message_log}")
            time.sleep(30)
    
    def get_stats(self):
        """Print statistics"""
        if not Path(self.message_log).exists():
            print("No logs found yet")
            return
        
        with open(self.message_log, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        sent = sum(1 for log in logs if log.get('sent'))
        avg_confidence = sum(log['confidence'] for log in logs) / total if total > 0 else 0
        
        print(f"\n=== Auto-Reply Statistics ===")
        print(f"Total scans: {total}")
        print(f"Auto-replies sent: {sent}")
        print(f"Avg confidence: {avg_confidence * 100:.1f}%")
        print(f"Success rate: {(sent/total*100):.1f}%" if total > 0 else "0%")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        daemon = IntegrationDaemon()
        daemon.get_stats()
    else:
        daemon = IntegrationDaemon(confidence_threshold=0.85)
        try:
            daemon.monitor_messages()
        except KeyboardInterrupt:
            print("\n[*] Daemon stopped")
            sys.exit(0)
