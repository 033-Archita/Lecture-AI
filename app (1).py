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
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: var(--bg-soft); }

    /* Hero Section */
    .hero {
        padding: 60px 0 40px 0;
        text-align: center;
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -2px;
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
        padding: 2rem !important;
        transition: all 0.4s ease;
        text-align: center;
    }

    .upload-zone:hover {
        border-color: var(--accent);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.1);
    }

    /* Note Content Cards */
    .note-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    .section-tag {
        color: var(--accent);
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
        display: block;
    }

    /* UI Components */
    .stButton > button {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.8rem 2.5rem !important;
        font-weight: 700 !important;
        transition: 0.3s all;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3) !important;
    }

    .keyword-pill {
        background: #FFF5F5;
        color: #C53030;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #FED7D7;
        margin: 4px;
        display: inline-block;
    }

    /* Metric Grid */
    .metric-grid {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2.5rem;
    }

    .metric-item {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        flex: 1;
        border-bottom: 4px solid var(--accent);
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    defaults = {
        'page': 'upload', 
        'transcript': None, 
        'notes': None, 
        'keywords': [], 
        'file_info': {}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def process_audio_logic(path, name):
    with st.status("🚀 Processing Lecture Content...", expanded=True) as status:
        st.write("🎙️ Extracting audio...")
        transcript = transcribe_audio(path)
        
        st.write("🔍 Identifying key concepts...")
        keywords = extract_keywords(transcript)
        
        st.write("📝 Generating study notes...")
        notes = generate_notes(transcript)
        
        # Calculate Stats
        word_count = len(transcript.split())
        read_time = max(1, round(word_count / 200))
        
        # Consistent Key Mapping
        st.session_state.update({
            'transcript': transcript,
            'keywords': keywords,
            'notes': notes,
            'file_info': {
                'name': name,
                'words': word_count,
                'time': f"{read_time} min"
            },
            'page': 'results'
        })
        status.update(label="Analysis Complete!", state="complete")
        time.sleep(0.5)
        st.rerun()

def upload_page():
    st.markdown('<div class="hero"><h1 class="hero-title">LectureAI</h1><p style="color: #64748B;">Smart Knowledge Extraction</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload audio", type=['mp3', 'wav', 'm4a','mp4'], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            st.markdown(f"<div style='text-align:center; padding: 15px;'>📄 <b>{uploaded_file.name}</b></div>", unsafe_allow_html=True)
            if st.button("Generate Smart Notes", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    process_audio_logic(tmp.name, uploaded_file.name)

def results_page():
    # Header & Back Action
    c1, c2 = st.columns([5, 1])
    with c1:
        st.title(f"📖 {st.session_state.file_info['name']}")
    with c2:
        if st.button("New Scan", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()

    # Metrics Layout
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-item"><small style='color:#64748B'>WORDS ANALYZED</small><br><b style='font-size:1.4rem'>{st.session_state.file_info['words']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>READING TIME</small><br><b style='font-size:1.4rem'>{st.session_state.file_info['time']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>TOPIC COVERAGE</small><br><b style='font-size:1.4rem'>Comprehensive</b></div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([2.5, 1], gap="large")

    with col_main:
        sections = extract_sections(st.session_state.notes)
        for i, (title, content) in enumerate(sections.items()):
            # Cleaning content for display
            display_content = content.replace('Theory:', '<b>💡 Theory:</b>').replace('Example:', '<br><br><b>✨ Example:</b>')
            
            st.markdown(f"""
            <div class="note-card">
                <span class="section-tag">MODULE {i+1}</span>
                <h2 style='margin-top:0; color:#1A1A1A;'>{title}</h2>
                <div style='color: #475569; line-height: 1.8; font-size: 1.05rem;'>{display_content}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown("#### 🏷️ Key Concepts")
        kw_html = "".join([f'<span class="keyword-pill">{kw}</span>' for kw in st.session_state.keywords])
        st.markdown(kw_html if kw_html else "No keywords found", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 📥 Export Data")
        st.download_button("Download .MD", st.session_state.notes, file_name="lecture_notes.md", use_container_width=True)
        
        with st.expander("📜 Transcript"):
            st.write(st.session_state.transcript)

def main():
    initialize_session_state()
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
