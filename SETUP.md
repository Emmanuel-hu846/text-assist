# WhatsApp Auto-Reply System - Setup Guide

## Installation Steps

### Windows Setup

#### Step 1: Install Python 3.9+
- Download from: https://www.python.org/downloads/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run:
  ```bash
  python --version
  ```

#### Step 2: Install Chrome Browser
- Download from: https://www.google.com/chrome/
- Install normally

#### Step 3: Download ChromeDriver
- Go to: https://chromedriver.chromium.org/
- Download version matching your Chrome version
- Extract `chromedriver.exe` to the project folder (same folder as main.py)
- Or add to PATH

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation
- `scikit-learn` - Machine learning (TF-IDF)
- `numpy` - Numerical computing

#### Step 5: Prepare Your Messages
Export from WhatsApp:
1. Open WhatsApp
2. Find a contact
3. Click More (⋮) → Export chat
4. Choose "Without media"
5. Save as `messages.json` or `chat_export.txt`

Or use the included `sample_messages.json` to test.

### Mac Setup

```bash
# Install Python 3.9+
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11

# Install Chrome
brew install --cask google-chrome

# Install ChromeDriver
brew install chromedriver

# Install dependencies
pip3 install -r requirements.txt
```

### Linux Setup (Ubuntu/Debian)

```bash
# Install Python
sudo apt-get update
sudo apt-get install python3.11 python3-pip

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo apt-get install google-chrome-stable

# Install ChromeDriver
sudo apt-get install chromium-chromedriver

# Install dependencies
pip3 install -r requirements.txt
```

### Docker Setup (All Platforms)

If you have Docker installed:

```bash
# Build image
docker build -t whatsapp-auto-reply .

# Run training
docker run -it -v $(pwd):/app whatsapp-auto-reply python3 main.py train sample_messages.json

# Run WhatsApp bot (requires display)
docker run -it -v $(pwd):/app -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY whatsapp-auto-reply python3 main.py whatsapp
```

## Quick Start After Installation

### 1. Test with Sample Data
```bash
python3 main.py train sample_messages.json
```

Expected output:
```
[*] Loading messages from sample_messages.json...
[+] Loaded 50 messages
[*] Training advanced engine...
[+] Model saved: message_model.json

[*] Test generation (5 samples):
  1. 'yo whats up' [89%] ✓ GOOD
  2. 'im down for that' [91%] ✓ GOOD
  3. 'nah not really' [84%] ⊘ WEAK
  4. 'fr fr no cap' [87%] ✓ GOOD
  5. 'lets goooo' [85%] ✓ GOOD

[+] Ready! Run: python3 main.py whatsapp
```

### 2. Test Generation
```bash
python3 main.py test
```

Output shows 10 generated replies with confidence scores.

### 3. Connect to WhatsApp (Manual Approval)
```bash
python3 main.py whatsapp
```

This will:
- Open Chrome browser
- Show WhatsApp Web
- Ask you to scan QR code
- Monitor messages and ask for approval before sending

### 4. View Statistics
```bash
python3 main.py stats
```

Shows how many messages were sent/rejected and confidence metrics.

## Training with Your Real Messages

### From WhatsApp Export (Recommended)

1. Open WhatsApp on your phone
2. Find a conversation
3. Tap More (⋮) → Export chat → Without media
4. Share to your computer
5. Save as `my_messages.json` or `chat.txt`

Train:
```bash
python3 main.py train my_messages.json
```

### From JSON Format

Create `my_messages.json`:
```json
[
  "hey whats up",
  "im good thanks for asking",
  "nah not really",
  "thats awesome",
  "lets do it",
  "my bad i was busy"
]
```

Train:
```bash
python3 main.py train my_messages.json
```

## Production Use

### With Manual Approval (SAFE - Recommended)

Every reply needs your "y/n" approval:

```bash
python3 main.py whatsapp
```

```
[→] Processing chat: John
  Generated: 'yo whats up bro'
  Confidence: 91.0%
  Send this reply? (y/n): y
[+] Message sent: 'yo whats up bro'
```

### Fully Automatic (RISKY)

Only do this after:
- Training on 100+ messages
- Testing extensively with `python3 main.py test`
- Running with approval mode for 10+ interactions

```bash
python3 main.py whatsapp --no-approval
```

⚠️ WARNING: System will reply automatically without asking!

## Troubleshooting

### "ChromeDriver error"
**Problem**: Can't find ChromeDriver
**Solution**: 
- Make sure chromedriver.exe is in project folder OR
- Add to PATH environment variable OR
- Specify path in code: `webdriver.Chrome('./chromedriver.exe')`

### "ModuleNotFoundError: No module named 'selenium'"
**Problem**: Dependencies not installed
**Solution**: 
```bash
pip install -r requirements.txt
```

### "QR code not loading"
**Problem**: WhatsApp Web times out
**Solution**:
- Check internet connection
- Try again (sometimes WhatsApp is slow)
- Make sure browser window stays open

### "Generated messages are bad"
**Problem**: Training data quality
**Solution**:
- Add more messages (50+ minimum, 100+ recommended)
- Remove very short messages
- Remove duplicates
- Use `python3 main.py test` to check quality

### "Permission denied on Linux"
**Problem**: Can't execute chromedriver
**Solution**:
```bash
sudo chmod +x /usr/bin/chromedriver
```

### "Chrome crashes on startup"
**Problem**: Incompatible Chrome/ChromeDriver versions
**Solution**:
- Check Chrome version: Chrome menu → About Chrome
- Download matching ChromeDriver from: https://chromedriver.chromium.org/
- Replace the chromedriver file

## File Breakdown

| File | Purpose |
|------|---------|
| `main.py` | Main CLI interface |
| `advanced_engine.py` | AI text generation (Markov + TF-IDF) |
| `whatsapp_integration.py` | WhatsApp Web automation (Selenium) |
| `message_model.json` | Your trained AI model (created after training) |
| `whatsapp_interactions.json` | Log of all interactions (created after first use) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker image definition |
| `docker-compose.yml` | Docker orchestration |

## Understanding the System

### How Training Works
```
Your Messages (50+)
        ↓
    Clean & Filter
        ↓
    Build Markov Chain (word sequences)
    Build TF-IDF vectors (similarity)
        ↓
    Save to message_model.json
```

### How Generation Works
```
Generate candidate replies (5-10)
        ↓
Score each with 3 factors:
  - Token match (do words match your vocab?)
  - Similarity (how close to your style?)
  - Length (is it 3-15 words?)
        ↓
Pick best reply
        ↓
Return with confidence score
```

### How WhatsApp Monitoring Works
```
Every 15 seconds:
  1. Check for unread messages
  2. Open each chat
  3. Get last 5 messages for context
  4. Generate reply
  5. Score confidence
  6. Ask user for approval (if enabled)
  7. Send if approved & confidence ≥85%
  8. Log to whatsapp_interactions.json
```

## Advanced Tips

### Increase Check Frequency
Edit `main.py` line with `check_interval`:
```python
bot.monitor_and_reply(engine, check_interval=5)  # Check every 5s instead of 15s
```

### Whitelist Specific Contacts
Edit `whatsapp_integration.py` in `monitor_and_reply()`:
```python
WHITELIST = ["Mom", "John", "Sarah"]

for chat_info in unread:
    contact = chat_info["contact"]
    if contact not in WHITELIST:
        logger.info(f"[⊘] Skipping {contact} (not whitelisted)")
        continue
```

### Adjust Confidence Threshold
Edit `main.py` (line with auto-reply logic):
```python
should_send = confidence >= 0.80  # Lower threshold = more aggressive
```

### Run in Background (Linux/Mac)
```bash
nohup python3 main.py whatsapp &
```

Monitor later:
```bash
python3 main.py stats
```

### Run with Systemd (Linux)
Create `/etc/systemd/system/whatsapp-reply.service`:
```ini
[Unit]
Description=WhatsApp Auto-Reply
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/main.py whatsapp
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable whatsapp-reply
sudo systemctl start whatsapp-reply
```

## Security Best Practices

1. **Keep Keys Private**: Don't share `message_model.json` - it contains your learned style
2. **Backup**: Save `message_model.json` regularly
3. **Manual Approval**: Always use manual approval mode initially
4. **Monitor Logs**: Check `whatsapp_interactions.json` for unexpected behavior
5. **Test First**: Use `python3 main.py test` before full automation
6. **Set Limits**: Use whitelist to control which contacts get auto-replies

## Performance Notes

| Task | Time |
|------|------|
| Train (100 messages) | 2-3 seconds |
| Generate reply | 100-200ms |
| WhatsApp check | ~1-2 seconds |
| Message send | 1-3 seconds |

Memory usage: 50-100MB

## What's Happening Behind the Scenes

### Text Generation Algorithm
1. Uses **Markov chains** to learn word sequences
2. Uses **TF-IDF** to find similar messages
3. Generates multiple candidates
4. Scores each with 3 factors (40% + 40% + 20% = 100%)
5. Returns highest scoring reply

### Confidence Scoring
- **Token Match (40%)**: Do the words appear in your training data?
- **Similarity (40%)**: How similar is it to actual messages you sent?
- **Length (20%)**: Is it a reasonable length (3-15 words)?

Final score is weighted average of these three.

### Why It Works
- Learns from 100s of your real messages
- Uses multiple scoring methods (not just random)
- Has safety threshold (85% minimum)
- Requires manual approval initially
- Logs everything for debugging

## Support

If something breaks:
1. Check error message in console
2. Run `python3 main.py test` to verify setup
3. Check `whatsapp_interactions.json` for logs
4. Review README.md troubleshooting section
5. Try with sample_messages.json first

## Next Steps

1. ✅ Install dependencies
2. ✅ Test with sample_messages.json
3. ✅ Export your real WhatsApp messages
4. ✅ Train model: `python3 main.py train your_messages.json`
5. ✅ Test generation: `python3 main.py test`
6. ✅ Start with approval: `python3 main.py whatsapp`
7. ✅ Monitor stats: `python3 main.py stats`
8. ✅ Gradually add more contacts
9. ✅ Only then consider `--no-approval` mode

Good luck! 🚀
