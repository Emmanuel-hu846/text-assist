#!/usr/bin/env python3
"""
WhatsApp Auto-Reply Integration
Connects to WhatsApp Web and auto-replies based on learned patterns
"""

import time
import json
import re
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhatsAppBot:
    def __init__(self, headless=False, approval_required=True):
        self.headless = headless
        self.approval_required = approval_required
        self.driver = None
        self.message_log = "whatsapp_interactions.json"
        self.processed_messages = set()
        
    def setup_driver(self):
        """Initialize Selenium WebDriver for WhatsApp Web"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0")
        chrome_options.add_argument("--start-maximized")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("[+] WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"[-] Failed to initialize WebDriver: {e}")
            return False
    
    def load_whatsapp(self, timeout=30):
        """Load WhatsApp Web and wait for QR scan"""
        try:
            logger.info("[*] Loading WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            logger.info("[!] Please scan QR code in the browser window")
            logger.info("[*] Waiting for login (timeout: 30s)...")
            
            # Wait for chat list to load (indicates successful login)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='chat-list-item']"))
            )
            
            logger.info("[+] WhatsApp Web loaded successfully")
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"[-] Failed to load WhatsApp: {e}")
            return False
    
    def get_unread_messages(self):
        """Get all unread messages"""
        try:
            unread_chats = self.driver.find_elements(By.XPATH, "//div[@data-testid='chat-list-item']")
            messages = []
            
            for chat in unread_chats:
                try:
                    # Get chat name
                    name_elem = chat.find_element(By.XPATH, ".//span[@title]")
                    contact_name = name_elem.get_attribute("title")
                    
                    # Check if unread (has unread badge)
                    try:
                        badge = chat.find_element(By.XPATH, ".//span[@data-icon='unread-badge']")
                        messages.append({
                            "contact": contact_name,
                            "element": chat,
                            "id": f"{contact_name}_{time.time()}"
                        })
                    except:
                        pass
                except:
                    pass
            
            return messages
        except Exception as e:
            logger.error(f"[-] Error getting unread messages: {e}")
            return []
    
    def open_chat(self, chat_element, timeout=10):
        """Open a specific chat"""
        try:
            chat_element.click()
            time.sleep(2)
            
            # Wait for message input to be available
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            return True
        except Exception as e:
            logger.error(f"[-] Error opening chat: {e}")
            return False
    
    def get_recent_messages(self, count=10):
        """Get last N messages from current chat"""
        try:
            messages = self.driver.find_elements(
                By.XPATH, 
                "//div[@data-testid='msg-container']//div[@class='copyable-text']"
            )
            
            recent = []
            for msg in messages[-count:]:
                text = msg.get_attribute("data-pre-plain-text")
                if text:
                    recent.append(text)
            
            return recent
        except Exception as e:
            logger.error(f"[-] Error getting recent messages: {e}")
            return []
    
    def send_message(self, text):
        """Send a message in the current chat"""
        try:
            # Find message input box
            input_box = self.driver.find_element(
                By.XPATH, 
                "//div[@contenteditable='true'][@data-tab='10']"
            )
            
            # Type message
            input_box.click()
            input_box.send_keys(text)
            time.sleep(0.5)
            
            # Send message
            send_button = self.driver.find_element(
                By.XPATH,
                "//button[@aria-label='Send']"
            )
            send_button.click()
            
            logger.info(f"[+] Message sent: '{text}'")
            return True
            
        except Exception as e:
            logger.error(f"[-] Error sending message: {e}")
            return False
    
    def log_interaction(self, contact, incoming, generated, confidence, sent, approved=False):
        """Log WhatsApp interaction"""
        logs = []
        if Path(self.message_log).exists():
            with open(self.message_log, 'r') as f:
                logs = json.load(f)
        
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "contact": contact,
            "incoming_message": incoming,
            "generated_reply": generated,
            "confidence": round(confidence, 3),
            "sent": sent,
            "required_approval": self.approval_required,
            "approved": approved
        })
        
        with open(self.message_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def monitor_and_reply(self, engine, check_interval=10, max_iterations=None):
        """Monitor WhatsApp and auto-reply"""
        logger.info("[*] Starting WhatsApp monitoring...")
        logger.info(f"[*] Check interval: {check_interval}s")
        logger.info(f"[*] Approval required: {self.approval_required}")
        
        iteration = 0
        
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    break
                
                iteration += 1
                logger.info(f"\n[*] Scan #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Get unread messages
                unread = self.get_unread_messages()
                logger.info(f"[*] Unread chats: {len(unread)}")
                
                for chat_info in unread:
                    contact = chat_info["contact"]
                    msg_id = chat_info["id"]
                    
                    if msg_id in self.processed_messages:
                        continue
                    
                    logger.info(f"[→] Processing chat: {contact}")
                    
                    # Open chat
                    if not self.open_chat(chat_info["element"]):
                        continue
                    
                    # Get recent messages for context
                    recent_msgs = self.get_recent_messages(5)
                    
                    # Generate reply
                    reply = engine.generate_reply(recent_msgs)
                    confidence = engine.calculate_confidence(reply)
                    
                    logger.info(f"  Generated: '{reply}'")
                    logger.info(f"  Confidence: {confidence*100:.1f}%")
                    
                    # Decision logic
                    should_send = confidence >= 0.85
                    
                    if should_send:
                        if self.approval_required:
                            user_input = input(f"  Send this reply? (y/n): ").lower()
                            if user_input != 'y':
                                logger.info(f"  ⊘ User rejected")
                                self.log_interaction(contact, recent_msgs[-1] if recent_msgs else "", 
                                                   reply, confidence, False, False)
                                continue
                        
                        # Send message
                        if self.send_message(reply):
                            self.log_interaction(contact, recent_msgs[-1] if recent_msgs else "", 
                                               reply, confidence, True, True)
                            self.processed_messages.add(msg_id)
                        else:
                            logger.error(f"  Failed to send message")
                    else:
                        logger.info(f"  ⊘ Confidence too low ({confidence*100:.1f}% < 85%)")
                        self.log_interaction(contact, recent_msgs[-1] if recent_msgs else "", 
                                           reply, confidence, False, True)
                
                logger.info(f"[*] Next check in {check_interval}s...")
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n[*] Monitoring stopped by user")
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_stats(self):
        """Print interaction statistics"""
        if not Path(self.message_log).exists():
            logger.warning("No interaction logs found")
            return
        
        with open(self.message_log, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        sent = sum(1 for log in logs if log['sent'])
        avg_confidence = sum(log['confidence'] for log in logs) / total if total > 0 else 0
        contacts = set(log['contact'] for log in logs)
        
        logger.info("\n" + "="*40)
        logger.info("WhatsApp Interaction Statistics")
        logger.info("="*40)
        logger.info(f"Total interactions: {total}")
        logger.info(f"Messages sent: {sent}")
        logger.info(f"Messages held back: {total - sent}")
        logger.info(f"Avg confidence: {avg_confidence*100:.1f}%")
        logger.info(f"Unique contacts: {len(contacts)}")
        logger.info(f"Success rate: {(sent/total*100):.1f}%" if total > 0 else "0%")
        logger.info("="*40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Usage: python3 whatsapp_integration.py <command> [options]")
        print("\nCommands:")
        print("  connect        - Connect to WhatsApp Web (manual mode)")
        print("  monitor        - Start auto-reply monitoring")
        print("  stats          - Show interaction statistics")
        print("\nOptions:")
        print("  --no-approval  - Send without user approval (risky!)")
        print("  --headless     - Run in headless mode")
        sys.exit(1)
    
    cmd = sys.argv[1]
    no_approval = "--no-approval" in sys.argv
    headless = "--headless" in sys.argv
    
    bot = WhatsAppBot(headless=headless, approval_required=not no_approval)
    
    if cmd == "connect":
        if bot.setup_driver():
            bot.load_whatsapp()
            logger.info("[*] Connected. Keep browser open. Press Ctrl+C to exit.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("[*] Disconnecting...")
                bot.driver.quit()
    
    elif cmd == "monitor":
        logger.warning("[!] WhatsApp monitoring requires trained model")
        model_path = "message_model.json"
        
        if not Path(model_path).exists():
            logger.error(f"[-] Model not found: {model_path}")
            logger.error("[-] Train model first: python3 auto_reply.py train messages.json")
            sys.exit(1)
        
        from auto_reply import MessageEngine
        engine = MessageEngine()
        engine.load(model_path)
        
        if bot.setup_driver():
            if bot.load_whatsapp():
                bot.monitor_and_reply(engine, check_interval=15, max_iterations=None)
            bot.driver.quit()
    
    elif cmd == "stats":
        bot.get_stats()
    
    else:
        logger.error(f"Unknown command: {cmd}")
        sys.exit(1)
