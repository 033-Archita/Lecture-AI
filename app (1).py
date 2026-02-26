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

# --- ADVANCED UI/UX STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #FF6B6B;
        --secondary: #FF8E72;
        --dark: #2D3436;
        --bg: #F8F9FA;
    }

    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: var(--bg); }

    /* Clean Header */
    .main-header {
        text-align: center;
        padding: 3rem 1rem;
        background: white;
        border-radius: 0 0 40px 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 3rem;
    }

    .app-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8C42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1.5px;
    }

    /* Stats Dashboard Row */
    .stats-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        flex: 1;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary);
    }

    .stat-label {
        font-size: 0.8rem;
        color: #636E72;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Note Content Styling */
    .note-section {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        border-left: 6px solid var(--primary);
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
    }

    .section-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--dark);
        margin-bottom: 1.5rem;
    }

    .theory-box {
        background: #FFF5F5;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px dashed #FF6B6B;
        margin: 1rem 0;
    }

    .example-box {
        background: #F0FFF4;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #C6F6D5;
        font-style: italic;
    }

    /* File Uploader Customization */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #DFE6E9;
        border-radius: 20px;
        padding: 3rem !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--dark) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: 0.3s all !important;
        border: none !important;
    }

    .stButton > button:hover {
        background: var(--primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        background: #F1F2F6;
        color: #57606F;
        border-radius: 50px;
        font-size: 0.85rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'page' not in st.session_state: st.session_state.page = 'upload'
    if 'transcript' not in st.session_state: st.session_state.transcript = None
    if 'notes' not in st.session_state: st.session_state.notes = None
    if 'keywords' not in st.session_state: st.session_state.keywords = []
    if 'file_info' not in st.session_state: st.session_state.file_info = {}

def process_audio_file(file_path, filename):
    try:
        progress_text = st.empty()
        bar = st.progress(0)
        
        progress_text.markdown("✨ **Step 1/3:** Transcribing audio...")
        transcript = transcribe_audio(file_path)
        bar.progress(40)
        
        if not transcript: return False
        
        progress_text.markdown("🧠 **Step 2/3:** Analyzing concepts...")
        keywords = extract_keywords(transcript, max_keywords=6)
        bar.progress(70)
        
        progress_text.markdown("✍️ **Step 3/3:** Formatting smart notes...")
        notes = generate_notes(transcript)
        bar.progress(100)
        
        st.session_state.transcript = transcript
        st.session_state.keywords = keywords
        st.session_state.notes = notes
        st.session_state.file_info = {
            'name': filename,
            'word_count': len(transcript.split()),
            'reading_time': round(len(transcript.split()) / 200)
        }
        
        st.session_state.page = 'results'
        st.rerun()
    except Exception as e:
        st.error(f"Processing error: {e}")

def upload_page():
    st.markdown('<div class="main-header"><h1 class="app-title">LectureAI</h1><p style="color: #636E72;">Your personal academic scribe</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Upload lecture (MP3, WAV, M4A)", type=['mp3', 'wav', 'm4a'], label_visibility="collapsed")
        
        if uploaded_file:
            st.info(f"📁 Selected: {uploaded_file.name}")
            if st.button("Generate My Notes", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    process_audio_file(tmp.name, uploaded_file.name)

def results_page():
    # Top Action Bar
    t1, t2 = st.columns([5, 1])
    with t1:
        st.markdown(f"### 📝 {st.session_state.file_info.get('name')}")
    with t2:
        if st.button("New Upload", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Word Count</div><div class="stat-value">{st.session_state.file_info.get("word_count")}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Est. Reading Time</div><div class="stat-value">{st.session_state.file_info.get("reading_time")} min</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">AI Confidence</div><div class="stat-value">High</div></div>', unsafe_allow_html=True)

    # Content Area
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        sections = extract_sections(st.session_state.notes)
        for title, content in sections.items():
            st.markdown(f'<div class="note-section"><div class="section-title">{title}</div>', unsafe_allow_html=True)
            
            # Smart split for Theory/Example
            if "Theory:" in content:
                parts = content.split("Example:")
                theory = parts[0].replace("Theory:", "").strip()
                st.markdown(f'<div class="theory-box"><b>💡 Core Concept:</b><br>{theory}</div>', unsafe_allow_html=True)
                if len(parts) > 1:
                    example = parts[1].strip()
                    st.markdown(f'<div class="example-box"><b>📝 Case/Example:</b><br>{example}</div>', unsafe_allow_html=True)
            else:
                st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("##### 🏷️ Key Concepts")
        for kw in st.session_state.keywords:
            st.markdown(f'<span class="badge">{kw}</span>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("##### 💾 Export")
        st.download_button("Download Markdown", st.session_state.notes, "notes.md", use_container_width=True)
        
        with st.expander("📜 Raw Transcript"):
            st.caption(st.session_state.transcript)

def main():
    initialize_session_state()
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
