# EmotionCrypt 🔐💭

An intelligent encryption system that protects text messages while preserving their emotional signature for AI detection.

**Made by Adit Jain** 🚀

## 🏆 Hackathon Submission

**Project:** Emotion Cipher - Decoding Feelings through Code  
**Event:** Emotion Cipher Hackathon  
**Category:** AI + NLP + Encryption

This project is submitted as part of the Emotion Cipher Hackathon, focusing on creating an intelligent system that can encode and decode human emotions expressed in text messages while maintaining a balance between privacy and empathy.

### 🎥 Project Demonstration

**Screen Recording:** [Upload your screen recording here showing the project running]

**Demo Video Features:**
- System initialization and setup
- Encrypting messages with emotion detection
- Viewing encrypted text and emotional signatures
- Decrypting messages and verifying emotion preservation
- Example use cases and workflows

## Overview

EmotionCrypt is a unique encryption system that:
- **Encrypts** text messages using AES-256 encryption (Fernet)
- **Preserves** emotional signatures as readable metadata
- **Allows** AI systems to detect emotions even from encrypted text
- **Decrypts** messages back to original text with verified emotions

## Key Features

- 🔒 **Strong Encryption**: Uses AES-256 (Fernet) for secure text encryption
- 😊 **Emotion Detection**: Advanced AI-powered emotion classification using Gemini API
- 📊 **Emotional Signatures**: Readable metadata that preserves emotional context
- ✅ **Integrity Verification**: Hash-based message verification
- 🚀 **Easy to Use**: Beautiful Streamlit web interface and simple Python API
- 🎨 **Modern UI**: Intuitive and visually appealing user interface
- 📱 **Web-Based**: No installation needed, run directly in your browser

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Get your API key from: https://makersuite.google.com/app/apikey

3. The system will automatically load the API key from the `.env` file. If no API key is provided, it falls back to keyword-based detection.

## Quick Start

### 🚀 Streamlit Web Application (Recommended)

Run the beautiful web interface:

```bash
streamlit run app.py
```

This will open a web browser with the EmotionCrypt interface where you can:
- 🔒 Encrypt messages with emotion detection
- 🔓 Decrypt encrypted messages
- 📊 View emotion scores and signatures
- 📝 Try example messages
- 💾 Download encrypted data

### 💻 Python API Usage

```python
from emotion_cipher import EmotionCipher

# Initialize the cipher
cipher = EmotionCipher()

# Encrypt a message
message = "Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead."
encrypted_data = cipher.encrypt(message)

# Display encrypted output
print(cipher.format_output(encrypted_data))
# Output:
# Encrypted Text: gAAAAABl...
# Detected Emotion: Joy + Anxiety

# Decrypt the message
decrypted_data = cipher.decrypt(encrypted_data)
print(cipher.format_decrypted_output(decrypted_data))
# Output:
# Original Message: Feeling ecstatic about joining the new AI research team...
# Detected Emotion: Joy + Anxiety
```

### Advanced Usage

```python
from emotion_cipher import EmotionCipher

# Initialize with custom password
cipher = EmotionCipher(password="my-secret-password")

# Encrypt and get full data
encrypted_data = cipher.encrypt(message)
print(encrypted_data)
# Contains:
# - encrypted_text: Encrypted message
# - emotional_signature: Emotional metadata (readable)
#   - primary_emotions: List of detected emotions
#   - emotion_scores: Confidence scores for each emotion
#   - emotional_vector: Normalized emotional feature vector
#   - message_hash: Hash for integrity verification

# Decrypt and verify
decrypted_data = cipher.decrypt(encrypted_data)
print(decrypted_data['original_message'])
print(decrypted_data['detected_emotion'])
print(decrypted_data['emotional_signature'])
```

## How It Works

### Encryption Process

1. **Emotion Detection**: Before encryption, the system detects emotions in the text using NLP models
2. **Text Encryption**: The actual text is encrypted using AES-256 (Fernet)
3. **Signature Creation**: Emotional metadata is stored as readable JSON alongside encrypted text
4. **Output**: Returns encrypted text + emotional signature (readable)

### Decryption Process

1. **Text Decryption**: Encrypted text is decrypted using the same key
2. **Emotion Retrieval**: Emotions are retrieved from the stored signature
3. **Verification**: System verifies message integrity using hash
4. **Output**: Returns original message + detected emotions

### Emotional Signature

The emotional signature is stored as readable metadata:
```json
{
  "primary_emotions": ["Joy", "Fear"],
  "emotion_scores": {
    "Joy": 0.85,
    "Fear": 0.72,
    "Neutral": 0.15
  },
  "emotional_vector": {
    "joy": 0.45,
    "fear": 0.38,
    "neutral": 0.17
  },
  "message_hash": "a1b2c3d4..."
}
```

This signature remains readable even when the text is encrypted, allowing AI systems to understand the emotional context without accessing the actual message.

## Example Output

### Input
```
"Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead."
```

### Encrypted Output
```
Encrypted Text: gAAAAABlXyZ...
Detected Emotion: Joy + Fear
```

### Decrypted Output
```
Original Message: Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead.
Detected Emotion: Joy + Fear
```

## Architecture

- **EmotionDetector**: Handles emotion detection using transformers or keyword matching
- **EmotionCipher**: Main class that handles encryption/decryption and emotion preservation
- **Emotional Signature**: JSON metadata that stores emotional information

## Security Features

- ✅ AES-256 encryption (Fernet)
- ✅ PBKDF2 key derivation
- ✅ Message integrity verification (SHA-256 hash)
- ✅ Secure password-based key generation

## Emotion Detection

The system supports multiple emotion detection methods (in priority order):

1. **Gemini API** (Primary): Uses Google's Gemini AI for advanced emotion detection
2. **Transformers** (Fallback): Uses pre-trained emotion classification models
3. **Basic Mode** (Fallback): Uses keyword-based emotion detection

### Gemini API Integration

The system uses Google's Gemini API for intelligent emotion detection. 

**Setting up your API key:**

1. **Using .env file (Recommended):**
   - Create a `.env` file in the project root
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`
   - The `.env` file is automatically loaded and ignored by git

2. **Using Streamlit UI:**
   - Enter your API key in the sidebar settings
   - This overrides the `.env` file for the current session

3. **Get your API key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy it to your `.env` file or enter it in the UI

```python
from emotion_cipher import EmotionCipher

# Use default API key
cipher = EmotionCipher()

# Or use your own API key
cipher = EmotionCipher(api_key="your-api-key-here")
```

Supported emotions:
- Joy
- Excitement
- Sadness
- Anger
- Anxiety
- Fear
- Surprise
- Love
- Neutral

## Limitations

- Emotional signatures are stored as readable metadata (by design)
- Requires internet connection for Gemini API (falls back to keyword-based detection if unavailable)
- Requires Gemini API key in `.env` file or entered via UI (falls back to keyword-based detection if not provided)
- Emotion detection accuracy depends on the AI model used

## Future Enhancements

- [ ] Support for more emotion categories
- [ ] Multi-language emotion detection
- [ ] Encrypted emotional signatures (optional)
- [ ] Real-time emotion streaming
- [ ] Custom emotion models

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

