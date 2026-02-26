import streamlit as st
import os
from pathlib import Path
import tempfile
from api_models import transcribe_audio, generate_notes, extract_keywords
from formatter import format_notes, extract_sections
import traceback
import time

# Page configuration
st.set_page_config(
    page_title="LectureAI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Glassmorphism Theme with Coral/Orange
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animated gradient background */
    .main {
        background: linear-gradient(135deg, #FFF9F0 0%, #FFE8D6 50%, #FFD7C4 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding: 1.5rem 2rem;
        max-width: 1600px;
    }
    
    /* Glassmorphism Header */
    .glass-header {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 2.5rem 3rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(255, 107, 107, 0.15);
    }
    
    .app-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E72 50%, #FF8C42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.03em;
    }
    
    .app-subtitle {
        font-size: 1.15rem;
        color: #2D3436;
        margin-top: 0.75rem;
        font-weight: 400;
        opacity: 0.85;
    }
    
    /* Glass Upload Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 3rem;
        margin: 2rem auto;
        max-width: 900px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .glass-card h3 {
        color: #2D3436;
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* File uploader - glassmorphism style */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 2px dashed #FF8E72;
        border-radius: 16px;
        padding: 3rem 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: rgba(255, 255, 255, 0.5);
        border-color: #FF6B6B;
        transform: translateY(-2px);
    }
    
    [data-testid="stFileUploader"] label {
        color: #2D3436 !important;
        font-weight: 500;
        font-size: 1.05rem;
    }
    
    /* Buttons with gradient */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8C42 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 3rem;
        font-size: 1.15rem;
        font-weight: 600;
        width: 100%;
        max-width: 400px;
        margin: 2rem auto;
        display: block;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.35);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(255, 107, 107, 0.45);
    }
    
    /* Info cards with glass effect */
    .info-glass {
        background: rgba(255, 235, 205, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-left: 4px solid #FF8C42;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #2D3436;
        border: 1px solid rgba(255, 140, 66, 0.2);
    }
    
    .success-glass {
        background: rgba(200, 255, 200, 0.4);
        backdrop-filter: blur(10px);
        border-left: 4px solid #51CF66;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #2D3436;
        border: 1px solid rgba(81, 207, 102, 0.2);
    }
    
    .error-glass {
        background: rgba(255, 200, 200, 0.4);
        backdrop-filter: blur(10px);
        border-left: 4px solid #FF6B6B;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #2D3436;
        border: 1px solid rgba(255, 107, 107, 0.2);
    }
    
    /* Results page header */
    .results-glass-header {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .results-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8C42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    /* Sidebar glass cards */
    .sidebar-glass {
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .sidebar-title {
        color: #2D3436;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Keyword badges with glass effect */
    .keyword-badge {
        display: inline-block;
        background: rgba(255, 107, 107, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 107, 107, 0.3);
        color: #FF6B6B;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .keyword-badge-alt {
        background: rgba(255, 140, 66, 0.15);
        border: 1px solid rgba(255, 140, 66, 0.3);
        color: #FF8C42;
    }
    
    /* Topic cards with glass */
    .topic-glass {
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .topic-header {
        color: #2D3436;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #FF8E72;
    }
    
    .theory-glass {
        background: rgba(255, 235, 220, 0.5);
        backdrop-filter: blur(10px);
        border-left: 4px solid #FF6B6B;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 107, 107, 0.2);
    }
    
    .example-glass {
        background: rgba(255, 245, 230, 0.5);
        backdrop-filter: blur(10px);
        border-left: 4px solid #FF8C42;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-style: italic;
        border: 1px solid rgba(255, 140, 66, 0.2);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: rgba(81, 207, 102, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(81, 207, 102, 0.3);
        color: #2D3436;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(81, 207, 102, 0.3);
        transform: translateY(-2px);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8C42 100%);
        border-radius: 10px;
    }
    
    /* Stats boxes */
    .stat-glass {
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-glass:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.95rem;
        color: #2D3436;
        font-weight: 500;
    }
    
    /* Back button */
    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        color: #2D3436;
        border: 1px solid rgba(255, 107, 107, 0.3);
        box-shadow: none;
    }
    
    /* Text area (transcript) */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 140, 66, 0.2);
        border-radius: 12px;
        color: #2D3436;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        color: #2D3436;
        font-weight: 500;
    }
    
    /* Responsive - Laptop friendly */
    @media (min-width: 1024px) {
        .block-container {
            padding: 2rem 4rem;
        }
        
        .glass-card {
            max-width: 1000px;
        }
    }
    
    @media (max-width: 768px) {
        .app-title {
            font-size: 2.5rem;
        }
        
        .glass-card {
            padding: 2rem 1.5rem;
        }
        
        .stButton > button {
            padding: 0.9rem 2rem;
            font-size: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state"""
    defaults = {
        'page': 'upload',
        'transcript': None,
        'notes': None,
        'keywords': [],
        'processing': False,
        'file_info': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def validate_api_keys():
    """Validate API keys"""
    required_keys = {
        'ASSEMBLYAI_API_KEY': 'AssemblyAI',
        'GROQ_API_KEY': 'Groq'
    }
    
    missing_keys = []
    for key, name in required_keys.items():
        try:
            if key in st.secrets:
                continue
        except:
            pass
        
        if os.getenv(key):
            continue
        
        missing_keys.append(name)
    
    return missing_keys

def process_audio_file(file_path, filename):
    """Process audio and redirect to results"""
    try:
        progress_bar = st.progress(0)
        status = st.empty()
        
        # Transcription
        status.info("🎙️ Transcribing audio...")
        progress_bar.progress(30)
        
        transcript = transcribe_audio(file_path)
        
        if not transcript or len(transcript.strip()) < 50:
            st.error("⚠️ Transcription failed or insufficient content.")
            return False
        
        st.session_state.transcript = transcript
        progress_bar.progress(60)
        
        # Extract keywords
        status.info("🔍 Extracting key concepts...")
        progress_bar.progress(70)
        keywords = extract_keywords(transcript, max_keywords=8)
        st.session_state.keywords = keywords
        
        # Generate notes
        status.info("🤖 Generating structured notes...")
        progress_bar.progress(85)
        
        notes = generate_notes(transcript)
        
        if not notes:
            st.error("⚠️ Note generation failed.")
            return False
        
        st.session_state.notes = notes
        
        # Store file info
        st.session_state.file_info = {
            'name': filename,
            'word_count': len(transcript.split()),
            'char_count': len(transcript)
        }
        
        progress_bar.progress(100)
        status.success("✅ Notes generated successfully!")
        
        time.sleep(1)
        
        # Redirect to results
        st.session_state.page = 'results'
        st.rerun()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        with st.expander("View detailed error"):
            st.code(traceback.format_exc())
        return False

def upload_page():
    """Upload page with glassmorphism"""
    
    # Header
    st.markdown("""
        <div class="glass-header">
            <h1 class="app-title">LectureAI</h1>
            <p class="app-subtitle">Transform lectures into structured notes with AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check API keys
    missing_keys = validate_api_keys()
    if missing_keys:
        st.markdown(f'''
            <div class="error-glass">
                <strong>⚠️ Missing API Keys:</strong> {', '.join(missing_keys)}<br>
                Add them in <strong>Settings → Secrets</strong> on Streamlit Cloud
            </div>
        ''', unsafe_allow_html=True)
        with st.expander("📖 Setup guide"):
            st.code("""
ASSEMBLYAI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
            """)
        return
    
    # Upload card
    st.markdown("""
        <div class="glass-card">
            <h3>📁 Upload Your Lecture Audio</h3>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose audio file",
        type=['mp3', 'wav', 'm4a', 'mp4', 'flac', 'ogg'],
        help="MP3, WAV, M4A, MP4, FLAC, OGG",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        file_size = uploaded_file.size / (1024 * 1024)
        st.markdown(f'''
            <div class="success-glass">
                <strong>✅ Ready:</strong> {uploaded_file.name} ({file_size:.2f} MB)
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🚀 Generate Notes"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                process_audio_file(tmp_path, uploaded_file.name)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # Info
    st.markdown("""
        <div class="info-glass">
            <strong>💡 How it works:</strong><br>
            1️⃣ Upload audio → 2️⃣ AI processes → 3️⃣ Get structured notes
        </div>
    """, unsafe_allow_html=True)
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="stat-glass">
                <div class="stat-icon">🎙️</div>
                <div class="stat-label">AI Transcription</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-glass">
                <div class="stat-icon">📝</div>
                <div class="stat-label">Smart Notes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-glass">
                <div class="stat-icon">💾</div>
                <div class="stat-label">Export Options</div>
            </div>
        """, unsafe_allow_html=True)

def results_page():
    """Results page with glassmorphism"""
    
    if not st.session_state.notes:
        st.session_state.page = 'upload'
        st.rerun()
        return
    
    # Header
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("""
            <div class="results-glass-header">
                <div class="results-title">📖 Your Notes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("← Back", key="back_btn", use_container_width=True):
            st.session_state.page = 'upload'
            st.session_state.notes = None
            st.session_state.transcript = None
            st.rerun()
    
    # Layout: Sidebar + Content
    col_side, col_main = st.columns([1, 2.5])
    
    with col_side:
        # Stats
        st.markdown("""
            <div class="sidebar-glass">
                <div class="sidebar-title">📊 Statistics</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.file_info:
            st.markdown(f"""
                <div class="stat-glass">
                    <div class="stat-icon">{st.session_state.file_info.get('word_count', 0):,}</div>
                    <div class="stat-label">Words</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Keywords
        st.markdown("""
            <div class="sidebar-glass">
                <div class="sidebar-title">🏷️ Key Concepts</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.keywords:
            for i, kw in enumerate(st.session_state.keywords):
                badge_class = "keyword-badge-alt" if i % 2 == 0 else "keyword-badge"
                st.markdown(f'<span class="{badge_class}">{kw}</span>', unsafe_allow_html=True)
        
        # Transcript
        st.markdown("""
            <div class="sidebar-glass">
                <div class="sidebar-title">📜 Transcript</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View transcript"):
            st.text_area(
                "Transcript",
                st.session_state.transcript,
                height=250,
                label_visibility="collapsed"
            )
        
        # Downloads
        st.markdown("""
            <div class="sidebar-glass">
                <div class="sidebar-title">💾 Downloads</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            "📥 TXT",
            st.session_state.notes,
            "notes.txt",
            use_container_width=True
        )
        
        formatted = format_notes(st.session_state.notes)
        st.download_button(
            "📥 Markdown",
            formatted,
            "notes.md",
            use_container_width=True
        )
    
    with col_main:
        # Notes
        sections = extract_sections(st.session_state.notes)
        
        for section_title, section_content in sections.items():
            st.markdown(f"""
                <div class="topic-glass">
                    <div class="topic-header">{section_title}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if "Theory:" in section_content or "**Theory:**" in section_content:
                parts = section_content.split("Example:")
                theory = parts[0].replace("Theory:", "").replace("**Theory:**", "").strip()
                
                st.markdown(f'<div class="theory-glass"><strong>💡 Theory:</strong> {theory}</div>', 
                          unsafe_allow_html=True)
                
                if len(parts) > 1:
                    example = parts[1].replace("**Example:**", "").strip()
                    st.markdown(f'<div class="example-glass"><strong>✨ Example:</strong> {example}</div>', 
                              unsafe_allow_html=True)
            else:
                st.markdown(section_content)

def main():
    initialize_session_state()
    
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
