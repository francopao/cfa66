"""
Progress Dashboard — shows streaks, accuracy, weak topics, upcoming reviews.
"""
import streamlit as st
from datetime import date, timedelta
from core.session_manager import get_stats, get_card_state
from core.scheduler import get_card_by_id, get_topics


def render_progress():
    progress = st.session_state.progress
    all_cards = st.session_state.all_cards
    stats = get_stats(progress)

    if st.button("← Back", use_container_width=False):
        st.session_state.mode = "home"
        st.rerun()

    st.markdown("### 📊 My Progress")

    # Streak + summary
    st.markdown(f"""
    <div style="background:#1E293B; border-radius:12px; padding:16px; margin-bottom:12px; text-align:center;">
      <div style="font-size:2rem;">🔥</div>
      <div style="font-size:1.8rem; font-weight:700; color:#F59E0B;">{stats['streak']} day streak</div>
      <div style="color:#94A3B8; font-size:0.85rem;">Keep it going — consistency beats intensity</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mastered", stats['mastered'], help="Cards with interval ≥ 21 days")
    with col2:
        st.metric("Learning", stats['learning'], help="Cards in active review")
    with col3:
        st.metric("Accuracy", f"{stats['accuracy']}%")

    # Session history (last 14 days)
    st.markdown("#### Recent Sessions")
    sessions = stats.get("sessions", [])[-14:]
    if sessions:
        import plotly.graph_objects as go
        dates = [s["date"] for s in sessions]
        cards = [s["cards_reviewed"] for s in sessions]
        accuracy = [round(s["correct"] / s["cards_reviewed"] * 100) if s["cards_reviewed"] > 0 else 0 for s in sessions]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dates, y=cards, name="Cards Reviewed",
                             marker_color='#2563EB', opacity=0.8))
        fig.update_layout(
            plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
            font=dict(color='#CBD5E1'),
            margin=dict(l=10, r=10, t=10, b=40),
            height=200, showlegend=False,
        )
        fig.update_xaxes(gridcolor='#334155', tickangle=-45)
        fig.update_yaxes(gridcolor='#334155')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Complete your first session to see history here.")

    # Weak cards (lowest easiness factor)
    st.markdown("#### 🎯 Your Weakest Cards")
    card_states = [(cid, get_card_state(progress, cid)) for cid in progress.get("cards", {})]
    card_states.sort(key=lambda x: x[1].easiness)
    weak_cards = card_states[:5]

    if weak_cards:
        for cid, state in weak_cards:
            card = get_card_by_id(cid, all_cards)
            if card:
                ease_pct = int((state.easiness - 1.3) / (2.5 - 1.3) * 100)
                ease_color = "#EF4444" if ease_pct < 33 else "#F59E0B" if ease_pct < 66 else "#10B981"
                st.markdown(f"""
                <div style="background:#0F172A; border-radius:8px; padding:10px 12px; margin:6px 0;
                            border-left:3px solid {ease_color};">
                  <div style="font-weight:600; font-size:0.9rem;">{card.get('name','')}</div>
                  <div style="color:#94A3B8; font-size:0.75rem;">{card.get('topic','')} · 
                    Ease: {state.easiness:.2f} · Interval: {state.interval}d</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Study some cards first to see your weak spots.")

    # Upcoming reviews
    st.markdown("#### 📅 Upcoming Reviews")
    upcoming = []
    for cid, s in card_states:
        days = (date.fromisoformat(s.next_review) - date.today()).days
        if 0 < days <= 14:
            card = get_card_by_id(cid, all_cards)
            if card:
                upcoming.append((days, card.get('name', cid), card.get('topic', '')))
    upcoming.sort()

    if upcoming:
        for days, name, topic in upcoming[:8]:
            label = f"in {days}d" if days > 1 else "tomorrow"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:6px 0;
                        border-bottom:1px solid #1E293B; font-size:0.85rem;">
              <span>{name}</span>
              <span style="color:#60A5FA;">{label}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No cards due in the next 14 days.")

    # Reset option
    st.markdown("---")
    with st.expander("⚠️ Reset Progress"):
        st.warning("This will delete all your spaced repetition data.")
        if st.button("Reset All Progress", type="primary"):
            import json, os
            progress_file = os.path.join(os.path.dirname(__file__), "..", "data", "progress.json")
            if os.path.exists(progress_file):
                os.remove(progress_file)
            st.session_state.progress = {"cards": {}, "sessions": [], "streak": 0, "last_study_date": ""}
            st.success("Progress reset.")
            st.rerun()
