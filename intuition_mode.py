"""
Intuition Mode — Deep conceptual understanding + interactive plots.
Shows the 'why' behind each formula with visual context.
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.scheduler import load_all_cards, get_topics


def render_intuition():
    all_cards = st.session_state.all_cards

    if st.button("← Back", use_container_width=False):
        st.session_state.mode = "home"
        st.rerun()

    st.markdown("### 💡 Deep Dive — Formula Intuition")

    topics = get_topics(all_cards)
    selected_topic = st.selectbox("Topic:", topics)
    topic_cards = [c for c in all_cards if c.get("topic") == selected_topic]

    card_names = [c.get("name", c["id"]) for c in topic_cards]
    selected_name = st.selectbox("Formula / Concept:", card_names)
    card = next((c for c in topic_cards if c.get("name") == selected_name), None)

    if not card:
        return

    # Formula display
    st.markdown(f"""
    <div class="card-formula">{card.get('formula','')}</div>
    """, unsafe_allow_html=True)

    # Intuition
    st.markdown(f"""
    <div class="intuition-box">
      💡 <b>The Deep Why</b><br><br>
      {card.get('intuition','').replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

    # Memory hook
    st.markdown(f"""
    <div class="hook-box">🎯 <b>Memory Hook:</b> {card.get('memory_hook','')}</div>
    """, unsafe_allow_html=True)

    # ─── INTERACTIVE PLOTS ──────────────────────────────────
    card_id = card.get("id", "")

    if card_id in ["fi_003", "fi_005"]:
        _plot_duration_convexity()
    elif card_id == "fi_001":
        _plot_bond_price_yield()
    elif card_id == "eq_001":
        _plot_ggm_sensitivity()
    elif card_id == "qm_001":
        _plot_compound_growth()
    elif card_id == "qm_006":
        _plot_am_vs_gm()
    elif card_id == "eq_003":
        _plot_dupont_decomposition()
    elif card_id in ["fsa_006", "fsa_007"]:
        _plot_depreciation_comparison()
    elif card_id == "fi_008":
        _plot_duration_gap()


def _plot_bond_price_yield():
    st.markdown("#### 📈 Bond Price vs. Yield (Interactive)")
    coupon = st.slider("Coupon Rate (%)", 1, 15, 6) / 100
    maturity = st.slider("Maturity (years)", 1, 30, 10)
    face = 1000

    yields = np.linspace(0.01, 0.20, 200)
    prices = []
    for y in yields:
        pv = sum([face * coupon / (1 + y)**t for t in range(1, maturity + 1)])
        pv += face / (1 + y)**maturity
        prices.append(pv)

    par_yield = coupon
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yields * 100, y=prices, mode='lines',
                             line=dict(color='#60A5FA', width=2.5), name='Bond Price'))
    fig.add_hline(y=face, line_dash="dash", line_color="#F59E0B",
                  annotation_text="Par ($1,000)")
    fig.add_vline(x=par_yield * 100, line_dash="dash", line_color="#10B981",
                  annotation_text=f"Coupon = {coupon*100:.0f}%")
    fig.update_layout(
        xaxis_title="Yield to Maturity (%)",
        yaxis_title="Price ($)",
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=320,
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Notice the convex curve — price drops less for a yield increase than it rises for an equivalent decrease.")


def _plot_duration_convexity():
    st.markdown("#### 📈 Duration vs. Convexity Approximation")
    mod_dur = st.slider("Modified Duration", 1.0, 15.0, 7.0, 0.5)
    convexity = st.slider("Convexity", 0, 200, 80, 10)

    yield_changes = np.linspace(-0.03, 0.03, 100)
    duration_only = -mod_dur * yield_changes * 100
    with_convexity = (-mod_dur * yield_changes + 0.5 * convexity * yield_changes**2) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yield_changes * 100, y=duration_only,
                             mode='lines', name='Duration only',
                             line=dict(color='#EF4444', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=yield_changes * 100, y=with_convexity,
                             mode='lines', name='Duration + Convexity',
                             line=dict(color='#60A5FA', width=2.5)))
    fig.add_hline(y=0, line_color='#475569')
    fig.add_vline(x=0, line_color='#475569')
    fig.update_layout(
        xaxis_title="Yield Change (bps / 100)",
        yaxis_title="% Price Change",
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=300,
        legend=dict(bgcolor='#0F172A')
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Convexity (blue) always beats duration-only (red). The gap is larger for big yield moves.")


def _plot_ggm_sensitivity():
    st.markdown("#### 📈 GGM — How Value Changes with Growth & Required Return")
    d1 = st.slider("D₁ (next dividend $)", 0.5, 5.0, 2.0, 0.1)
    ke = st.slider("Required Return Ke (%)", 5, 20, 12) / 100

    growth_rates = np.linspace(0.01, ke - 0.005, 50)
    values = d1 / (ke - growth_rates)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=growth_rates * 100, y=values,
                             mode='lines', line=dict(color='#10B981', width=2.5),
                             name='Intrinsic Value'))
    fig.update_layout(
        xaxis_title="Growth Rate g (%)",
        yaxis_title="Intrinsic Value V₀ ($)",
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=280,
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"At Ke={ke*100:.0f}%, value explodes as g approaches Ke. Never plug in g ≥ Ke!")


def _plot_compound_growth():
    st.markdown("#### 📈 Power of Compounding")
    pv = st.slider("Initial Investment ($)", 1000, 50000, 10000, 1000)
    rate = st.slider("Annual Rate (%)", 1, 20, 8) / 100
    years = st.slider("Years", 5, 40, 20)

    t = np.arange(0, years + 1)
    compound = pv * (1 + rate)**t
    simple = pv * (1 + rate * t)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=compound, mode='lines',
                             line=dict(color='#60A5FA', width=2.5), name='Compound'))
    fig.add_trace(go.Scatter(x=t, y=simple, mode='lines',
                             line=dict(color='#94A3B8', width=1.5, dash='dash'), name='Simple'))
    fig.update_layout(
        xaxis_title="Years",
        yaxis_title="Value ($)",
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=280,
        legend=dict(bgcolor='#0F172A')
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    final = pv * (1 + rate)**years
    st.caption(f"${pv:,.0f} at {rate*100:.0f}% for {years} years = **${final:,.0f}**. Simple interest gives only ${pv*(1+rate*years):,.0f}.")


def _plot_am_vs_gm():
    st.markdown("#### 📈 AM vs GM — Why Geometric Mean Tells the Truth")
    r1 = st.slider("Year 1 Return (%)", -50, 100, 50) / 100
    r2 = st.slider("Year 2 Return (%)", -50, 100, -33) / 100

    am = (r1 + r2) / 2
    gm = ((1 + r1) * (1 + r2))**0.5 - 1
    wealth = 1000 * (1 + r1) * (1 + r2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Arith Mean", f"{am*100:.1f}%")
    col2.metric("Geo Mean", f"{gm*100:.1f}%")
    col3.metric("$1000 → ", f"${wealth:.0f}")

    st.info(f"Starting with $1,000: after +{r1*100:.0f}% then {r2*100:.0f}%, you end up with **${wealth:.0f}**. "
            f"Arithmetic mean says {am*100:.1f}% per year — which would give ${1000*(1+am)**2:.0f}. "
            f"Only the geometric mean ({gm*100:.1f}%) correctly predicts your actual ending wealth.")


def _plot_dupont_decomposition():
    st.markdown("#### 📊 DuPont Decomposition — Visualize ROE Drivers")
    margin = st.slider("Net Profit Margin (%)", 1, 30, 10) / 100
    turnover = st.slider("Asset Turnover (x)", 0.5, 3.0, 1.5, 0.1)
    leverage = st.slider("Financial Leverage (x)", 1.0, 5.0, 2.0, 0.1)
    roe = margin * turnover * leverage

    fig = go.Figure(go.Bar(
        x=["Net Profit Margin", "Asset Turnover", "Fin. Leverage", "ROE"],
        y=[margin * 100, turnover * 10, leverage * 5, roe * 100],
        marker_color=['#2563EB', '#10B981', '#F59E0B', '#EF4444'],
        text=[f"{margin*100:.1f}%", f"{turnover:.1f}x", f"{leverage:.1f}x", f"{roe*100:.1f}%"],
        textposition='outside'
    ))
    fig.update_layout(
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=280,
        showlegend=False,
    )
    fig.update_yaxes(showticklabels=False, gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"ROE = {margin*100:.1f}% × {turnover:.1f}x × {leverage:.1f}x = **{roe*100:.1f}%**")


def _plot_depreciation_comparison():
    st.markdown("#### 📈 Straight-Line vs Double-Declining Balance")
    cost = st.slider("Asset Cost ($K)", 100, 1000, 500, 50)
    salvage = st.slider("Salvage Value ($K)", 0, 200, 50, 10)
    life = st.slider("Useful Life (years)", 3, 20, 10)

    years = list(range(1, life + 1))
    sl_dep = [(cost - salvage) / life] * life

    ddb_dep = []
    bv = cost
    for y in years:
        d = bv * 2 / life
        sl_remaining = (bv - salvage) / (life - y + 1)
        d = max(d, sl_remaining) if bv - d < salvage else d
        d = min(d, bv - salvage)
        ddb_dep.append(d)
        bv -= d

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Straight-Line', x=years, y=sl_dep,
                         marker_color='#2563EB', opacity=0.8))
    fig.add_trace(go.Bar(name='DDB', x=years, y=ddb_dep,
                         marker_color='#F59E0B', opacity=0.8))
    fig.update_layout(
        barmode='group',
        xaxis_title="Year",
        yaxis_title="Depreciation ($K)",
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=40),
        height=280,
        legend=dict(bgcolor='#0F172A')
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("DDB front-loads expenses → lower taxable income early → deferred taxes (DTL). Converges to SL over time.")


def _plot_duration_gap():
    st.markdown("#### 📈 Duration Gap & Risk Exposure")
    investment_horizon = st.slider("Investment Horizon (years)", 1, 20, 7)
    mac_dur = st.slider("Macaulay Duration (years)", 1, 20, 10)

    gap = mac_dur - investment_horizon
    gap_color = "#EF4444" if gap > 0 else "#10B981" if gap < 0 else "#F59E0B"
    gap_label = "Price Risk Dominates" if gap > 0 else "Reinvestment Risk Dominates" if gap < 0 else "Immunized ✓"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Investment Horizon", "Macaulay Duration"],
        y=[investment_horizon, mac_dur],
        marker_color=['#2563EB', '#F59E0B'],
        text=[f"{investment_horizon}y", f"{mac_dur}y"],
        textposition='outside'
    ))
    fig.update_layout(
        plot_bgcolor='#0F172A', paper_bgcolor='#1E293B',
        font=dict(color='#CBD5E1'),
        margin=dict(l=10, r=10, t=20, b=60),
        height=240,
        showlegend=False,
        annotations=[dict(
            text=f"Gap = {gap:+.0f}y | {gap_label}",
            x=0.5, y=-0.25, xref='paper', yref='paper',
            showarrow=False, font=dict(color=gap_color, size=13)
        )]
    )
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)
