# WhatsApp Auto-Reply System

A sophisticated system that learns your texting style and automatically replies to WhatsApp messages while sounding exactly like you.

## Features

✅ **Advanced AI Engine**
- Markov chain text generation
- TF-IDF similarity matching
- Multi-factor confidence scoring
- Context-aware replies

✅ **WhatsApp Web Integration**
- Real-time message monitoring
- Automatic reply detection
- User approval system
- Complete interaction logging

✅ **Smart Learning**
- Learns from your message history
- Matches your vocabulary and tone
- Adapts to different contacts
- Improves over time

✅ **Safety Features**
- Manual approval before sending (default)
- Confidence thresholding (85% minimum)
- Comprehensive logging
- Easy to pause/resume

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- 20+ messages for good training data

## Installation

### Option 1: Local Installation (Recommended for Testing)

```bash
# Clone or download the files
git clone <repo>
cd whatsapp-auto-reply

# Install dependencies
pip install -r requirements.txt

# You now have 3 main commands:
# 1. Train from messages
# 2. Test generation
# 3. Connect to WhatsApp
```

### Option 2: Docker

```bash
docker-compose up --build
docker-compose exec auto-reply python3 main.py
```

## Quick Start

### Step 1: Prepare Your Messages

**Option A: Export from WhatsApp**
- Open WhatsApp
- Find a contact
- More menu → Export chat (without media)
- Save as `messages.json` or `chat_export.txt`

**Option B: Use JSON Format**
```json
[
  "yo whats up",
  "im down for that",
  "nah not really",
  "bruhhh thats hilarious",
  "fr fr no cap",
  "lets goooo",
  "idk seems sus",
  "yeah cool"
]
```

### Step 2: Train the Model

```bash
python3 main.py train messages.json
```

Output:
```
[*] Loading messages from messages.json...
[+] Loaded 150 messages
[*] Training advanced engine...
[+] Model saved: message_model.json

[*] Test generation (5 samples):
  1. 'yo im down for that' [92%] ✓ GOOD
  2. 'nah not really feeling it' [88%] ✓ GOOD
  3. 'lets goooo' [85%] ✓ GOOD
  4. 'idk thats sus' [82%] ⊘ WEAK
  5. 'my bad was sleeping' [90%] ✓ GOOD

[+] Ready! Run: python3 main.py whatsapp
```

### Step 3: Test Generation

```bash
python3 main.py test
```

Generates 10 sample replies to verify quality before connecting.

### Step 4: Connect to WhatsApp

```bash
python3 main.py whatsapp
```

This will:
1. Open Chrome browser with WhatsApp Web
2. Ask you to scan QR code
3. Monitor for new messages
4. Generate and ask for approval before sending

**With manual approval (default):**
```bash
python3 main.py whatsapp
```

You'll be prompted before each reply:
```
[→] Processing chat: John
  Generated: 'yo whats up'
  Confidence: 92.0%
  Send this reply? (y/n): y
[+] Message sent: 'yo whats up'
```

**Without approval (automatic):**
```bash
python3 main.py whatsapp --no-approval
```

⚠️ **WARNING**: Only use `--no-approval` after extensive testing!

### Step 5: View Statistics

```bash
python3 main.py stats
```

Output:
```
========================================
WhatsApp Interaction Statistics
========================================
Total interactions: 23
Messages sent: 18
Messages held back: 5
Avg confidence: 87.3%
Unique contacts: 5
Success rate: 78.3%
========================================
```

## How It Works

### Training Phase
1. Reads your message history (WhatsApp export or JSON)
2. Builds word frequency map
3. Creates Markov chain (word → next word probabilities)
4. Computes TF-IDF vectors for similarity matching
5. Saves trained model to `message_model.json`

### Generation Phase
1. Generates multiple candidate replies using Markov chain
2. Evaluates each reply with multi-factor scoring:
   - **Token Match (40%)**: Do the words match your vocabulary?
   - **Similarity (40%)**: How similar is it to your previous messages?
   - **Length (20%)**: Is the message length reasonable (3-15 words)?
3. Returns the highest-scoring reply

### Confidence Scoring
- **0-60%**: Too different from your style, held back
- **60-85%**: Decent match, may be held for review
- **85%+**: Confident match, approved for sending

### WhatsApp Integration
1. Opens WhatsApp Web (requires QR scan)
2. Monitors all active chats for new messages
3. For each new message:
   - Generates context-aware reply
   - Calculates confidence score
   - Either sends (≥85%) or holds back (<85%)
4. Logs all interactions to `whatsapp_interactions.json`

## File Structure

```
whatsapp-auto-reply/
├── main.py                      # CLI interface
├── advanced_engine.py           # AI text generation
├── whatsapp_integration.py      # WhatsApp Web automation
├── message_model.json           # Trained model (auto-created)
├── whatsapp_interactions.json   # Interaction log (auto-created)
├── messages.json                # Your training data
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker orchestration
└── README.md                    # This file
```

## Configuration

### Adjust Confidence Threshold

Edit `whatsapp_integration.py`:
```python
bot.monitor_and_reply(engine, check_interval=15)  # Change check_interval
```

### Add Contact Whitelist/Blacklist

Edit `whatsapp_integration.py` in `monitor_and_reply()`:
```python
whitelist = ["Mom", "John", "Sarah"]
if contact not in whitelist:
    continue
```

### Customize Check Interval

```bash
# Check for new messages every 15 seconds (default)
python3 main.py whatsapp

# Check every 30 seconds (less resource intensive)
# Edit check_interval=30 in main.py
```

## Troubleshooting

### "No Chrome found"
```bash
# Install Chromium
sudo apt-get install chromium-browser

# Or use Docker
docker-compose up --build
```

### "QR code not scanning"
- Manually click on the WhatsApp Web window
- Use a recent version of Chrome/Chromium
- Try without `--headless` flag for better debugging

### "Messages generated are weird"
- **Solution**: Train on more messages (50+ minimum)
- Quality scales with data: more messages = better replies
- Avoid very short messages in training data

### "Confidence always too low"
- **Cause**: Training data is too diverse or small
- **Solution**: 
  - Add 50+ more messages
  - Remove unrelated messages
  - Check message quality in JSON

### Browser keeps closing
- Keep the terminal window active while monitoring
- Don't close the Chrome browser manually
- Use Ctrl+C to gracefully stop

## Security & Privacy

⚠️ **Important Warnings**

1. **WhatsApp Terms of Service**: Auto-replying violates WhatsApp ToS. Use at your own risk.

2. **Message Privacy**: Your messages are stored locally in:
   - `message_model.json` - Your learned style model
   - `whatsapp_interactions.json` - Interaction history
   
   Keep these files private.

3. **Browser Access**: The system has full access to your WhatsApp account via browser automation.

4. **Approval System**: Always keep manual approval enabled until you're confident in quality.

## Advanced Usage

### Training on Multiple Contacts

```bash
# Train on messages from specific contact
python3 main.py train "John_messages.json"

# This learns John's style specifically
# Then customize for John's conversations

# To handle multiple contacts:
# - Train on combined messages
# - System will learn common patterns
```

### Improving Reply Quality

1. **Add more training data** (100+ messages)
   ```bash
   python3 main.py train large_export.json
   ```

2. **Use only good messages** in training
   - Remove duplicates
   - Remove very short replies
   - Remove auto-replies or copy-pastes

3. **Check statistics regularly**
   ```bash
   python3 main.py stats
   ```

4. **Adjust confidence threshold** in code (advanced)
   - Lower threshold = more replies sent (riskier)
   - Higher threshold = fewer replies (safer but less active)

### Batch Process Multiple Contacts

```bash
# Create contact-specific models
python3 main.py train mom_messages.json
mv message_model.json mom_model.json

python3 main.py train john_messages.json
mv message_model.json john_model.json

# Then use appropriate model per contact
# (Requires code modification)
```

## Examples

### Example 1: Lazy Replier

```bash
# Collect your messages
# Generate model
python3 main.py train messages.json

# Test it out
python3 main.py test

# Connect with approval
python3 main.py whatsapp
```

### Example 2: Fully Automated

```bash
# After confident training:
python3 main.py whatsapp --no-approval
```

Monitor logs:
```bash
# In another terminal
watch -n 5 python3 main.py stats
```

### Example 3: Docker Deployment

```bash
docker-compose up --build
docker-compose exec auto-reply python3 main.py train messages.json
docker-compose exec auto-reply python3 main.py whatsapp
```

## Performance

- **Training**: 50 messages → 2-5 seconds
- **Reply Generation**: ~100-200ms per message
- **WhatsApp Check**: Every 15 seconds (adjustable)
- **Memory**: ~50-100MB with 100+ messages

## Limitations

- Requires messages in English (can be adapted)
- Best with 50+ training messages (fewer = lower quality)
- Cannot detect images/media (skips automatically)
- Cannot detect message intent (question vs statement)
- May struggle with sarcasm or context-dependent replies

## Future Improvements

- [ ] Sentiment analysis for emotional replies
- [ ] Question detection and handling
- [ ] Multi-language support
- [ ] Contact-specific models
- [ ] Real WhatsApp API (instead of Web automation)
- [ ] Neural network model (instead of Markov)
- [ ] Message scheduling
- [ ] Reply timing (match your response speed)
- [ ] Reaction emoji detection

## Contributing

Found bugs or have ideas? Create an issue or PR.

## License

MIT - Use at your own risk

## Disclaimer

This tool is for educational purposes. Use responsibly. WhatsApp may ban accounts using automation. Senders should be aware you're using auto-reply. Always verify conversations are appropriate before enabling full automation.

---

**Questions?** Check the logs: `whatsapp_interactions.json`

**Want to debug?** Run: `python3 main.py test` to see generated replies

**Need to pause?** Just press Ctrl+C. No messages will be sent without your action.
