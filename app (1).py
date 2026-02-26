import streamlit as st
import os
from pathlib import Path
import tempfile
from api_models import transcribe_audio, generate_notes, extract_keywords
from formatter import format_notes, extract_sections
import traceback
import time
import base64

# Page configuration
st.set_page_config(
    page_title="LectureAI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, clean CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
        background: white;
        border-radius: 20px;
        margin: 2rem auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 2rem 0 3rem 0;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #f9fafb;
        padding: 0.5rem;
        border-radius: 12px;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 1rem 2rem;
        background-color: transparent;
        border-radius: 8px;
        color: #6b7280;
        font-weight: 500;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f3f4f6;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Info boxes */
    .info-card {
        background: linear-gradient(135deg, #e0e7ff 0%, #ede9fe 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
    }
    
    .error-card {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #ef4444;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
    }
    
    /* Notes display */
    .notes-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .topic-card {
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .topic-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .theory-block {
        background: #eff6ff;
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .example-block {
        background: #fef3c7;
        border-left: 3px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-style: italic;
    }
    
    .keyword-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stDownloadButton > button:hover {
        background: #059669;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'transcript': None,
        'notes': None,
        'keywords': [],
        'processing': False,
        'recorded_audio': None,
        'show_recorder_actions': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def validate_api_keys():
    """Validate required API keys"""
    required_keys = {
        'ASSEMBLYAI_API_KEY': 'AssemblyAI',
        'GROQ_API_KEY': 'Groq'
    }
    
    missing_keys = []
    for key, name in required_keys.items():
        # Check Streamlit secrets first (deployment)
        try:
            if key in st.secrets:
                continue
        except:
            pass
        
        # Check environment variables (local backup)
        if os.getenv(key):
            continue
        
        # Key not found anywhere
        missing_keys.append(name)
    
    return missing_keys

def process_audio_file(file_path, file_type="uploaded"):
    """Process audio file and generate notes"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Transcription
        status_text.info("🎙️ Transcribing audio... This may take a few minutes.")
        progress_bar.progress(20)
        
        transcript = transcribe_audio(file_path)
        
        if not transcript or len(transcript.strip()) < 50:
            st.error("⚠️ Transcription failed or returned insufficient content.")
            return False
        
        st.session_state.transcript = transcript
        progress_bar.progress(60)
        
        # Extract keywords
        status_text.info("🔍 Extracting key concepts...")
        progress_bar.progress(70)
        keywords = extract_keywords(transcript, max_keywords=10)
        st.session_state.keywords = keywords
        
        # Generate notes
        status_text.info("🤖 Analyzing lecture structure... Please wait.")
        progress_bar.progress(80)
        
        notes = generate_notes(transcript)
        
        if not notes:
            st.error("⚠️ Note generation failed. Please try again.")
            return False
        
        st.session_state.notes = notes
        progress_bar.progress(100)
        
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ Notes generated successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        with st.expander("View detailed error"):
            st.code(traceback.format_exc())
        return False

def display_notes():
    """Display generated notes"""
    if not st.session_state.notes:
        return
    
    st.markdown('<div class="section-header">📖 Your Notes</div>', unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2.5, 1])
    
    with col_main:
        st.markdown('<div class="notes-container">', unsafe_allow_html=True)
        
        sections = extract_sections(st.session_state.notes)
        
        for section_title, section_content in sections.items():
            if section_title.lower() == "introduction":
                st.markdown("### 📝 Introduction")
                st.markdown(section_content)
            elif "topic" in section_title.lower() or "technique" in section_title.lower():
                st.markdown(f'''
                <div class="topic-card">
                    <div class="topic-title">{section_title}</div>
                ''', unsafe_allow_html=True)
                
                if "Theory:" in section_content:
                    parts = section_content.split("Example:")
                    theory = parts[0].replace("Theory:", "").strip()
                    st.markdown(f'<div class="theory-block"><strong>💡 Theory:</strong> {theory}</div>', 
                              unsafe_allow_html=True)
                    
                    if len(parts) > 1:
                        example = parts[1].strip()
                        st.markdown(f'<div class="example-block"><strong>✨ Example:</strong> {example}</div>', 
                                  unsafe_allow_html=True)
                else:
                    st.markdown(section_content)
                
                st.markdown('</div>', unsafe_allow_html=True)
            elif section_title.lower() == "conclusion":
                st.markdown("### 🎯 Conclusion")
                st.markdown(section_content)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Notes (TXT)",
                st.session_state.notes,
                "lecture_notes.txt",
                mime="text/plain"
            )
        with col2:
            formatted = format_notes(st.session_state.notes)
            st.download_button(
                "📥 Download Notes (MD)",
                formatted,
                "lecture_notes.md",
                mime="text/markdown"
            )
    
    with col_side:
        st.markdown("### 🏷️ Key Concepts")
        if st.session_state.keywords:
            for kw in st.session_state.keywords:
                st.markdown(f'<span class="keyword-badge">{kw}</span>', unsafe_allow_html=True)
        
        st.markdown("### 📄 Transcript")
        with st.expander("View full transcript", expanded=False):
            st.text_area(
                "Transcript",
                st.session_state.transcript,
                height=300,
                label_visibility="collapsed"
            )

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="header-container">
            <h1 class="main-title">LectureAI</h1>
            <p class="subtitle">Transform lectures into structured notes with AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check API keys
    missing_keys = validate_api_keys()
    if missing_keys:
        st.markdown(f'''
            <div class="error-card">
                <strong>⚠️ Missing API Keys:</strong> {', '.join(missing_keys)}<br><br>
                Configure your keys in <code>.streamlit/secrets.toml</code>
            </div>
        ''', unsafe_allow_html=True)
        with st.expander("📖 Setup Instructions"):
            st.code("""
# Create .streamlit/secrets.toml
ASSEMBLYAI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
            """)
        return
    
    # Main tab - Just Upload (Live Recording doesn't work on Streamlit Cloud)
    st.markdown("### Upload your lecture audio")
    
    st.markdown("""
        <div class="info-card">
            <strong>💡 Tip:</strong> You can record audio on your device first, then upload it here.<br>
            Supported formats: MP3, WAV, M4A, MP4, FLAC, OGG
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'mp4', 'flac', 'ogg'],
        help="Upload a lecture recording"
    )
    
    if uploaded_file:
        st.markdown(f'<div class="success-card">✅ File uploaded: <strong>{uploaded_file.name}</strong></div>', 
                   unsafe_allow_html=True)
        
        if st.button("🚀 Generate Notes"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                success = process_audio_file(tmp_path)
                if success:
                    st.rerun()
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # Display notes if available
    if st.session_state.notes:
        st.markdown("<br><br>", unsafe_allow_html=True)
        display_notes()

if __name__ == "__main__":
    main()
