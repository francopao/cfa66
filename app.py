"""
CFA Deep Memory System
Mobile-first Streamlit app for spaced repetition learning.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="CFA Memory",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile-first layout */
    .block-container { padding: 0.5rem 1rem 2rem 1rem; max-width: 600px; }
    
    /* Header */
    .cfa-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        text-align: center;
    }
    .cfa-header h2 { color: white; margin: 0; font-size: 1.3rem; }
    .cfa-header p { color: #93C5FD; margin: 4px 0 0 0; font-size: 0.85rem; }
    
    /* Cards */
    .card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .card-formula {
        background: #0F172A;
        border: 1px solid #2563EB;
        border-radius: 8px;
        padding: 12px;
        font-family: monospace;
        font-size: 1rem;
        color: #60A5FA;
        text-align: center;
        margin: 12px 0;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-fi { background: #1E3A5F; color: #93C5FD; }
    .badge-eq { background: #1A3A2A; color: #6EE7B7; }
    .badge-qm { background: #3A1A3A; color: #C4B5FD; }
    .badge-fsa { background: #3A2A0A; color: #FCD34D; }
    
    /* Stats */
    .stat-row {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
    }
    .stat-box {
        flex: 1;
        background: #1E293B;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        border: 1px solid #334155;
    }
    .stat-number { font-size: 1.4rem; font-weight: 700; color: #60A5FA; }
    .stat-label { font-size: 0.7rem; color: #94A3B8; margin-top: 2px; }
    
    /* Nav buttons */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 12px;
        font-weight: 600;
        border: none;
        margin-bottom: 4px;
    }
    
    /* Quality buttons */
    .quality-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    
    /* Progress bar custom */
    .progress-bar {
        background: #1E293B;
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
        margin: 4px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #2563EB, #06B6D4);
    }
    
    /* Hide Streamlit branding on mobile */
    #MainMenu, footer, header { visibility: hidden; }
    
    .intuition-box {
        background: #0F2A1A;
        border-left: 3px solid #10B981;
        border-radius: 0 8px 8px 0;
        padding: 12px;
        color: #6EE7B7;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 12px 0;
    }
    .hook-box {
        background: #2A1A0F;
        border-left: 3px solid #F59E0B;
        border-radius: 0 8px 8px 0;
        padding: 10px;
        color: #FCD34D;
        font-size: 0.85rem;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

from core.session_manager import load_progress, get_stats
from core.scheduler import load_all_cards, get_due_cards, load_all_exercises

# Load data
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "all_cards" not in st.session_state:
    st.session_state.all_cards = load_all_cards()
if "all_exercises" not in st.session_state:
    st.session_state.all_exercises = load_all_exercises()
if "mode" not in st.session_state:
    st.session_state.mode = "home"

progress = st.session_state.progress
all_cards = st.session_state.all_cards
stats = get_stats(progress)
all_ids = [c["id"] for c in all_cards]
due_ids = get_due_cards(progress, all_ids)

# ─── HEADER ────────────────────────────────────────────────
st.markdown(f"""
<div class="cfa-header">
  <h2>📊 CFA Memory System</h2>
  <p>🔥 {stats['streak']} day streak &nbsp;|&nbsp; {len(due_ids)} cards due today</p>
</div>
""", unsafe_allow_html=True)

# ─── HOME MODE ──────────────────────────────────────────────
if st.session_state.mode == "home":
    # Stats row
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-box">
        <div class="stat-number">{len(due_ids)}</div>
        <div class="stat-label">Due Today</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{stats['mastered']}</div>
        <div class="stat-label">Mastered</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{stats['accuracy']}%</div>
        <div class="stat-label">Accuracy</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{len(all_cards)}</div>
        <div class="stat-label">Total Cards</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Choose your study mode")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"🔁 Review Today\n({len(due_ids)} cards)", use_container_width=True):
            st.session_state.mode = "flashcard"
            st.session_state.due_queue = due_ids.copy()
            st.session_state.current_card_idx = 0
            st.session_state.show_answer = False
            st.session_state.session_correct = 0
            st.session_state.session_total = 0
            st.rerun()
    with col2:
        if st.button("📐 Exercise\n(Numeric)", use_container_width=True):
            st.session_state.mode = "exercise"
            st.session_state.ex_idx = 0
            st.session_state.show_ex_answer = False
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("💡 Intuition\nDeep Dive", use_container_width=True):
            st.session_state.mode = "intuition"
            st.rerun()
    with col4:
        if st.button("📊 My Progress\nDashboard", use_container_width=True):
            st.session_state.mode = "progress"
            st.rerun()

    # Topic filter quick access
    st.markdown("---")
    st.markdown("**Study by topic:**")
    topics = sorted(set(c.get("topic", "?") for c in all_cards))
    topic_cols = st.columns(2)
    for i, topic in enumerate(topics):
        with topic_cols[i % 2]:
            topic_cards = [c["id"] for c in all_cards if c.get("topic") == topic]
            topic_due = [cid for cid in topic_cards if cid in due_ids]
            if st.button(f"{topic}\n({len(topic_due)} due / {len(topic_cards)} total)", use_container_width=True):
                st.session_state.mode = "flashcard"
                st.session_state.due_queue = topic_cards
                st.session_state.current_card_idx = 0
                st.session_state.show_answer = False
                st.session_state.session_correct = 0
                st.session_state.session_total = 0
                st.rerun()

# ─── FLASHCARD MODE ─────────────────────────────────────────
elif st.session_state.mode == "flashcard":
    from modes.flashcard_mode import render_flashcard
    render_flashcard()

# ─── EXERCISE MODE ──────────────────────────────────────────
elif st.session_state.mode == "exercise":
    from modes.exercise_mode import render_exercise
    render_exercise()

# ─── INTUITION MODE ─────────────────────────────────────────
elif st.session_state.mode == "intuition":
    from modes.intuition_mode import render_intuition
    render_intuition()

# ─── PROGRESS MODE ──────────────────────────────────────────
elif st.session_state.mode == "progress":
    from modes.review_summary import render_progress
    render_progress()
