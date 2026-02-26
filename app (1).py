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

# --- PREMIUM UI STYLING (V4 - HEADER & SIDEBAR FIXES) ---
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

    /* Centered Uploader Fix */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #E2E8F0;
        border-radius: 20px;
        padding: 2rem !important;
        display: flex;
        justify-content: center;
    }
    [data-testid="stFileUploader"] section {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }

    /* Smaller, Refined Note Cards (FIX FOR "TOO BIG") */
    .note-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #F1F5F9;
    }

    .note-card h2 {
        font-size: 1.5rem !important; /* Smaller Header */
        margin: 0.5rem 0 1rem 0 !important;
        font-weight: 700;
        color: #1A1A1A;
    }

    .section-tag {
        display: inline-block;
        color: var(--accent);
        background: rgba(255, 107, 107, 0.1);
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Metric Layout Fixes */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin-bottom: 2rem;
    }

    .metric-item {
        background: white;
        padding: 1.2rem;
        border-radius: 18px;
        border-bottom: 4px solid var(--accent);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    /* Keyword Pills Spacing */
    .keyword-pill {
        background: white;
        color: var(--accent);
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #FFDADA;
        margin: 4px;
        display: inline-block;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    for key, val in {'page': 'upload', 'transcript': None, 'notes': None, 'keywords': [], 'file_info': {}}.items():
        if key not in st.session_state: st.session_state[key] = val

def process_audio_logic(path, name):
    with st.status("🔮 Analyzing...", expanded=True) as status:
        transcript = transcribe_audio(path)
        keywords = extract_keywords(transcript)
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
        status.update(label="Done!", state="complete")
        time.sleep(0.5)
        st.rerun()

def upload_page():
    st.markdown('<h1 style="text-align:center; font-weight:800; background:linear-gradient(135deg, #FF6B6B 0%, #FF8E72 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:3.5rem; margin-top:2rem;">LectureAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#64748B; margin-bottom:3rem;">Smart Knowledge Extraction</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader("Upload", type=['mp3', 'wav', 'm4a', 'mp4'], label_visibility="collapsed")
        if uploaded_file:
            st.markdown(f"<div style='text-align:center; padding: 1rem;'>📄 <b>{uploaded_file.name}</b></div>", unsafe_allow_html=True)
            if st.button("🚀 Analyze Lecture", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    process_audio_logic(tmp.name, uploaded_file.name)

def results_page():
    # Top Header
    c1, c2 = st.columns([5, 1.2])
    with c1: st.markdown(f"<h1 style='margin:0;'>📖 {st.session_state.file_info['name']}</h1>", unsafe_allow_html=True)
    with c2: 
        if st.button("New Scan", use_container_width=True):
            st.session_state.page = 'upload'; st.rerun()

    # Metrics
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-item"><small style='color:#64748B'>WORDS</small><br><b style='font-size:1.5rem;'>{st.session_state.file_info['words']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>READ TIME</small><br><b style='font-size:1.5rem;'>{st.session_state.file_info['time']}</b></div>
        <div class="metric-item"><small style='color:#64748B'>COVERAGE</small><br><b style='font-size:1.5rem;'>High</b></div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([2.5, 1], gap="large")

    with col_main:
        sections = extract_sections(st.session_state.notes)
        for i, (title, content) in enumerate(sections.items()):
            # Custom container for card styling
            st.markdown(f'<div class="note-card"><span class="section-tag">MODULE {i+1}</span><h2>{title}</h2>', unsafe_allow_html=True)
            # st.markdown here correctly handles the **Bold** and list items
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        # Sidebar fix: Using standard Streamlit headers to avoid the ## raw text issue
        st.subheader("🏷️ Key Concepts")
        kw_html = "".join([f'<span class="keyword-pill">{kw}</span>' for kw in st.session_state.keywords])
        st.markdown(f'<div style="line-height:2;">{kw_html}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("📥 Actions")
        st.download_button("Download .MD", st.session_state.notes, file_name="notes.md", use_container_width=True)
        
        with st.expander("📜 Transcript"):
            st.caption(st.session_state.transcript)

def main():
    initialize_session_state()
    if st.session_state.page == 'upload':
        upload_page()
    else:
        results_page()

if __name__ == "__main__":
    main()
