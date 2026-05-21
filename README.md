# 📊 CFA Deep Memory System

A science-based spaced repetition app for CFA Level I — built for mobile study during commutes.

## Scientific Methods Used
| Technique | Implementation |
|---|---|
| Spaced Repetition (SM-2) | Algorithm schedules each card individually |
| Active Recall | Cards hide the answer; you reconstruct it |
| Interleaving | Sessions mix topics automatically |
| Testing Effect | Multiple choice + numeric exercises |
| Elaborative Encoding | Every card has intuition + memory hook |
| Visual Learning | Interactive Plotly plots per formula |

## Topics Covered
- **Quantitative Methods** — TVM, Returns, Statistics, Hypothesis Testing, Regression
- **Fixed Income** — Bond Valuation, Duration, Convexity, Spreads, Credit
- **Equity Investments** — DDM, GGM, DuPont, FCF, Multiples, Leverage
- **Financial Statement Analysis** — Cash Flows, Ratios, Inventory, Depreciation, Taxes

## Project Structure
```
cfa_memory_system/
├── app.py                    # Main entry point
├── requirements.txt
├── .streamlit/config.toml    # Dark mobile theme
├── core/
│   ├── sm2.py               # SM-2 algorithm
│   ├── session_manager.py   # Progress persistence
│   └── scheduler.py         # Content loader
├── content/
│   ├── formulas/            # YAML card files per topic
│   ├── concepts/            # Principle/theorem cards
│   └── exercises/           # Numeric exercises
├── modes/
│   ├── flashcard_mode.py    # Active recall + SM-2
│   ├── exercise_mode.py     # Numeric problems
│   ├── intuition_mode.py    # Deep dive + plots
│   └── review_summary.py   # Progress dashboard
└── data/
    └── progress.json        # Your study progress
```

## Deploy to Streamlit Cloud

1. Fork or push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path**: `app.py`
5. Deploy — done

> ⚠️ **Note on progress persistence:** Streamlit Community Cloud resets the filesystem on each redeploy. For persistent progress across sessions, consider upgrading `data/progress.json` to use `st.session_state` with browser cookies, or connect a free Supabase/Firebase database. For personal use on a single device, progress persists within each session.

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Add More Cards
Edit any YAML file in `content/formulas/` following this structure:
```yaml
- id: unique_id
  topic: Fixed Income
  subtopic: Duration
  name: Card Title
  formula: "formula text"
  latex: "latex_string"
  intuition: "Why this formula works..."
  memory_hook: "Short memorable phrase"
  tags: [tag1, tag2]
  options:
    - "Option A"
    - "Option B (correct)"
    - "Option C"
    - "Option D"
  correct_option: 1
```
