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
    page_title="LectureAI | Smart Notes",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LUXURY UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --accent: #FF6B6B;
        --accent-gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E72 100%);
        --bg-soft: #FDFCFB;
        --text-main: #1A1A1A;
        --glass: rgba(255, 255, 255, 0.8);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: var(--bg-soft); }

    /* Glass Navigation Bar */
    .nav-bar {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 70px;
        background: var(--glass);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4rem;
        z-index: 1000;
    }

    /* Hero Section */
    .hero {
        padding: 100px 0 40px 0;
        text-align: center;
    }

    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -3px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    /* Modern Upload Container */
    .upload-zone {
        background: white;
        border: 2px dashed #E2E8F0;
        border-radius: 32px;
        padding: 4rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
    }

    .upload-zone:hover {
        border-color: var(--accent);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.1);
        transform: translateY(-4px);
    }

    /* Content Cards */
    .note-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: 0.3s ease;
    }

    .note-card:hover {
        box-shadow: 0 12px 24px rgba(0,0,0,0.06);
    }

    .section-tag {
        color: var(--accent);
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        display: block;
    }

    /* Interactive Elements */
    .stButton > button {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.8rem 2.5rem !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 20px rgba(255, 107, 107, 0.2) !important;
    }

    .keyword-pill {
        background: #FFF5F5;
        color: #C53030;
        padding: 6px 16px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #FED7D7;
        margin: 4px;
        display: inline-block;
    }

    /* Metric Layout */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 3rem;
    }

    .metric-item {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: left;
        border-bottom: 4px solid var(--accent);
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    for key, val in {'page': 'upload', 'transcript': None, 'notes': None, 'keywords': [], 'file_info': {}}.items():
        if key not in st.session_state: st.session_state[key] = val

def upload_page():
    st.markdown('<div class="hero"><h1 class="hero-title">LectureAI</h1><p style="font-size: 1.2rem; color: #64748B;">Turn complex audio into structured knowledge</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop audio here", type=['mp3', 'wav', 'm4a'], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            st.markdown(f"<div style='text-align:center; padding: 20px; color: #475569;'>Selected: <b>{uploaded_file.name}</b></div>", unsafe_allow_html=True)
            if st.button("✨ Transcribe & Analyze", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    process_audio_logic(tmp.name, uploaded_file.name)

def process_audio_logic(path, name):
    with st.status("🚀 Processing Lecture...", expanded=True) as status:
        st.write("🎙️ Extracting audio...")
        transcript = transcribe_audio(path)
        st.write("🔍 Identifying key concepts...")
        keywords = extract_keywords(transcript)
        st.write("📝 Generating study notes...")
        notes = generate_notes(transcript)
        
        st.session_state.update({
            'transcript': transcript, 'keywords': keywords, 'notes': notes,
            'file_info': {'name': name, 'words': len(transcript.split()), 'time': f"{round(len(transcript.split())/150)}m read"},
            'page': 'results'
        })
        status.update(label="Complete!", state="complete")
        time.sleep(1)
        st.rerun()

def results_page():
    # Sticky header-like action row
    c1, c2 = st.columns([4, 1])
    with c1: st.title(f"📖 {st.session_state.file_info['name']}")
    with c2: 
        if st.button("Restart", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()

    # Metrics Row
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-item"><small style='color:#64748B'>WORD COUNT</small><br><b>{st.session_state.file_info['words']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>READING TIME</small><br><b>{st.session_state.file_info['time']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>CONCEPTS FOUND</small><br><b>{len(st.session_state.keywords)}</b></div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([2.5, 1], gap="large")

    with col_main:
        sections = extract_sections(st.session_state.notes)
        for i, (title, content) in enumerate(sections.items()):
            st.markdown(f"""
            <div class="note-card">
                <span class="section-tag">TOPIC {i+1}</span>
                <h2 style='margin-top:0;'>{title}</h2>
                <div style='color: #334155; line-height: 1.7;'>{content.replace('Theory:', '<b>💡 Theory:</b>').replace('Example:', '<br><b>✨ Example:</b>')}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown("#### 🏷️ Key Concepts")
        kw_html = "".join([f'<span class="keyword-pill">{kw}</span>' for kw in st.session_state.keywords])
        st.markdown(kw_html, unsafe_allow_html=True)
        
        st.markdown("<br>#### 📁 Export", unsafe_allow_html=True)
        st.download_button("Export as PDF/Markdown", st.session_state.notes, file_name="notes.md", use_container_width=True)
        
        with st.expander("🔍 View Raw Transcript"):
            st.write(st.session_state.transcript)

def main():
    initialize_session_state()
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
