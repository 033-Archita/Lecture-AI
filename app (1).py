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

# --- PREMIUM UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --accent: #FF6B6B;
        --accent-gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E72 100%);
        --bg-soft: #FDFCFB;
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: var(--bg-soft); }

    /* Center the Uploader & Style it (UI FIX) */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #E2E8F0;
        border-radius: 24px;
        padding: 3rem !important;
        display: flex;
        justify-content: center;
    }
    
    [data-testid="stFileUploader"] section {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Hero Styling */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 2rem;
        text-align: center;
    }

    /* Metric Cards (UI FIX) */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .metric-item {
        background: white;
        padding: 1.5rem;
        border-radius: 24px;
        border-bottom: 5px solid var(--accent);
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
    }

    /* Note Card & Module Tags (UI FIX) */
    .note-card {
        background: white;
        border-radius: 28px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        border: 1px solid #F1F5F9;
    }

    .section-tag {
        display: inline-block;
        color: var(--accent);
        background: rgba(255, 107, 107, 0.1);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }

    /* Keyword Sidebar Pills (UI FIX) */
    .keyword-pill {
        background: white;
        color: var(--accent);
        padding: 8px 18px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #FFDADA;
        margin: 5px;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    /* Button Polish */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        transition: 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    for key, val in {'page': 'upload', 'transcript': None, 'notes': None, 'keywords': [], 'file_info': {}}.items():
        if key not in st.session_state: st.session_state[key] = val

def process_audio_logic(path, name):
    with st.status("🔮 Analyzing Lecture...", expanded=True) as status:
        st.write("🎙️ Transcribing audio...")
        transcript = transcribe_audio(path)
        
        st.write("🔍 Extracting concepts...")
        keywords = extract_keywords(transcript)
        
        st.write("✍️ Generating smart notes...")
        notes = generate_notes(transcript)
        
        word_count = len(transcript.split())
        st.session_state.update({
            'transcript': transcript, 'keywords': keywords, 'notes': notes,
            'file_info': {
                'name': name, 'words': word_count, 
                'time': f"{max(1, round(word_count/200))} min"
            },
            'page': 'results'
        })
        status.update(label="Complete!", state="complete")
        time.sleep(0.5)
        st.rerun()

def upload_page():
    st.markdown('<h1 class="hero-title">LectureAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B; margin-bottom:3rem;">Smart Knowledge Extraction</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Upload", type=['mp3', 'wav', 'm4a', 'mp4'], label_visibility="collapsed")
        if uploaded_file:
            st.markdown(f"<div style='text-align:center; padding: 1rem;'>📄 <b>{uploaded_file.name}</b></div>", unsafe_allow_html=True)
            if st.button("🚀 Start Analysis", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    process_audio_logic(tmp.name, uploaded_file.name)

def results_page():
    # Header row with Icon and New Scan button
    c1, c2 = st.columns([5, 1.2])
    with c1: st.markdown(f"<h1>📖 {st.session_state.file_info['name']}</h1>", unsafe_allow_html=True)
    with c2: 
        if st.button("New Scan", use_container_width=True):
            st.session_state.page = 'upload'; st.rerun()

    # Metric Row
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-item"><small style='color:#64748B'>WORDS ANALYZED</small><br><b style='font-size:1.8rem;'>{st.session_state.file_info['words']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>READING TIME</small><br><b style='font-size:1.8rem;'>{st.session_state.file_info['time']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>TOPIC COVERAGE</small><br><b style='font-size:1.8rem;'>Comprehensive</b></div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([2.5, 1], gap="large")

    with col_main:
        sections = extract_sections(st.session_state.notes)
        for i, (title, content) in enumerate(sections.items()):
            # Using st.container for styling while st.markdown handles the asterisks fix
            with st.container():
                st.markdown(f'<div class="note-card"><span class="section-tag">MODULE {i+1}</span><h2 style="margin:0 0 1rem 0;">{title}</h2>', unsafe_allow_html=True)
                
                # FIX: st.markdown renders the **Bold** text correctly instead of raw text
                st.markdown(content)
                
                st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("#### 🏷️ Key Concepts")
        # Generate the HTML for the pills
        kw_html = "".join([f'<span class="keyword-pill">{kw}</span>' for kw in st.session_state.keywords])
        st.markdown(f'<div style="line-height:2.2;">{kw_html}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>#### 📥 Export Data", unsafe_allow_html=True)
        st.download_button("Download .MD", st.session_state.notes, file_name="notes.md", use_container_width=True)
        
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
