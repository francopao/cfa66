"""
Flashcard Mode — SM-2 Spaced Repetition Active Recall
Supports both multiple choice (CFA-style) and free recall.
"""
import streamlit as st
import random
from core.sm2 import sm2_update, quality_label, days_until_review
from core.session_manager import (
    get_card_state, save_card_state, save_progress, log_session
)
from core.scheduler import get_card_by_id

TOPIC_COLORS = {
    "Fixed Income": "#1E3A5F",
    "Equity Investments": "#1A3A2A",
    "Quantitative Methods": "#3A1A3A",
    "Financial Statement Analysis": "#3A2A0A",
}
TOPIC_TEXT = {
    "Fixed Income": "#93C5FD",
    "Equity Investments": "#6EE7B7",
    "Quantitative Methods": "#C4B5FD",
    "Financial Statement Analysis": "#FCD34D",
}


def render_flashcard():
    progress = st.session_state.progress
    all_cards = st.session_state.all_cards
    due_queue = st.session_state.get("due_queue", [])

    if st.button("← Back to Home", use_container_width=False):
        st.session_state.mode = "home"
        st.rerun()

    if not due_queue or st.session_state.current_card_idx >= len(due_queue):
        _render_session_complete()
        return

    card_id = due_queue[st.session_state.current_card_idx]
    card = get_card_by_id(card_id, all_cards)
    if not card:
        st.session_state.current_card_idx += 1
        st.rerun()
        return

    state = get_card_state(progress, card_id)
    total = len(due_queue)
    current = st.session_state.current_card_idx + 1
    topic = card.get("topic", "")

    # Progress bar
    pct = int((current - 1) / total * 100)
    st.markdown(f"""
    <div style="margin-bottom:8px;">
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94A3B8; margin-bottom:4px;">
        <span>Card {current} of {total}</span>
        <span>{st.session_state.session_correct} correct</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

    # Topic badge
    bg = TOPIC_COLORS.get(topic, "#1E293B")
    tc = TOPIC_TEXT.get(topic, "#CBD5E1")
    st.markdown(f"""
    <span style="background:{bg}; color:{tc}; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600;">
      {topic} · {card.get('subtopic','')}
    </span>
    """, unsafe_allow_html=True)

    # Card title
    st.markdown(f"### {card.get('name', card_id)}")

    # Formula (always visible — active recall means reconstructing the formula from the name)
    if not st.session_state.show_answer:
        st.markdown("""
        <div style="background:#0F172A; border:2px dashed #334155; border-radius:10px;
                    padding:30px; text-align:center; color:#475569; margin:16px 0;">
          <div style="font-size:1.5rem">🤔</div>
          <div style="margin-top:8px; font-size:0.9rem">Recall the formula before revealing</div>
        </div>
        """, unsafe_allow_html=True)

        # Multiple choice OR reveal button
        if card.get("options"):
            st.markdown("**Choose the correct formula/answer:**")
            options = card["options"]
            # Shuffle but keep track of correct
            correct_idx = card.get("correct_option", 0)
            if f"shuffled_{card_id}" not in st.session_state:
                idx_list = list(range(len(options)))
                random.shuffle(idx_list)
                st.session_state[f"shuffled_{card_id}"] = idx_list
            idx_list = st.session_state[f"shuffled_{card_id}"]

            for display_pos, orig_idx in enumerate(idx_list):
                label = f"{chr(65+display_pos)}. {options[orig_idx]}"
                if st.button(label, key=f"opt_{card_id}_{display_pos}", use_container_width=True):
                    st.session_state[f"selected_{card_id}"] = orig_idx
                    st.session_state.show_answer = True
                    # Auto-grade
                    if orig_idx == correct_idx:
                        st.session_state[f"quality_{card_id}"] = 4
                        st.session_state.session_correct += 1
                    else:
                        st.session_state[f"quality_{card_id}"] = 1
                    st.session_state.session_total += 1
                    st.rerun()
        else:
            if st.button("👁 Reveal Answer", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()

    else:
        # Show the answer
        selected = st.session_state.get(f"selected_{card_id}", -1)
        correct_idx = card.get("correct_option", 0)
        options = card.get("options", [])

        if options and selected >= 0:
            if selected == correct_idx:
                st.success(f"✅ Correct! **{options[correct_idx]}**")
            else:
                st.error(f"❌ You chose: {options[selected]}")
                st.success(f"✅ Correct: **{options[correct_idx]}**")

        # Formula box
        st.markdown(f"""
        <div class="card-formula">{card.get('formula','')}</div>
        """, unsafe_allow_html=True)

        # Intuition
        st.markdown(f"""
        <div class="intuition-box">💡 <b>Why this works:</b><br>{card.get('intuition','')}</div>
        """, unsafe_allow_html=True)

        # Memory hook
        st.markdown(f"""
        <div class="hook-box">🎯 <b>Memory hook:</b> {card.get('memory_hook','')}</div>
        """, unsafe_allow_html=True)

        # SM-2 quality rating (if no multiple choice or override)
        auto_quality = st.session_state.get(f"quality_{card_id}", -1)

        if auto_quality >= 0 and card.get("options"):
            # Auto-graded from MC — just show next button
            st.markdown(f"**Auto-rated: {quality_label(auto_quality)}**")
            _apply_and_next(card_id, auto_quality, progress)
        else:
            st.markdown("**How well did you recall this?**")
            cols = st.columns(3)
            quality_map = [
                (0, "💀 Blank", cols[0]),
                (2, "😅 Hard", cols[1]),
                (3, "🤔 OK", cols[2]),
                (4, "😊 Good", cols[0]),
                (5, "🔥 Easy", cols[1]),
            ]
            for q, label, col in quality_map:
                with col:
                    if st.button(label, key=f"q_{card_id}_{q}", use_container_width=True):
                        if q >= 3:
                            st.session_state.session_correct += 1
                        st.session_state.session_total += 1
                        _apply_and_next(card_id, q, progress)


def _apply_and_next(card_id, quality, progress):
    state = get_card_state(progress, card_id)
    state = sm2_update(state, quality)
    progress = save_card_state(progress, state)
    st.session_state.progress = progress
    save_progress(progress)

    # Advance
    st.session_state.current_card_idx += 1
    st.session_state.show_answer = False
    # Clean up shuffle state
    for key in [f"shuffled_{card_id}", f"selected_{card_id}", f"quality_{card_id}"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def _render_session_complete():
    correct = st.session_state.get("session_correct", 0)
    total = st.session_state.get("session_total", 0)
    pct = int(correct / total * 100) if total > 0 else 0

    progress = st.session_state.progress
    progress = log_session(progress, total, correct)
    save_progress(progress)
    st.session_state.progress = progress

    emoji = "🔥" if pct >= 80 else "💪" if pct >= 60 else "📚"
    st.markdown(f"""
    <div style="text-align:center; padding:30px;">
      <div style="font-size:3rem">{emoji}</div>
      <h2>Session Complete!</h2>
      <div style="font-size:1.5rem; color:#60A5FA;">{correct}/{total} correct ({pct}%)</div>
      <div style="color:#94A3B8; margin-top:8px;">
        {'Excellent! Science says you\'re building strong memories.' if pct >= 80 else 
         'Good effort. SM-2 will show you weak cards again sooner.' if pct >= 60 else
         'Keep going — spaced repetition works best with consistent daily sessions.'}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.mode = "home"
        st.rerun()
