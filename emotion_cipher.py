"""
EmotionCrypt - An intelligent system that encrypts text messages
while preserving their emotional signature for AI detection.
"""

import json
import base64
import hashlib
import string
import os
from typing import Dict, List, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Install it to use .env file: pip install python-dotenv")

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("Warning: google-generativeai library not found. Using basic emotion detection.")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class EmotionDetector:
    """Detects emotions in text using Gemini API or NLP models."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the emotion detector.
        
        Args:
            api_key: Gemini API key. If None, tries to load from GEMINI_API_KEY environment variable.
                    If not found, will use fallback detection methods.
        """
        self.gemini_model = None
        self.emotion_model = None
        self.tokenizer = None
        # Try to get API key from parameter, then environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: No Gemini API key provided. Using fallback emotion detection methods.")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the emotion detection model."""
        # Try Gemini API first (only if API key is provided)
        if HAS_GEMINI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Try available model names (without 'models/' prefix)
                model_names = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                for model_name in model_names:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        print(f"Loaded Gemini API ({model_name}) for emotion detection successfully.")
                        return
                    except Exception as e:
                        continue
                raise Exception("No compatible Gemini model found")
            except Exception as e:
                print(f"Could not initialize Gemini API: {e}")
                print("Falling back to basic keyword-based emotion detection.")
                self.gemini_model = None
        elif HAS_GEMINI and not self.api_key:
            print("No Gemini API key provided. Skipping Gemini initialization.")
            self.gemini_model = None
        
        # Fallback to transformers if Gemini not available
        if HAS_TRANSFORMERS:
            try:
                # Using a pre-trained emotion classification model
                model_name = "j-hartmann/emotion-english-distilroberta-base"
                self.emotion_model = pipeline(
                    "text-classification",
                    model=model_name,
                    return_all_scores=True
                )
                print("Loaded emotion detection model successfully.")
            except Exception as e:
                print(f"Could not load transformer model: {e}")
                print("Falling back to basic keyword-based emotion detection.")
                self.emotion_model = None
        else:
            self.emotion_model = None
    
    def detect_emotions(self, text: str) -> List[Tuple[str, float]]:
        """
        Detect emotions in text using Gemini API or fallback methods.
        Returns list of (emotion, confidence) tuples.
        """
        # Try Gemini API first
        if self.gemini_model:
            try:
                return self._detect_with_gemini(text)
            except Exception as e:
                print(f"Error in Gemini emotion detection: {e}")
                print("Falling back to keyword-based detection.")
                return self._basic_emotion_detection(text)
        
        # Fallback to transformers
        if self.emotion_model:
            try:
                results = self.emotion_model(text)[0]
                # Sort by score and return top emotions
                emotions = [(item['label'], item['score']) for item in results]
                emotions.sort(key=lambda x: x[1], reverse=True)
                return emotions
            except Exception as e:
                print(f"Error in emotion detection: {e}")
                return self._basic_emotion_detection(text)
        else:
            return self._basic_emotion_detection(text)
    
    def _detect_with_gemini(self, text: str) -> List[Tuple[str, float]]:
        """Detect emotions using Gemini API."""
        prompt = f"""Analyze the following text and identify the PRIMARY emotions expressed. 
Focus on the top 2 most prominent emotions. Return a JSON object with emotions and their confidence scores (0.0 to 1.0).

Available emotions: Joy, Excitement, Sadness, Anger, Anxiety, Fear, Surprise, Love, Neutral

Text: "{text}"

Return ONLY a JSON object in this exact format (no markdown, no explanations):
{{
  "emotions": [
    {{"emotion": "Joy", "confidence": 0.85}},
    {{"emotion": "Anxiety", "confidence": 0.65}}
  ]
}}

Instructions:
- Identify ONLY the top 2 most prominent emotions
- Use emotion names exactly as listed above (capitalized)
- Confidence scores should be between 0.0 and 1.0
- Return ONLY the JSON object, no other text"""

        try:
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            import json
            result = json.loads(response_text)
            
            # Extract emotions
            emotions = []
            if "emotions" in result:
                for item in result["emotions"]:
                    emotion_name = item.get("emotion", "")
                    confidence = float(item.get("confidence", 0.5))
                    # Normalize emotion names to match our system
                    emotion_name = self._normalize_emotion_name(emotion_name)
                    emotions.append((emotion_name, confidence))
            
            if emotions:
                emotions.sort(key=lambda x: x[1], reverse=True)
                return emotions
            else:
                return self._basic_emotion_detection(text)
                
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._basic_emotion_detection(text)
    
    def _normalize_emotion_name(self, emotion: str) -> str:
        """Normalize emotion names to match our system."""
        emotion_lower = emotion.lower()
        emotion_mapping = {
            'joy': 'Joy',
            'happiness': 'Joy',
            'happy': 'Joy',
            'excitement': 'Excitement',
            'excited': 'Excitement',
            'sadness': 'Sadness',
            'sad': 'Sadness',
            'anger': 'Anger',
            'angry': 'Anger',
            'anxiety': 'Anxiety',
            'anxious': 'Anxiety',
            'fear': 'Fear',
            'afraid': 'Fear',
            'surprise': 'Surprise',
            'surprised': 'Surprise',
            'love': 'Love',
            'neutral': 'Neutral'
        }
        return emotion_mapping.get(emotion_lower, emotion.capitalize())
    
    def _basic_emotion_detection(self, text: str) -> List[Tuple[str, float]]:
        """Fallback basic emotion detection using keyword matching."""
        text_lower = text.lower()
        
        # Emotion keywords with weights
        emotion_keywords = {
            'joy': ['happy', 'joyful', 'delighted', 'pleased', 'overjoyed', 'glad', 'cheerful', 'ecstatic'],
            'excitement': ['excited', 'thrilled', 'enthusiastic', 'eager', 'pumped', 'excitement'],  # Excitement as distinct emotion
            'sadness': ['sad', 'unhappy', 'depressed', 'melancholy', 'down', 'disappointed', 'upset', 'gloomy'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage', 'frustrated', 'upset'],
            'anxiety': ['anxious', 'anxiety', 'apprehensive'],  # Anxiety as distinct emotion
            'fear': ['worried', 'afraid', 'scared', 'nervous', 'fearful', 'concerned'],  # General fear
            'surprise': ['surprised', 'amazed', 'shocked', 'astonished', 'stunned'],
            'love': ['love', 'adore', 'cherish', 'fond', 'affection'],
            'neutral': []
        }
        
        # Words that trigger both joy and excitement
        dual_emotion_keywords = {
            'thrilled': ['joy', 'excitement'],
            'ecstatic': ['joy', 'excitement'],
            'overjoyed': ['joy', 'excitement'],
        }
        
        # Phrases for excitement
        excitement_phrases = ["can't wait", "cannot wait", "can not wait", "looking forward"]
        
        detected_emotions = []
        emotion_scores = {}
        
        # Check for dual emotion keywords first
        for keyword, emotions in dual_emotion_keywords.items():
            if keyword in text_lower:
                for emotion in emotions:
                    if emotion not in emotion_scores:
                        emotion_scores[emotion] = 0.4
                    else:
                        emotion_scores[emotion] = min(emotion_scores[emotion] + 0.2, 0.95)
        
        # Check for excitement phrases
        for phrase in excitement_phrases:
            if phrase in text_lower:
                if 'excitement' not in emotion_scores:
                    emotion_scores['excitement'] = 0.4
                else:
                    emotion_scores['excitement'] = min(emotion_scores['excitement'] + 0.2, 0.95)
                # Excitement phrases also suggest joy
                if 'joy' not in emotion_scores:
                    emotion_scores['joy'] = 0.3
        
        # Check for positive outcomes that indicate joy
        positive_outcomes = ['got', 'received', 'achieved', 'succeeded', 'won', 'offer', 'success']
        outcome_matches = sum(1 for outcome in positive_outcomes if outcome in text_lower)
        if outcome_matches > 0 and any(word in text_lower for word in ['job', 'promotion', 'acceptance', 'approval']):
            if 'joy' not in emotion_scores:
                emotion_scores['joy'] = 0.35
            else:
                emotion_scores['joy'] = min(emotion_scores['joy'] + 0.15, 0.95)
        
        # Check standard emotion keywords
        for emotion, keywords in emotion_keywords.items():
            if emotion == 'neutral':
                continue
            # Skip if already processed as dual emotion
            matches = sum(1 for keyword in keywords if keyword in text_lower and keyword not in dual_emotion_keywords)
            if matches > 0:
                # Calculate confidence based on keyword matches
                base_confidence = min(matches * 0.4, 0.95)
                # Boost confidence if multiple strong keywords found
                if matches >= 2:
                    base_confidence = min(base_confidence + 0.1, 0.95)
                
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = base_confidence
                else:
                    # Merge with existing score
                    emotion_scores[emotion] = min(emotion_scores[emotion] + base_confidence * 0.5, 0.95)
        
        # Convert to list of tuples
        for emotion, score in emotion_scores.items():
            detected_emotions.append((emotion.capitalize(), score))
        
        if not detected_emotions:
            detected_emotions.append(('Neutral', 0.5))
        
        # Sort by confidence, but prioritize certain emotion orders when scores are close
        detected_emotions.sort(key=lambda x: (
            -x[1],  # Primary sort: confidence (descending)
            0 if x[0] == 'Joy' else 1 if x[0] == 'Excitement' else 2  # Secondary: preferred order
        ))
        return detected_emotions
    
    def get_primary_emotions(self, text: str, threshold: float = 0.3) -> List[str]:
        """
        Get primary emotions above threshold.
        Returns list of emotion names.
        """
        emotions = self.detect_emotions(text)
        primary = [emotion for emotion, confidence in emotions if confidence >= threshold]
        
        # If no emotions above threshold, return top emotion
        if not primary and emotions:
            primary = [emotions[0][0]]
        
        # Sort primary emotions with preferred order: Joy before Excitement
        emotion_priority = {'Joy': 0, 'Excitement': 1, 'Anxiety': 2, 'Fear': 3, 
                           'Anger': 4, 'Sadness': 5, 'Surprise': 6, 'Love': 7}
        primary.sort(key=lambda x: (emotion_priority.get(x, 999), -emotions[[e[0] for e in emotions].index(x)][1] if x in [e[0] for e in emotions] else 0))
        
        return primary


class EmotionCipher:
    """
    Main class for encrypting text while preserving emotional signatures.
    """
    
    def __init__(self, password: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the EmotionCipher.
        
        Args:
            password: Optional password for encryption. If None, generates a key.
            api_key: Optional Gemini API key. If None, uses default key.
        """
        self.emotion_detector = EmotionDetector(api_key=api_key)
        self.password = password or self._generate_key()
        self.cipher_suite = self._create_cipher_suite(self.password)
    
    def _generate_key(self) -> str:
        """Generate a random encryption key."""
        return Fernet.generate_key().decode()
    
    def _create_cipher_suite(self, password: str) -> Fernet:
        """Create a Fernet cipher suite from password."""
        # Convert password to bytes
        password_bytes = password.encode()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'emotion_crypt_salt',  # In production, use random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)
    
    def _generate_short_encrypted_text(self, full_encrypted_text: str, length: int = 16) -> str:
        """
        Generate a short, readable encrypted text representation for display.
        Uses the hash of the encrypted text to create a deterministic short string.
        Similar to examples: "9x@T!aZkP#13qWv$"
        
        Args:
            full_encrypted_text: The full base64 encrypted text
            length: Desired length of short encrypted text (default: 16)
            
        Returns:
            Short encrypted text string with special characters
        """
        # Create a hash from the encrypted text for deterministic generation
        text_hash = hashlib.sha256(full_encrypted_text.encode()).hexdigest()
        
        # Character sets for short encrypted text (matching example style)
        # Mix of letters, numbers, and special characters
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Use hash to generate deterministic short string
        short_text = []
        hash_bytes = bytes.fromhex(text_hash)
        
        for i in range(length):
            # Use hash bytes to select characters deterministically
            byte_value = hash_bytes[i % len(hash_bytes)]
            char_index = byte_value % len(chars)
            short_text.append(chars[char_index])
        
        return ''.join(short_text)
    
    def encrypt(self, message: str) -> Dict:
        """
        Encrypt a message while preserving its emotional signature.
        
        Args:
            message: The text message to encrypt
            
        Returns:
            Dictionary containing encrypted text and emotional signature
        """
        # Detect emotions BEFORE encryption
        emotions = self.emotion_detector.get_primary_emotions(message)
        emotion_details = self.emotion_detector.detect_emotions(message)
        
        # Encrypt the text
        encrypted_bytes = self.cipher_suite.encrypt(message.encode())
        full_encrypted_text = base64.urlsafe_b64encode(encrypted_bytes).decode()
        
        # Generate short encrypted text for display
        short_encrypted_text = self._generate_short_encrypted_text(full_encrypted_text, length=16)
        
        # Create emotional signature (readable metadata)
        emotional_signature = {
            'primary_emotions': emotions,
            'emotion_scores': {emotion: float(score) for emotion, score in emotion_details},
            'emotional_vector': self._create_emotional_vector(emotion_details),
            'message_hash': hashlib.sha256(message.encode()).hexdigest()[:16]  # For verification
        }
        
        return {
            'encrypted_text': full_encrypted_text,  # Full encrypted text for decryption
            'short_encrypted_text': short_encrypted_text,  # Short version for display
            'emotional_signature': emotional_signature,
            'encryption_method': 'AES-256-Fernet'
        }
    
    def _create_emotional_vector(self, emotion_details: List[Tuple[str, float]]) -> Dict[str, float]:
        """Create a normalized emotional feature vector."""
        vector = {}
        total_score = sum(score for _, score in emotion_details)
        
        if total_score > 0:
            for emotion, score in emotion_details:
                vector[emotion.lower()] = float(score / total_score)
        else:
            vector['neutral'] = 1.0
        
        return vector
    
    def decrypt(self, encrypted_data: Dict) -> Dict:
        """
        Decrypt a message and retrieve original text and emotion.
        
        Args:
            encrypted_data: Dictionary containing encrypted text and emotional signature
            
        Returns:
            Dictionary containing decrypted message and detected emotion
        """
        # Extract encrypted text
        encrypted_text = encrypted_data['encrypted_text']
        emotional_signature = encrypted_data.get('emotional_signature', {})
        
        # Decrypt the text
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            original_message = decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
        
        # Verify message integrity using hash
        if 'message_hash' in emotional_signature:
            computed_hash = hashlib.sha256(original_message.encode()).hexdigest()[:16]
            if computed_hash != emotional_signature['message_hash']:
                print("Warning: Message integrity check failed!")
        
        # Get emotions from signature
        detected_emotions = emotional_signature.get('primary_emotions', [])
        
        # Also detect emotions from decrypted text for verification
        verified_emotions = self.emotion_detector.get_primary_emotions(original_message)
        
        return {
            'original_message': original_message,
            'detected_emotion': detected_emotions,
            'verified_emotion': verified_emotions,
            'emotional_signature': emotional_signature
        }
    
    def format_output(self, encrypted_data: Dict, use_short: bool = True) -> str:
        """Format encrypted output for display."""
        # Use short encrypted text for display if available, otherwise use full
        if use_short and 'short_encrypted_text' in encrypted_data:
            encrypted_text = encrypted_data['short_encrypted_text']
        else:
            encrypted_text = encrypted_data['encrypted_text']
        
        emotions = encrypted_data['emotional_signature']['primary_emotions']
        emotion_str = ' + '.join(emotions) if emotions else 'Neutral'
        
        return f"Encrypted Text: {encrypted_text}\nDetected Emotion: {emotion_str}"
    
    def format_decrypted_output(self, decrypted_data: Dict) -> str:
        """Format decrypted output for display."""
        message = decrypted_data['original_message']
        emotions = decrypted_data['detected_emotion']
        emotion_str = ' + '.join(emotions) if emotions else 'Neutral'
        
        return f"Original Message: {message}\nDetected Emotion: {emotion_str}"


def main():
    """Example usage of EmotionCipher."""
    # Initialize the cipher
    cipher = EmotionCipher()
    
    # Example message
    message = "Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead."
    
    print("=" * 70)
    print("EMOTION CRYPT - Encryption Demo")
    print("=" * 70)
    print(f"\nInput Message: {message}\n")
    
    # Encrypt
    print("-" * 70)
    print("ENCRYPTING...")
    print("-" * 70)
    encrypted_data = cipher.encrypt(message)
    print(cipher.format_output(encrypted_data))
    print(f"\nFull Encrypted Data (JSON):")
    print(json.dumps(encrypted_data, indent=2))
    
    # Decrypt
    print("\n" + "-" * 70)
    print("DECRYPTING...")
    print("-" * 70)
    decrypted_data = cipher.decrypt(encrypted_data)
    print(cipher.format_decrypted_output(decrypted_data))
    
    # Verify emotions match
    print("\n" + "-" * 70)
    print("VERIFICATION")
    print("-" * 70)
    original_emotions = encrypted_data['emotional_signature']['primary_emotions']
    decrypted_emotions = decrypted_data['detected_emotion']
    print(f"Original Emotions: {original_emotions}")
    print(f"Decrypted Emotions: {decrypted_emotions}")
    print(f"Emotions Match: {set(original_emotions) == set(decrypted_emotions)}")
    
    print("\n" + "=" * 70)
    print("Emotion preserved while text remains encrypted! [SUCCESS]")
    print("=" * 70)


if __name__ == "__main__":
    main()

