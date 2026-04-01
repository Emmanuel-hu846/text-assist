#!/usr/bin/env python3
"""
Advanced WhatsApp Integration with All Features
- Sentiment matching
- Contact-specific models
- Media handling
- Context awareness
- Message scheduling
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import Tuple, Optional

from sentiment_analyzer import SentimentAnalyzer, QuestionDetector, MultiLanguageDetector
from contact_models import ContactModelManager
from media_and_context import MediaHandler, ContextAnalyzer, MessageScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedWhatsAppBot:
    """Advanced WhatsApp bot with sentiment, context, media, and contact-specific learning"""
    
    def __init__(self, headless=False, approval_required=True):
        self.headless = headless
        self.approval_required = approval_required
        self.driver = None
        
        # Initialize advanced components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.question_detector = QuestionDetector()
        self.language_detector = MultiLanguageDetector()
        self.contact_manager = ContactModelManager()
        self.media_handler = MediaHandler()
        self.context_analyzer = ContextAnalyzer()
        self.message_scheduler = MessageScheduler()
        
        # Logging
        self.interaction_log = "advanced_interactions.json"
        self.processed_messages = set()
    
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
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
        """Load WhatsApp Web"""
        try:
            logger.info("[*] Loading WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            logger.info("[!] Please scan QR code in the browser window")
            
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
                    name_elem = chat.find_element(By.XPATH, ".//span[@title]")
                    contact_name = name_elem.get_attribute("title")
                    
                    try:
                        chat.find_element(By.XPATH, ".//span[@data-icon='unread-badge']")
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
            
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            return True
        except Exception as e:
            logger.error(f"[-] Error opening chat: {e}")
            return False
    
    def get_recent_messages(self, count=10) -> list:
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
        except:
            return []
    
    def detect_media(self) -> Optional[dict]:
        """Detect if chat contains media"""
        try:
            # Look for media elements
            media_elements = self.driver.find_elements(
                By.XPATH,
                "//div[@data-testid='msg-container']//img[@alt]"
            )
            
            if media_elements:
                last_media = media_elements[-1]
                alt_text = last_media.get_attribute("alt")
                src = last_media.get_attribute("src")
                
                return {
                    'type': 'image',
                    'description': alt_text,
                    'src': src
                }
            
            return None
        except:
            return None
    
    def generate_smart_reply(self, contact: str, incoming_message: str, context_messages: list = None) -> Tuple[str, float]:
        """
        Generate reply using all advanced features:
        - Contact-specific model
        - Sentiment matching
        - Question detection
        - Language matching
        - Context awareness
        """
        
        # Get contact-specific model
        model = self.contact_manager.load_or_create_model(contact)
        
        # Generate base reply
        base_reply, base_confidence = model.generate_multiple(count=5, context_messages=context_messages)
        
        # Analyze incoming message
        emotion = self.sentiment_analyzer.get_emotion_category(incoming_message)
        is_question = self.question_detector.is_direct_question_to_you(incoming_message)
        language = self.language_detector.detect_language(incoming_message)
        
        # Adjust reply based on sentiment
        sentiment_score = self.sentiment_analyzer.match_sentiment_in_reply(incoming_message, base_reply)
        
        # Adjust reply for emotion if needed
        if sentiment_score < 0.8:
            base_reply = self.sentiment_analyzer.adjust_reply_for_emotion(base_reply, incoming_message, sentiment_score)
        
        # Analyze context
        context = self.context_analyzer.analyze_conversation_flow(context_messages or [])
        topic = self.context_analyzer.detect_topic(incoming_message)
        
        # Combine scores
        final_confidence = (base_confidence * 0.5) + (sentiment_score * 0.3) + (0.2 * 0.9)  # Base 0.2 for other factors
        
        logger.info(f"  [Emotion: {emotion}, Question: {is_question}, Language: {language}, Topic: {topic}]")
        logger.info(f"  [Sentiment match: {sentiment_score*100:.0f}%, Base conf: {base_confidence*100:.0f}%, Final: {final_confidence*100:.0f}%]")
        
        return base_reply, final_confidence
    
    def send_message(self, text):
        """Send a message"""
        try:
            input_box = self.driver.find_element(
                By.XPATH,
                "//div[@contenteditable='true'][@data-tab='10']"
            )
            
            input_box.click()
            input_box.send_keys(text)
            time.sleep(0.5)
            
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
    
    def log_advanced_interaction(self, contact: str, incoming: str, generated: str, 
                                confidence: float, emotion: str, topic: str, 
                                sent: bool, approved=False, media: dict = None):
        """Log interaction with advanced metadata"""
        logs = []
        if Path(self.interaction_log).exists():
            with open(self.interaction_log, 'r') as f:
                logs = json.load(f)
        
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "contact": contact,
            "incoming_message": incoming,
            "generated_reply": generated,
            "confidence": round(confidence, 3),
            "emotion_detected": emotion,
            "topic": topic,
            "sent": sent,
            "approved": approved,
            "media_detected": media is not None,
            "media_info": media
        })
        
        with open(self.interaction_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def monitor_and_reply_advanced(self, check_interval=10, max_iterations=None):
        """Monitor WhatsApp with all advanced features"""
        logger.info("[*] Starting advanced WhatsApp monitoring...")
        logger.info(f"[*] Features: Sentiment, Contact-Models, Media, Context, Language")
        
        iteration = 0
        
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    break
                
                iteration += 1
                logger.info(f"\n[*] Scan #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                unread = self.get_unread_messages()
                logger.info(f"[*] Unread chats: {len(unread)}")
                
                for chat_info in unread:
                    contact = chat_info["contact"]
                    msg_id = chat_info["id"]
                    
                    if msg_id in self.processed_messages:
                        continue
                    
                    logger.info(f"\n[→] Processing: {contact}")
                    
                    if not self.open_chat(chat_info["element"]):
                        continue
                    
                    # Get conversation context
                    recent_msgs = self.get_recent_messages(10)
                    last_msg = recent_msgs[-1] if recent_msgs else "new message"
                    
                    # Check for media
                    media_info = self.detect_media()
                    if media_info:
                        logger.info(f"[📸] Media detected: {media_info['type']}")
                    
                    # Get sentiment and topic
                    emotion = self.sentiment_analyzer.get_emotion_category(last_msg)
                    topic = self.context_analyzer.detect_topic(last_msg)
                    
                    # Generate smart reply
                    reply, confidence = self.generate_smart_reply(contact, last_msg, recent_msgs)
                    
                    logger.info(f"  Generated: '{reply}'")
                    logger.info(f"  Confidence: {confidence*100:.1f}%")
                    
                    # Decision
                    should_send = confidence >= 0.85
                    
                    if should_send:
                        if self.approval_required:
                            user_input = input(f"  Send? (y/n): ").lower()
                            if user_input != 'y':
                                logger.info(f"  ⊘ User rejected")
                                self.log_advanced_interaction(contact, last_msg, reply, confidence,
                                                             emotion, topic, False, False, media_info)
                                continue
                        
                        if self.send_message(reply):
                            self.log_advanced_interaction(contact, last_msg, reply, confidence,
                                                         emotion, topic, True, True, media_info)
                            self.processed_messages.add(msg_id)
                            
                            # Record timing
                            self.message_scheduler.record_reply(contact, 0)
                    else:
                        logger.info(f"  ⊘ Confidence too low")
                        self.log_advanced_interaction(contact, last_msg, reply, confidence,
                                                     emotion, topic, False, True, media_info)
                
                logger.info(f"[*] Next check in {check_interval}s...")
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n[*] Monitoring stopped")
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_advanced_stats(self):
        """Get detailed statistics"""
        if not Path(self.interaction_log).exists():
            logger.warning("No logs found")
            return
        
        with open(self.interaction_log, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        sent = sum(1 for log in logs if log['sent'])
        media_messages = sum(1 for log in logs if log['media_detected'])
        
        emotions = {}
        topics = {}
        
        for log in logs:
            emotion = log.get('emotion_detected', 'unknown')
            topic = log.get('topic', 'unknown')
            
            emotions[emotion] = emotions.get(emotion, 0) + 1
            topics[topic] = topics.get(topic, 0) + 1
        
        logger.info("\n" + "="*50)
        logger.info("Advanced WhatsApp Statistics")
        logger.info("="*50)
        logger.info(f"Total interactions: {total}")
        logger.info(f"Messages sent: {sent}")
        logger.info(f"Messages with media: {media_messages}")
        logger.info(f"Success rate: {(sent/total*100):.1f}%" if total > 0 else "0%")
        logger.info(f"\nEmotions detected: {dict(emotions)}")
        logger.info(f"Topics found: {dict(topics)}")
        logger.info(f"\nTrained contacts: {self.contact_manager.list_trained_contacts()}")
        logger.info("="*50)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("""
Advanced WhatsApp Bot
Usage: python3 advanced_whatsapp.py <command>

Commands:
  connect   - Connect to WhatsApp Web
  monitor   - Start advanced monitoring
  stats     - Show statistics
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    no_approval = "--no-approval" in sys.argv
    
    bot = AdvancedWhatsAppBot(approval_required=not no_approval)
    
    if cmd == "monitor":
        if bot.setup_driver():
            if bot.load_whatsapp():
                bot.monitor_and_reply_advanced(check_interval=15)
            bot.driver.quit()
    
    elif cmd == "stats":
        bot.get_advanced_stats()
    
    elif cmd == "connect":
        if bot.setup_driver():
            bot.load_whatsapp()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                bot.driver.quit()
