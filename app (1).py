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

# Navy & Gold Premium Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .main {
        background-color: #fdfcfa;
    }
    
    .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8f 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 58, 95, 0.3);
    }
    
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .app-title .gold {
        color: #d4af37;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Upload Card */
    .upload-card {
        background: white;
        border: 2px solid #e8e6e3;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem auto;
        max-width: 700px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .upload-card h3 {
        color: #1e3a5f;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border: 3px dashed #d4af37;
        border-radius: 12px;
        padding: 2rem;
        background: #fdfcfa;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #1e3a5f;
        background: #f8f7f5;
    }
    
    [data-testid="stFileUploader"] label {
        color: #1e3a5f !important;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8f 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        max-width: 300px;
        margin: 1.5rem auto;
        display: block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 95, 0.4);
        background: linear-gradient(135deg, #2d5a8f 0%, #1e3a5f 100%);
    }
    
    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, #e8f0f7 0%, #f0f4f8 100%);
        border-left: 4px solid #1e3a5f;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        color: #1e3a5f;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        color: #155724;
    }
    
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        color: #721c24;
    }
    
    /* Results page styling */
    .results-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .results-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Sidebar styling */
    .sidebar-card {
        background: white;
        border: 1px solid #e8e6e3;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .sidebar-title {
        color: #1e3a5f;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Keyword badges */
    .keyword-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8f 100%);
        color: white;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .keyword-badge-gold {
        background: linear-gradient(135deg, #d4af37 0%, #f0c75e 100%);
        color: #1e3a5f;
    }
    
    /* Topic cards */
    .topic-card {
        background: white;
        border: 1px solid #e8e6e3;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    
    .topic-header {
        color: #1e3a5f;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 3px solid #d4af37;
        padding-bottom: 0.5rem;
    }
    
    .theory-block {
        background: #e8f0f7;
        border-left: 4px solid #1e3a5f;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .example-block {
        background: #fef5e7;
        border-left: 4px solid #d4af37;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-style: italic;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: #28a745;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        margin: 0.3rem;
    }
    
    .stDownloadButton > button:hover {
        background: #218838;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1e3a5f 0%, #d4af37 100%);
    }
    
    /* Stats */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background: white;
        border: 1px solid #e8e6e3;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .block-container {
            padding: 1rem 0.5rem;
        }
        
        .upload-card {
            padding: 2rem 1rem;
        }
        
        .stButton > button {
            padding: 0.8rem 2rem;
            font-size: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state"""
    defaults = {
        'page': 'upload',  # 'upload' or 'results'
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
        
        # Redirect to results page
        st.session_state.page = 'results'
        st.rerun()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        with st.expander("View detailed error"):
            st.code(traceback.format_exc())
        return False

def upload_page():
    """Upload page - main landing"""
    
    # Header
    st.markdown("""
        <div class="app-header">
            <h1 class="app-title">Lecture<span class="gold">AI</span></h1>
            <p class="app-subtitle">Transform lectures into structured notes with AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check API keys
    missing_keys = validate_api_keys()
    if missing_keys:
        st.markdown(f'''
            <div class="error-card">
                <strong>⚠️ Missing API Keys:</strong> {', '.join(missing_keys)}<br><br>
                Add your keys in Streamlit Cloud: <strong>Settings → Secrets</strong>
            </div>
        ''', unsafe_allow_html=True)
        with st.expander("📖 How to add API keys"):
            st.code("""
# In Streamlit Cloud Settings → Secrets:
ASSEMBLYAI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
            """)
        return
    
    # Upload section
    st.markdown("""
        <div class="upload-card">
            <h3>📁 Upload Your Lecture Audio</h3>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'mp4', 'flac', 'ogg'],
        help="Supported: MP3, WAV, M4A, MP4, FLAC, OGG",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Show file info
        file_size = uploaded_file.size / (1024 * 1024)  # MB
        st.markdown(f'''
            <div class="success-card">
                <strong>✅ File Ready:</strong> {uploaded_file.name}<br>
                <strong>Size:</strong> {file_size:.2f} MB
            </div>
        ''', unsafe_allow_html=True)
        
        # Generate button
        if st.button("🚀 Generate Notes"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                process_audio_file(tmp_path, uploaded_file.name)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    # Info section
    st.markdown("""
        <div class="info-card">
            <strong>💡 How it works:</strong><br>
            1. Upload your lecture audio file<br>
            2. AI transcribes and analyzes the content<br>
            3. Get structured notes with key concepts<br>
            4. Download in TXT or Markdown format
        </div>
    """, unsafe_allow_html=True)
    
    # Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">🎙️</div>
                <div class="stat-label">AI Transcription</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">📝</div>
                <div class="stat-label">Smart Notes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">💾</div>
                <div class="stat-label">Export Options</div>
            </div>
        """, unsafe_allow_html=True)

def results_page():
    """Results page - shows generated notes"""
    
    if not st.session_state.notes:
        st.session_state.page = 'upload'
        st.rerun()
        return
    
    # Header with back button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div class="results-header">
                <div class="results-title">📖 Your Notes</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("← New Upload"):
            st.session_state.page = 'upload'
            st.session_state.notes = None
            st.session_state.transcript = None
            st.rerun()
    
    # Main layout: Sidebar + Content
    col_side, col_main = st.columns([1, 2.5])
    
    with col_side:
        # File info
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">📄 File Info</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.file_info:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{st.session_state.file_info.get('word_count', 0):,}</div>
                    <div class="stat-label">Words</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Key concepts
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">🏷️ Key Concepts</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.keywords:
            for i, kw in enumerate(st.session_state.keywords):
                badge_class = "keyword-badge-gold" if i % 3 == 0 else "keyword-badge"
                st.markdown(f'<span class="{badge_class}">{kw}</span>', unsafe_allow_html=True)
        
        # Transcript
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">📜 Transcript</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View full transcript"):
            st.text_area(
                "Transcript",
                st.session_state.transcript,
                height=300,
                label_visibility="collapsed"
            )
        
        # Downloads
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-title">💾 Download</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            "📥 TXT",
            st.session_state.notes,
            "notes.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        formatted = format_notes(st.session_state.notes)
        st.download_button(
            "📥 Markdown",
            formatted,
            "notes.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col_main:
        # Display notes
        sections = extract_sections(st.session_state.notes)
        
        for section_title, section_content in sections.items():
            st.markdown(f"""
                <div class="topic-card">
                    <div class="topic-header">{section_title}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if "Theory:" in section_content or "**Theory:**" in section_content:
                parts = section_content.split("Example:")
                theory = parts[0].replace("Theory:", "").replace("**Theory:**", "").strip()
                
                st.markdown(f'<div class="theory-block"><strong>💡 Theory:</strong> {theory}</div>', 
                          unsafe_allow_html=True)
                
                if len(parts) > 1:
                    example = parts[1].replace("**Example:**", "").strip()
                    st.markdown(f'<div class="example-block"><strong>✨ Example:</strong> {example}</div>', 
                              unsafe_allow_html=True)
            else:
                st.markdown(section_content)

def main():
    initialize_session_state()
    
    # Route to correct page
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
