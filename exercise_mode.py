"""
Exercise Mode — CFA-style numeric problems with step-by-step solutions.
Supports both multiple choice and numeric input validation.
"""
import streamlit as st
import random
from core.scheduler import load_all_exercises


def render_exercise():
    exercises = st.session_state.all_exercises

    if st.button("← Back", use_container_width=False):
        st.session_state.mode = "home"
        st.rerun()

    if not exercises:
        st.info("No exercises found. Check content/exercises/ folder.")
        return

    # Topic filter
    topics = sorted(set(e.get("topic", "All") for e in exercises))
    selected_topic = st.selectbox("Filter by topic:", ["All"] + topics)

    filtered = exercises if selected_topic == "All" else [
        e for e in exercises if e.get("topic") == selected_topic
    ]

    if not filtered:
        st.info("No exercises for this topic yet.")
        return

    # Shuffle mode or sequential
    if "ex_order" not in st.session_state or st.session_state.get("ex_topic") != selected_topic:
        order = list(range(len(filtered)))
        random.shuffle(order)
        st.session_state.ex_order = order
        st.session_state.ex_topic = selected_topic
        st.session_state.ex_pos = 0
        st.session_state.show_ex_answer = False

    pos = st.session_state.get("ex_pos", 0) % len(filtered)
    ex = filtered[st.session_state.ex_order[pos]]

    total = len(filtered)
    current = pos + 1

    # Progress
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; color:#94A3B8; font-size:0.8rem; margin-bottom:12px;">
      <span>Exercise {current} of {total}</span>
      <span>{ex.get('topic','')} · {ex.get('subtopic','')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Difficulty badge
    diff = ex.get("difficulty", "medium")
    diff_color = {"easy": "#10B981", "medium": "#F59E0B", "hard": "#EF4444"}.get(diff, "#94A3B8")
    st.markdown(f"""
    <span style="background:{diff_color}22; color:{diff_color}; 
                 padding:2px 10px; border-radius:999px; font-size:0.75rem; font-weight:700;">
      {diff.upper()}
    </span>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"### {ex.get('question','')}")

    # Given values
    given = ex.get("given", {})
    if given:
        with st.expander("📋 Given values", expanded=True):
            for k, v in given.items():
                st.markdown(f"- **{k}** = {v}")

    # Answer options (Multiple Choice)
    options = ex.get("options", [])
    correct_idx = ex.get("correct_option", 0)

    if not st.session_state.show_ex_answer:
        if options:
            st.markdown("**Select your answer:**")
            for i, opt in enumerate(options):
                label = f"{chr(65+i)}. {opt}"
                if st.button(label, key=f"ex_opt_{pos}_{i}", use_container_width=True):
                    st.session_state.ex_selected = i
                    st.session_state.show_ex_answer = True
                    st.rerun()
        else:
            # Numeric input
            user_answer = st.text_input("Your answer:", placeholder="e.g. 1051.54")
            if st.button("Check Answer ✓", use_container_width=True):
                st.session_state.ex_selected = user_answer
                st.session_state.show_ex_answer = True
                st.rerun()

    else:
        selected = st.session_state.get("ex_selected", -1)

        if options:
            if selected == correct_idx:
                st.success(f"✅ **Correct!** {options[correct_idx]}")
            else:
                st.error(f"❌ You chose: {options[selected] if isinstance(selected, int) else selected}")
                st.success(f"✅ Correct answer: **{options[correct_idx]}**")
        
        # Step-by-step solution
        st.markdown("---")
        st.markdown("**📐 Step-by-step solution:**")
        steps = ex.get("solution_steps", [])
        for i, step in enumerate(steps):
            st.markdown(f"""
            <div style="background:#0F172A; border-left:3px solid #2563EB; 
                        border-radius:0 8px 8px 0; padding:10px 12px; margin:6px 0;
                        font-family: monospace; font-size:0.9rem;">
              <span style="color:#64748B; font-size:0.75rem;">Step {i+1}</span><br>
              <span style="color:#E2E8F0;">{step}</span>
            </div>
            """, unsafe_allow_html=True)

        if ex.get("note"):
            st.markdown(f"""
            <div class="hook-box">💡 <b>Pro tip:</b> {ex['note']}</div>
            """, unsafe_allow_html=True)

        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.ex_pos = (pos - 1) % total
                st.session_state.show_ex_answer = False
                st.session_state.ex_selected = None
                st.rerun()
        with col2:
            if st.button("Next Exercise →", use_container_width=True):
                st.session_state.ex_pos = (pos + 1) % total
                st.session_state.show_ex_answer = False
                st.session_state.ex_selected = None
                st.rerun()
