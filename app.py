"""
EmotionCrypt - Streamlit Web Application
A beautiful interface for encrypting text while preserving emotional signatures.
"""

import streamlit as st
import json
import os
import time
from emotion_cipher import EmotionCipher

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional, will use environment variables or user input

# Page configuration
st.set_page_config(
    page_title="EmotionCrypt 🔐💭",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern animations and styling (inspired by Awwwards)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.5);
        }
        50% {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.8), 0 0 30px rgba(118, 75, 162, 0.6);
        }
    }
    
    /* Main Header with Animated Gradient */
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #667eea 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite, fadeInUp 1s ease;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
        line-height: 1.2;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        animation: fadeInUp 1s ease 0.2s both;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Animated Emotion Badges */
    .emotion-badge {
        display: inline-block;
        padding: 0.6rem 1.3rem;
        margin: 0.3rem;
        border-radius: 50px;
        font-weight: 600;
        color: white;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease both;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .emotion-badge::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .emotion-badge:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .emotion-badge:hover::before {
        width: 300px;
        height: 300px;
    }
    
    /* Emotion Colors with Gradients */
    .joy { 
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #333;
        animation-delay: 0.1s;
    }
    .excitement { 
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        animation-delay: 0.2s;
    }
    .sadness { 
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        animation-delay: 0.1s;
    }
    .anger { 
        background: linear-gradient(135deg, #FF4757 0%, #FF6B7A 100%);
        animation-delay: 0.2s;
    }
    .anxiety { 
        background: linear-gradient(135deg, #FFA502 0%, #FFB84D 100%);
        color: #333;
        animation-delay: 0.15s;
    }
    .fear { 
        background: linear-gradient(135deg, #747D8C 0%, #95A5A6 100%);
        animation-delay: 0.1s;
    }
    .surprise { 
        background: linear-gradient(135deg, #FF6348 0%, #FF8C69 100%);
        animation-delay: 0.2s;
    }
    .love { 
        background: linear-gradient(135deg, #FF1493 0%, #FF69B4 100%);
        animation-delay: 0.15s;
    }
    .neutral { 
        background: linear-gradient(135deg, #95A5A6 0%, #BDC3C7 100%);
        animation-delay: 0.1s;
    }
    
    /* Glassmorphism Encrypted Box */
    .encrypted-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        margin: 1.5rem 0;
        animation: fadeInUp 0.8s ease, glow 3s ease-in-out infinite;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .encrypted-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Success Box with Animation */
    .success-box {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        animation: slideInRight 0.6s ease;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, rgba(23, 162, 184, 0.1) 0%, rgba(23, 162, 184, 0.05) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        animation: fadeIn 0.6s ease;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
    }
    
    /* Floating Animation for Icons */
    .float-animation {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Pulse Animation */
    .pulse-animation {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Shimmer Effect */
    .shimmer {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }
    
    /* Card Style */
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
    }
    
    /* Gradient Background */
    .gradient-bg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
    }
    
    /* Smooth Transitions */
    * {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Stagger Animation Delays */
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    .stagger-4 { animation-delay: 0.4s; }
    
    /* Loading Spinner */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cipher' not in st.session_state:
    st.session_state.cipher = None
if 'encrypted_data' not in st.session_state:
    st.session_state.encrypted_data = None
if 'decrypted_data' not in st.session_state:
    st.session_state.decrypted_data = None

# Initialize cipher
@st.cache_resource
def get_cipher(api_key=None):
    """Initialize and cache the EmotionCipher instance."""
    return EmotionCipher(api_key=api_key)

# Emotion color mapping
EMOTION_COLORS = {
    'Joy': 'joy',
    'Excitement': 'excitement',
    'Sadness': 'sadness',
    'Anger': 'anger',
    'Anxiety': 'anxiety',
    'Fear': 'fear',
    'Surprise': 'surprise',
    'Love': 'love',
    'Neutral': 'neutral'
}

def get_emotion_badge(emotion):
    """Get HTML badge for emotion."""
    color_class = EMOTION_COLORS.get(emotion, 'neutral')
    return f'<span class="emotion-badge {color_class}">{emotion}</span>'

# Animated Header
st.markdown('<h1 class="main-header">🔐 EmotionCrypt 💭</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Encrypt text while preserving emotions for AI detection</p>', unsafe_allow_html=True)

# Add animated separator
st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); margin: 0 auto; border-radius: 2px; animation: fadeInUp 1s ease 0.4s both;"></div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input - Load from .env file or allow user to override
    default_api_key = os.getenv("GEMINI_API_KEY", "")
    
    if default_api_key:
        # API key loaded from .env file
        st.success("✅ API key loaded from .env file")
        with st.expander("🔑 Override API Key (Optional)"):
            override_key = st.text_input(
                "Gemini API Key",
                value="",
                type="password",
                help="Leave empty to use .env file key, or enter a different key to override",
                key="api_key_override"
            )
            # Use override if provided, otherwise use .env key
            api_key = override_key.strip() if override_key and override_key.strip() else default_api_key
        st.info("💡 Using API key from .env file. Click 'Override API Key' to use a different key.")
    else:
        # No API key in .env, show input field
        api_key = st.text_input(
            "Gemini API Key",
            value="",
            type="password",
            help="Enter your Gemini API key. You can also set it in .env file as GEMINI_API_KEY",
            key="api_key_input"
        )
        api_key = api_key.strip() if api_key else ""
        if not api_key:
            st.warning("⚠️ Please provide a Gemini API key to use AI emotion detection. Without it, the system will use fallback methods.")
            st.info("💡 Tip: Create a `.env` file with `GEMINI_API_KEY=your_key` to auto-load the key.")
    
    # Initialize cipher
    if st.button("🔄 Initialize System", use_container_width=True, type="primary"):
        with st.spinner("Initializing EmotionCrypt..."):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    status_text.text(f"Loading... {i + 1}%")
                    time.sleep(0.01)
                
                # Ensure we use the .env key if no override was provided
                final_api_key = api_key if (api_key and api_key.strip()) else (default_api_key if default_api_key else None)
                st.session_state.cipher = get_cipher(api_key=final_api_key)
                progress_bar.empty()
                status_text.empty()
                st.success("✅ System initialized successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Examples
    st.header("📝 Examples")
    st.markdown("Click any example to load it into the message field:")
    
    example_1 = "Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead."
    example_2 = "I can't believe I failed that test again. I'm so disappointed and frustrated right now."
    example_3 = "Finally got the job offer! I'm thrilled and can't wait to start this new journey."
    
    # Example buttons with better styling
    if st.button("📝 Example 1: Joy + Anxiety", use_container_width=True, type="secondary"):
        st.session_state.example_text = example_1
        st.session_state.example_loaded = True
        st.session_state.example_number = 1
        st.rerun()
    
    if st.button("📝 Example 2: Sadness + Anger", use_container_width=True, type="secondary"):
        st.session_state.example_text = example_2
        st.session_state.example_loaded = True
        st.session_state.example_number = 2
        st.rerun()
    
    if st.button("📝 Example 3: Joy + Excitement", use_container_width=True, type="secondary"):
        st.session_state.example_text = example_3
        st.session_state.example_loaded = True
        st.session_state.example_number = 3
        st.rerun()
    
    # Show which example is currently loaded (if any)
    if st.session_state.get('example_text') and st.session_state.get('example_number'):
        example_num = st.session_state.example_number
        example_names = {1: "Joy + Anxiety", 2: "Sadness + Anger", 3: "Joy + Excitement"}
        st.info(f"📌 Example {example_num} loaded: **{example_names[example_num]}** - Check the Encrypt tab!")
    
    st.divider()
    
    # Info
    st.info("""
    **How it works:**
    1. Enter your message
    2. Click Encrypt
    3. View encrypted text & emotions
    4. Click Decrypt to verify
    """)

# Main content
if st.session_state.cipher is None:
    st.warning("⚠️ Please initialize the system from the sidebar first.")
    st.info("💡 Click '🔄 Initialize System' in the sidebar to get started.")
else:
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔒 Encrypt", "🔓 Decrypt", "ℹ️ About"])
    
    with tab1:
        st.header("Encrypt Your Message")
        
        # Text input - Handle example text properly
        # Check if example text exists in session state
        if 'example_text' in st.session_state and st.session_state.example_text:
            default_message = st.session_state.example_text
            example_just_loaded = st.session_state.get('example_loaded', False)
        else:
            default_message = ""
            example_just_loaded = False
        
        # Create text area - no key to allow dynamic value updates
        message = st.text_area(
            "Enter your message:",
            value=default_message,
            height=150,
            placeholder="Type your message here or select an example from the sidebar...",
            help="The message will be encrypted while emotions are preserved. Try the examples in the sidebar!"
        )
        
        # Show info if example was just loaded
        if example_just_loaded and default_message:
            example_num = st.session_state.get('example_number', '')
            example_names = {1: "Joy + Anxiety", 2: "Sadness + Anger", 3: "Joy + Excitement"}
            example_name = example_names.get(example_num, "Example")
            st.success(f"✅ **Example {example_num} loaded: {example_name}** - You can modify the text above or click Encrypt to proceed.")
            # Clear the loaded flag but keep the text
            st.session_state.example_loaded = False
        
        col1, col2, col3 = st.columns([1.5, 1, 3.5])
        with col1:
            encrypt_button = st.button("🔒 Encrypt", type="primary", use_container_width=True)
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.encrypted_data = None
                st.session_state.decrypted_data = None
                st.session_state.example_text = ''
                if 'example_loaded' in st.session_state:
                    del st.session_state.example_loaded
                if 'example_number' in st.session_state:
                    del st.session_state.example_number
                st.rerun()
        
        if encrypt_button and message:
            # Create a more engaging loading experience
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown("""
                    <div style="text-align: center; padding: 2rem;">
                        <div class="spinner" style="margin: 0 auto;"></div>
                        <p style="margin-top: 1rem; color: #667eea; font-weight: 600;">🔐 Encrypting message and detecting emotions...</p>
                    </div>
                """, unsafe_allow_html=True)
            
            try:
                # Encrypt
                encrypted_data = st.session_state.cipher.encrypt(message)
                st.session_state.encrypted_data = encrypted_data
                st.session_state.decrypted_data = None
                loading_placeholder.empty()
                
                # Clear example text after encryption to prevent reloading
                if 'example_text' in st.session_state:
                    # Keep message but clear example flag
                    st.session_state.example_text = ''
                    if 'example_loaded' in st.session_state:
                        del st.session_state.example_loaded
                    if 'example_number' in st.session_state:
                        del st.session_state.example_number
                
                # Display results with animation
                st.markdown("""
                    <div style="animation: fadeInUp 0.6s ease;">
                """, unsafe_allow_html=True)
                st.success("✅ Message encrypted successfully!")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Detected emotions - Show prominently first with animation
                st.markdown("### 😊 Detected Emotions")
                emotions = encrypted_data['emotional_signature']['primary_emotions']
                emotion_badges = " ".join([get_emotion_badge(emotion) for emotion in emotions])
                st.markdown(
                    f'<div style="margin: 1.5rem 0; font-size: 1.2rem; text-align: center; animation: fadeInUp 0.8s ease;">{emotion_badges}</div>', 
                    unsafe_allow_html=True
                )
                                
                # Show full encrypted text in expander (for technical users)
                with st.expander("🔍 View Full Encrypted Data (for decryption)"):
                    st.markdown("**Full Encrypted Text:**")
                    st.code(encrypted_data['encrypted_text'], language="text")
                    st.info("💡 The full encrypted text is stored in the JSON data and is used for decryption.")
                
                # Emotion scores
                with st.expander("📊 View Emotion Scores"):
                    emotion_scores = encrypted_data['emotional_signature']['emotion_scores']
                    for emotion, score in emotion_scores.items():
                        st.progress(score, text=f"{emotion}: {score:.2f}")
                
                # Copy button
                st.markdown("### 📋 Encrypted Data (JSON)")
                encrypted_json = json.dumps(encrypted_data, indent=2)
                st.code(encrypted_json, language="json")
                st.download_button(
                    label="💾 Download Encrypted Data",
                    data=encrypted_json,
                    file_name="encrypted_message.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"❌ Error: {str(e)}")
        elif encrypt_button and not message:
            st.warning("⚠️ Please enter a message to encrypt.")
    
    with tab2:
        st.header("Decrypt Your Message")
        
        if st.session_state.encrypted_data is None:
            st.info("ℹ️ No encrypted data available. Please encrypt a message first.")
            
            # Manual input option
            st.markdown("### Or paste encrypted data manually:")
            encrypted_input = st.text_area(
                "Paste encrypted JSON data:",
                height=200,
                placeholder='{"encrypted_text": "...", "emotional_signature": {...}}',
                help="Paste the encrypted JSON data here"
            )
            
            if st.button("🔓 Decrypt Manual Input", type="primary"):
                if encrypted_input:
                    try:
                        encrypted_data = json.loads(encrypted_input)
                        st.session_state.encrypted_data = encrypted_data
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON format. Please check your input.")
                else:
                    st.warning("⚠️ Please paste encrypted data.")
        else:
            st.markdown("### 📦 Encrypted Data Available")
            st.success("✅ Ready to decrypt!")
            
            if st.button("🔓 Decrypt", type="primary", use_container_width=True):
                decrypt_placeholder = st.empty()
                with decrypt_placeholder.container():
                    st.markdown("""
                        <div style="text-align: center; padding: 2rem;">
                            <div class="spinner" style="margin: 0 auto;"></div>
                            <p style="margin-top: 1rem; color: #667eea; font-weight: 600;">🔓 Decrypting message...</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                try:
                    decrypted_data = st.session_state.cipher.decrypt(st.session_state.encrypted_data)
                    st.session_state.decrypted_data = decrypted_data
                    decrypt_placeholder.empty()
                    
                    # Display results
                    st.success("✅ Message decrypted successfully!")
                    
                    # Original message with animation
                    st.markdown("### 📝 Original Message")
                    st.markdown(
                        f'<div class="success-box" style="animation: slideInRight 0.8s ease; line-height: 1.8; font-size: 1.1rem;">{decrypted_data["original_message"]}</div>', 
                        unsafe_allow_html=True
                    )
                    
                    # Detected emotions with staggered animation
                    st.markdown("### 😊 Detected Emotions")
                    emotions = decrypted_data['detected_emotion']
                    emotion_badges = " ".join([get_emotion_badge(emotion) for emotion in emotions])
                    st.markdown(
                        f'<div style="margin: 1.5rem 0; font-size: 1.2rem; text-align: center; animation: fadeInUp 0.8s ease 0.2s both;">{emotion_badges}</div>', 
                        unsafe_allow_html=True
                    )
                    
                    # Verification
                    original_emotions = st.session_state.encrypted_data['emotional_signature']['primary_emotions']
                    decrypted_emotions = decrypted_data['detected_emotion']
                    
                    if set(original_emotions) == set(decrypted_emotions):
                        st.markdown("### ✅ Verification")
                        st.success("✅ Emotions preserved correctly!")
                    else:
                        st.warning("⚠️ Emotions differ between encryption and decryption.")
                    
                except Exception as e:
                    decrypt_placeholder.empty()
                    st.error(f"❌ Error: {str(e)}")
            
            # Show encrypted data
            with st.expander("📋 View Encrypted Data"):
                st.json(st.session_state.encrypted_data)
    
    with tab3:
        st.header("About EmotionCrypt")
        
        st.markdown("""
        ### 🔐💭 What is EmotionCrypt?
        
        EmotionCrypt is an intelligent encryption system that protects text messages while preserving 
        their emotional signature for AI detection. It maintains a balance between:
        
        - **🔒 Privacy**: The actual text stays secure through encryption
        - **💭 Empathy**: The emotional meaning is still detectable by AI
        
        ### ✨ Key Features
        
        - **Advanced Encryption**: Uses AES-256 (Fernet) for secure text encryption
        - **AI-Powered Emotion Detection**: Uses Google's Gemini API for accurate emotion detection
        - **Emotional Signatures**: Readable metadata that preserves emotional context
        - **Integrity Verification**: Hash-based message verification
        - **Easy to Use**: Simple and intuitive interface
        
        ### 🎯 How It Works
        
        1. **Encryption**: Your message is encrypted using AES-256 encryption
        2. **Emotion Detection**: Emotions are detected using Gemini AI before encryption
        3. **Signature Creation**: Emotional metadata is stored as readable JSON
        4. **Decryption**: Original message and emotions are retrieved and verified
        
        ### 😊 Supported Emotions
        
        - **Joy** - Happiness and positive feelings
        - **Excitement** - Enthusiasm and anticipation
        - **Sadness** - Sorrow and disappointment
        - **Anger** - Frustration and irritation
        - **Anxiety** - Worry and apprehension
        - **Fear** - Concern and nervousness
        - **Surprise** - Amazement and shock
        - **Love** - Affection and fondness
        - **Neutral** - No strong emotion
        
        ### 🚀 Technology Stack
        
        - **Backend**: Python, Cryptography (Fernet)
        - **AI**: Google Gemini API
        - **Frontend**: Streamlit
        - **Encryption**: AES-256
        
        ### 📝 Examples
        
        Check out the examples in the sidebar to see EmotionCrypt in action!
        
        ### 🔒 Security
        
        - Messages are encrypted using industry-standard AES-256 encryption
        - Emotional signatures are stored as metadata (by design)
        - Message integrity is verified using SHA-256 hashing
        - API keys are handled securely
        
        ### 📚 Learn More
        
        For more information, check out the README.md file in the project repository.
        """)
        
        st.divider()
        
        st.markdown("""
        ### 🎨 Made with ❤️ using Streamlit
        
        **EmotionCrypt** - Where feelings stay readable, but words stay private.
        
        ---
        
        **Made by Adit Jain** 🚀
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "🔐💭 EmotionCrypt - Encrypting text while preserving emotions<br>"
    "<small>Made by <strong>Adit Jain</strong> 🚀</small>"
    "</div>",
    unsafe_allow_html=True
)

