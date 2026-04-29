"""
TriNetra AI — Streamlit Dashboard (Fixed)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

ROOT      = Path(__file__).resolve().parent.parent
DATA_PATH = Path(r"E:\Hack\TriNetra\data\processed\risk_scores.csv")
MRGD_PATH = Path(r"E:\Hack\TriNetra\data\processed\merged_features.csv")
SRC_PATH  = r"E:\Hack\TriNetra\src"
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
sys.path.insert(0, str(ROOT / "src"))

st.set_page_config(page_title="TriNetra AI", page_icon="🔺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0e1a; color: #e2e8f0; }
.risk-block  { background:linear-gradient(135deg,#7f1d1d,#450a0a);border:1px solid #ef4444;border-radius:12px;padding:16px;text-align:center; }
.risk-verify { background:linear-gradient(135deg,#78350f,#451a03);border:1px solid #f59e0b;border-radius:12px;padding:16px;text-align:center; }
.risk-approve{ background:linear-gradient(135deg,#14532d,#052e16);border:1px solid #22c55e;border-radius:12px;padding:16px;text-align:center; }
.header-glow { font-size:2.8rem;font-weight:900;background:linear-gradient(135deg,#818cf8,#c084fc,#fb7185);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
div[data-testid="stMetricValue"] { color:#818cf8 !important; font-size:2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Layout helpers ────────────────────────────────────────────────────────────
def dark_layout(fig, h=380):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#e2e8f0", title_font_color="#818cf8",
                      height=h, margin=dict(t=50,b=30,l=20,r=20))
    return fig

def gauge(score, title="Risk Score"):
    color = "#ef4444" if score > 70 else "#f59e0b" if score > 30 else "#22c55e"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        title={"text": title, "font": {"color": "#e2e8f0", "size": 16}},
        number={"font": {"color": color, "size": 48}},
        gauge={"axis": {"range": [0,100],"tickcolor":"#4b5563"},
               "bar": {"color": color,"thickness":0.3},"bgcolor":"#1e293b",
               "steps":[{"range":[0,30],"color":"rgba(34,197,94,0.15)"},
                        {"range":[30,70],"color":"rgba(245,158,11,0.15)"},
                        {"range":[70,100],"color":"rgba(239,68,68,0.15)"}],
               "threshold":{"line":{"color":color,"width":4},"value":score}}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      height=260,margin=dict(t=40,b=10,l=20,r=20),font={"color":"#e2e8f0"})
    return fig

# ── Data (no cache — always read fresh) ─────────────────────────────────────
def load_data():
    df  = pd.read_csv(DATA_PATH) if DATA_PATH.exists() else None
    mgd = pd.read_csv(MRGD_PATH) if MRGD_PATH.exists() else None
    return df, mgd

df, merged = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔺 TriNetra AI")
    st.markdown("*Hybrid Fraud Intelligence*")
    st.divider()
    page = st.radio("Navigate", ["🏠 Overview","🔍 User Lookup",
                                  "🌐 Fraud Rings","📈 Temporal Patterns",
                                  "🎯 Anomaly Map","⚡ Live Simulator"])
    st.divider()
    st.markdown("**Model Weights**")
    st.progress(0.30, "🕸️ Graph (GNN): 30%")
    st.progress(0.40, "⏱️ Temporal (LSTM): 40%")
    st.progress(0.30, "🔬 Anomaly (AE): 30%")
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.rerun()
    if df is not None:
        st.caption(f"✅ {len(df):,} users loaded")
        st.caption(f"Graph: {df['graph_risk_score'].mean():.1f} avg")
        st.caption(f"Risk: {df['risk_score'].mean():.1f} avg")

if df is None:
    st.error("⚠️ Run `python train.py` first.")
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown('<p class="header-glow">🔺 TriNetra AI</p>', unsafe_allow_html=True)
    st.markdown("### Real-Time Fraud Detection · GNN + LSTM + Autoencoder")
    st.divider()

    total    = len(df)
    blocked  = (df["decision"]=="BLOCK").sum()
    verify   = (df["decision"]=="VERIFY").sum()
    approved = (df["decision"]=="APPROVE").sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("👥 Total Users",  f"{total:,}")
    c2.metric("🚫 Blocked",      f"{blocked:,}", f"{blocked/total:.1%}")
    c3.metric("⚠️ Verify",       f"{verify:,}",  f"{verify/total:.1%}")
    c4.metric("✅ Approved",     f"{approved:,}", f"{approved/total:.1%}")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="risk_score", nbins=60,
                           color_discrete_sequence=["#818cf8"],
                           title="Risk Score Distribution")
        fig.add_vrect(x0=0,  x1=30,  fillcolor="rgba(34,197,94,0.1)",  line_width=0)
        fig.add_vrect(x0=30, x1=70,  fillcolor="rgba(245,158,11,0.1)", line_width=0)
        fig.add_vrect(x0=70, x1=100, fillcolor="rgba(239,68,68,0.1)",  line_width=0)
        fig.add_annotation(x=15,  y=0, text="APPROVE", showarrow=False, font=dict(color="#22c55e", size=10))
        fig.add_annotation(x=50,  y=0, text="VERIFY",  showarrow=False, font=dict(color="#f59e0b", size=10))
        fig.add_annotation(x=85,  y=0, text="BLOCK",   showarrow=False, font=dict(color="#ef4444", size=10))
        st.plotly_chart(dark_layout(fig), use_container_width=True)

    with col2:
        fig2 = px.pie(values=[approved,verify,blocked],
                      names=["Approve","Verify","Block"],
                      color_discrete_sequence=["#22c55e","#f59e0b","#ef4444"],
                      title="Decision Distribution", hole=0.55)
        st.plotly_chart(dark_layout(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Bar chart of component scores by decision (more informative than scatter)
        comp = df.groupby("decision")[["graph_risk_score","temporal_risk_score","anomaly_score"]].mean().reset_index()
        fig3 = px.bar(comp, x="decision", y=["graph_risk_score","temporal_risk_score","anomaly_score"],
                      barmode="group", title="Avg Component Score by Decision",
                      color_discrete_sequence=["#818cf8","#c084fc","#fb7185"],
                      labels={"value":"Score","variable":"Model"})
        st.plotly_chart(dark_layout(fig3), use_container_width=True)

    with col4:
        fig4 = px.box(df, x="decision", y="risk_score", color="decision",
                      color_discrete_map={"BLOCK":"#ef4444","VERIFY":"#f59e0b","APPROVE":"#22c55e"},
                      title="Risk Score by Decision")
        st.plotly_chart(dark_layout(fig4), use_container_width=True)

    st.markdown("### 🚨 Top 10 Highest-Risk Users")
    top10 = df.nlargest(10,"risk_score")[
        ["user_id","risk_score","decision","graph_risk_score","temporal_risk_score","anomaly_score","reason_str"]
    ].reset_index(drop=True)
    st.dataframe(top10, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# USER LOOKUP
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔍 User Lookup":
    st.markdown('<p class="header-glow">🔍 User Risk Lookup</p>', unsafe_allow_html=True)

    # Load surrogate for SHAP
    MODELS_DIR = Path(r"E:\Hack\TriNetra\models")
    shap_available = (MODELS_DIR / "shap_surrogate.pkl").exists()

    block_ids  = df[df["decision"]=="BLOCK"]["user_id"].head(5).tolist()
    verify_ids = df[df["decision"]=="VERIFY"]["user_id"].head(3).tolist()
    appr_ids   = df[df["decision"]=="APPROVE"]["user_id"].head(3).tolist()

    col_hint, col_input = st.columns([2,1])
    with col_hint:
        st.info(f"🚫 **Block** examples: `{'  |  '.join(map(str,block_ids))}`  \n"
                f"⚠️ **Verify** examples: `{'  |  '.join(map(str,verify_ids))}`  \n"
                f"✅ **Approve** examples: `{'  |  '.join(map(str,appr_ids))}`")
    with col_input:
        uid_input = st.text_input("Enter User ID", placeholder="e.g. 43")

    if uid_input:
        try:
            uid = int(uid_input)
            row = df[df["user_id"]==uid]
            if row.empty:
                st.warning(f"User {uid} not found.")
            else:
                row = row.iloc[0]
                score    = row["risk_score"]
                decision = row["decision"]
                css   = {"BLOCK":"risk-block","VERIFY":"risk-verify","APPROVE":"risk-approve"}[decision]
                emoji = {"BLOCK":"🚫","VERIFY":"⚠️","APPROVE":"✅"}[decision]

                st.divider()

                # ── TOP ROW: Gauge + Decision + Component Scores ──────────────
                gc1, gc2 = st.columns([1, 2])
                with gc1:
                    st.plotly_chart(gauge(score), use_container_width=True)
                    st.markdown(f'<div class="{css}"><h2 style="text-align:center">{emoji} {decision}</h2></div>',
                                unsafe_allow_html=True)
                with gc2:
                    st.markdown("#### Component Scores")
                    s1, s2, s3 = st.columns(3)
                    s1.metric("🕸️ Graph",    f"{row['graph_risk_score']:.1f}")
                    s2.metric("⏱️ Temporal", f"{row['temporal_risk_score']:.1f}")
                    s3.metric("🔬 Anomaly",  f"{row['anomaly_score']:.1f}")

                    # Component bar
                    fig_comp = go.Figure(go.Bar(
                        x=[row["graph_risk_score"], row["temporal_risk_score"], row["anomaly_score"]],
                        y=["Graph (GNN)", "Temporal (LSTM)", "Anomaly (AE)"],
                        orientation="h",
                        marker_color=["#818cf8","#c084fc","#fb7185"],
                        text=[f"{row['graph_risk_score']:.0f}",
                              f"{row['temporal_risk_score']:.0f}",
                              f"{row['anomaly_score']:.0f}"],
                        textposition="outside",
                    ))
                    fig_comp.update_xaxes(range=[0, 110])
                    fig_comp.update_layout(title="Model Component Scores")
                    st.plotly_chart(dark_layout(fig_comp, h=200), use_container_width=True)

                st.divider()

                # ── RISK REASONS ──────────────────────────────────────────────
                tab1, tab2, tab3 = st.tabs(["🧠 Risk Reasons", "📦 Return Analysis", "🔬 Explainable AI (SHAP)"])

                with tab1:
                    st.markdown("#### Why This Decision Was Made")
                    reasons = str(row["reason_str"]).split(" | ")
                    for i, r in enumerate(reasons):
                        color = "#ef4444" if decision == "BLOCK" else "#f59e0b" if decision == "VERIFY" else "#22c55e"
                        st.markdown(
                            f'<div style="background:rgba(99,102,241,0.1);border-left:3px solid {color};'
                            f'padding:10px;border-radius:6px;margin:6px 0">'
                            f'<b>#{i+1}</b> {r}</div>',
                            unsafe_allow_html=True
                        )

                with tab2:
                    st.markdown("#### 📦 Return Item Fraud Analysis")
                    if merged is not None:
                        mrow = merged[merged["user_id"] == uid]
                        if not mrow.empty:
                            mrow = mrow.iloc[0]
                            rc1, rc2, rc3, rc4 = st.columns(4)
                            rc1.metric("Total Returns",   f"{int(mrow.get('return_count', 0)):,}")
                            rc2.metric("Return Ratio",    f"{mrow.get('return_ratio', 0):.1%}")
                            rc3.metric("Avg Return Days", f"{mrow.get('avg_return_time', 0):.1f}")
                            rc4.metric("Wardrobing",      f"{int(mrow.get('wardrobing_count', 0))}")

                            # Return ratio gauge
                            rr = float(mrow.get("return_ratio", 0)) * 100
                            fig_rr = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=rr,
                                title={"text": "Return Ratio (%)", "font": {"color": "#e2e8f0"}},
                                number={"suffix": "%", "font": {"color": "#c084fc"}},
                                delta={"reference": 15, "suffix": "%"},
                                gauge={
                                    "axis": {"range": [0, 100]},
                                    "bar": {"color": "#c084fc"},
                                    "bgcolor": "#1e293b",
                                    "steps": [
                                        {"range": [0, 20],  "color": "rgba(34,197,94,0.15)"},
                                        {"range": [20, 50], "color": "rgba(245,158,11,0.15)"},
                                        {"range": [50, 100],"color": "rgba(239,68,68,0.15)"},
                                    ],
                                }
                            ))
                            fig_rr.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                                 font_color="#e2e8f0", height=220)
                            st.plotly_chart(fig_rr, use_container_width=True)

                            # Return fraud signals
                            st.markdown("##### Return Fraud Signals")
                            signals = []
                            if mrow.get("return_ratio", 0) > 0.5:
                                signals.append(("🔴 HIGH", "Return ratio above 50% — possible wardrobing"))
                            if mrow.get("wardrobing_count", 0) > 2:
                                signals.append(("🔴 HIGH", f"{int(mrow.get('wardrobing_count',0))} wardrobing returns flagged"))
                            if mrow.get("avg_return_time", 30) < 5:
                                signals.append(("🟠 MED", "Returns within 5 days — used & returned pattern"))
                            if mrow.get("return_count", 0) > 10:
                                signals.append(("🟠 MED", f"{int(mrow.get('return_count',0))} total returns — above normal"))
                            if not signals:
                                signals.append(("🟢 LOW", "No significant return fraud signals"))
                            for level, msg in signals:
                                st.markdown(f"**{level}** — {msg}")
                    else:
                        st.info("Merged features not available.")

                with tab3:
                    st.markdown("#### 🔬 Explainable AI — Score Decomposition")
                    st.markdown("*Exact breakdown of how each model contributed to the final risk score.*")

                    # ── Weighted contribution of each model ───────────────────
                    pop_graph    = float(df["graph_risk_score"].mean())
                    pop_temporal = float(df["temporal_risk_score"].mean())
                    pop_anomaly  = float(df["anomaly_score"].mean())
                    pop_base     = round(0.30*pop_graph + 0.40*pop_temporal + 0.30*pop_anomaly, 1)

                    user_graph    = float(row["graph_risk_score"])
                    user_temporal = float(row["temporal_risk_score"])
                    user_anomaly  = float(row["anomaly_score"])

                    contrib_graph    = round(0.30 * user_graph, 1)
                    contrib_temporal = round(0.40 * user_temporal, 1)
                    contrib_anomaly  = round(0.30 * user_anomaly, 1)

                    delta_graph    = round(contrib_graph    - 0.30*pop_graph,    1)
                    delta_temporal = round(contrib_temporal - 0.40*pop_temporal, 1)
                    delta_anomaly  = round(contrib_anomaly  - 0.30*pop_anomaly,  1)

                    # ── Chart 1: User vs Population grouped bar ───────────────
                    fig_cmp = go.Figure()
                    models_x   = ["Graph (GNN) ×30%", "Temporal (LSTM) ×40%", "Anomaly (AE) ×30%"]
                    user_pts   = [contrib_graph, contrib_temporal, contrib_anomaly]
                    pop_pts    = [round(0.30*pop_graph,1), round(0.40*pop_temporal,1), round(0.30*pop_anomaly,1)]

                    fig_cmp.add_trace(go.Bar(
                        name="Population Avg",
                        x=models_x, y=pop_pts,
                        marker_color="#4b5563",
                        text=[f"{v:.1f}" for v in pop_pts],
                        textposition="outside",
                    ))
                    fig_cmp.add_trace(go.Bar(
                        name=f"User {uid}",
                        x=models_x, y=user_pts,
                        marker_color=["#818cf8","#c084fc","#f472b6"],
                        text=[f"{v:.1f}" for v in user_pts],
                        textposition="outside",
                    ))
                    fig_cmp.update_layout(
                        barmode="group",
                        title=f"Weighted Score Contribution — User {uid} vs Population",
                        yaxis_title="Points contributed to Risk Score",
                        yaxis_range=[0, max(max(user_pts), max(pop_pts)) + 10],
                        legend=dict(orientation="h", y=1.1),
                    )
                    st.plotly_chart(dark_layout(fig_cmp, h=360), use_container_width=True)

                    # ── Chart 2: Stacked contribution showing final build-up ────
                    final_color = "#ef4444" if score > 70 else "#f59e0b" if score > 30 else "#22c55e"
                    fig_stack = go.Figure()
                    fig_stack.add_trace(go.Bar(
                        name="Graph (GNN)",
                        x=[f"User {uid}", "Avg User"],
                        y=[contrib_graph, round(0.30*pop_graph,1)],
                        marker_color="#818cf8",
                        text=[f"{contrib_graph:.1f}", f"{round(0.30*pop_graph,1):.1f}"],
                        textposition="inside", textfont=dict(color="white"),
                    ))
                    fig_stack.add_trace(go.Bar(
                        name="Temporal (LSTM)",
                        x=[f"User {uid}", "Avg User"],
                        y=[contrib_temporal, round(0.40*pop_temporal,1)],
                        marker_color="#c084fc",
                        text=[f"{contrib_temporal:.1f}", f"{round(0.40*pop_temporal,1):.1f}"],
                        textposition="inside", textfont=dict(color="white"),
                    ))
                    fig_stack.add_trace(go.Bar(
                        name="Anomaly (AE)",
                        x=[f"User {uid}", "Avg User"],
                        y=[contrib_anomaly, round(0.30*pop_anomaly,1)],
                        marker_color="#f472b6",
                        text=[f"{contrib_anomaly:.1f}", f"{round(0.30*pop_anomaly,1):.1f}"],
                        textposition="inside", textfont=dict(color="white"),
                    ))
                    fig_stack.update_layout(
                        barmode="stack",
                        title=f"Final Score Build-up: {score:.1f} vs avg {pop_base:.1f}",
                        yaxis_title="Risk Score",
                        yaxis_range=[0, 110],
                        legend=dict(orientation="h", y=1.1),
                    )
                    st.plotly_chart(dark_layout(fig_stack, h=360), use_container_width=True)

                    # ── Side-by-side comparison: User vs Population ───────────
                    st.markdown("##### 📊 User vs Population Average")
                    cmp_cols = st.columns(3)

                    for col, label, user_val, pop_val, weight in zip(
                        cmp_cols,
                        ["🕸️ Graph (GNN)", "⏱️ Temporal (LSTM)", "🔬 Anomaly (AE)"],
                        [user_graph, user_temporal, user_anomaly],
                        [pop_graph,  pop_temporal,  pop_anomaly],
                        [0.30, 0.40, 0.30]
                    ):
                        diff  = user_val - pop_val
                        arrow = "🔺" if diff > 5 else ("🔻" if diff < -5 else "➡️")
                        bcolor = "#ef4444" if diff > 5 else ("#22c55e" if diff < -5 else "#f59e0b")
                        col.markdown(
                            f'<div style="background:rgba(99,102,241,0.1);border:1px solid #374151;'
                            f'border-radius:10px;padding:14px;text-align:center">'
                            f'<div style="font-size:0.85rem;color:#9ca3af">{label}</div>'
                            f'<div style="font-size:2rem;font-weight:700;color:#e2e8f0">{user_val:.1f}</div>'
                            f'<div style="font-size:0.8rem;color:#6b7280">Pop avg: {pop_val:.1f}</div>'
                            f'<div style="color:{bcolor};font-weight:600">{arrow} {diff:+.1f} vs avg</div>'
                            f'<div style="font-size:0.75rem;color:#6b7280">Weight: {weight:.0%} → '
                            f'contributes <b>{weight*user_val:.1f}</b> pts</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    st.divider()
                    st.markdown(
                        f"**Formula:** `0.30 × {user_graph:.1f}` + `0.40 × {user_temporal:.1f}` + "
                        f"`0.30 × {user_anomaly:.1f}` = **{score:.1f}**  \n"
                        f"Population base: `0.30 × {pop_graph:.1f}` + `0.40 × {pop_temporal:.1f}` + "
                        f"`0.30 × {pop_anomaly:.1f}` = **{pop_base:.1f}**"
                    )


        except ValueError:
            st.error("Enter a valid numeric User ID.")


# ════════════════════════════════════════════════════════════════════════════
# FRAUD RINGS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Fraud Rings":
    st.markdown('<p class="header-glow">🌐 Fraud Ring Analysis</p>', unsafe_allow_html=True)
    st.markdown("Users connected via shared devices, IPs, or payment methods.")

    # Direct bucket counts — avoids pd.cut categorical issues
    bucket_df = pd.DataFrame({
        "Range": ["0–30", "31–50", "51–70", "71–85", "86–100"],
        "Users": [
            int((df["graph_risk_score"] <= 30).sum()),
            int(df["graph_risk_score"].between(31, 50).sum()),
            int(df["graph_risk_score"].between(51, 70).sum()),
            int(df["graph_risk_score"].between(71, 85).sum()),
            int((df["graph_risk_score"] > 85).sum()),
        ],
        "Color": ["#22c55e","#84cc16","#f59e0b","#f97316","#ef4444"]
    })

    c1,c2,c3 = st.columns(3)
    c1.metric("Total Users Analysed", f"{len(df):,}")
    c2.metric("High Graph Risk (>70)", f"{(df['graph_risk_score']>70).sum():,}",
              f"{(df['graph_risk_score']>70).mean():.1%}")
    c3.metric("BLOCK Decisions", f"{(df['decision']=='BLOCK').sum():,}")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(bucket_df, x="Range", y="Users",
                     color="Range",
                     color_discrete_sequence=["#22c55e","#84cc16","#f59e0b","#f97316","#ef4444"],
                     title="Graph Risk Score Buckets",
                     text="Users",
                     labels={"Range":"Graph Risk Range","Users":"Number of Users"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(dark_layout(fig), use_container_width=True)

    with col2:
        # Histogram of final risk score split by ring membership
        df2 = df.copy()
        df2["ring_member"] = df2["graph_risk_score"] > 70
        df2["ring_label"] = df2["ring_member"].map({True: "Ring Member", False: "Normal"})
        fig2 = px.histogram(df2, x="risk_score", color="ring_label", nbins=50,
                            barmode="overlay", opacity=0.75,
                            color_discrete_map={"Ring Member":"#ef4444","Normal":"#818cf8"},
                            title="Final Risk Score: Ring Members vs Others",
                            labels={"ring_label":"User Type","risk_score":"Risk Score (0-100)"})
        st.plotly_chart(dark_layout(fig2), use_container_width=True)

    st.markdown("### 🔴 Top Suspected Fraud Ring Members")
    top_ring = df.nlargest(20,"graph_risk_score")[
        ["user_id","graph_risk_score","temporal_risk_score","anomaly_score","risk_score","decision","reason_str"]
    ].reset_index(drop=True)
    st.dataframe(top_ring, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TEMPORAL PATTERNS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📈 Temporal Patterns":
    st.markdown('<p class="header-glow">📈 Temporal Behavior</p>', unsafe_allow_html=True)

    # Temporal score distribution
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="temporal_risk_score", nbins=60,
                           color_discrete_sequence=["#c084fc"],
                           title="Temporal Risk Score Distribution")
        fig.add_vline(x=70, line_dash="dash", line_color="#ef4444",
                      annotation_text="High Risk Threshold")
        st.plotly_chart(dark_layout(fig), use_container_width=True)

    with col2:
        # Temporal vs Anomaly coloured by decision
        fig2 = px.scatter(df.sample(min(2000,len(df))),
                          x="temporal_risk_score", y="anomaly_score",
                          color="decision", opacity=0.6,
                          color_discrete_map={"BLOCK":"#ef4444","VERIFY":"#f59e0b","APPROVE":"#22c55e"},
                          title="Temporal Score vs Anomaly Score",
                          size_max=8)
        st.plotly_chart(dark_layout(fig2), use_container_width=True)

    # Raw feature bars from merged (unscaled categorical flags)
    if merged is not None:
        # Re-derive flags directly from raw values (not scaled)
        raw_path = ROOT / "data" / "raw" / "fraud_transactions.csv"
        if raw_path.exists():
            col3, col4 = st.columns(2)
            raw = pd.read_csv(raw_path, usecols=["user_id","is_fraud"] if "is_fraud" in pd.read_csv(raw_path, nrows=1).columns else ["user_id"])
            with col3:
                night_users = (df["temporal_risk_score"] > 60).sum()
                normal_users = len(df) - night_users
                fig3 = px.pie(values=[normal_users, night_users],
                              names=["Normal Temporal","High Temporal Risk"],
                              color_discrete_sequence=["#22c55e","#ef4444"],
                              title="Temporal Risk Split", hole=0.5)
                st.plotly_chart(dark_layout(fig3), use_container_width=True)
            with col4:
                blocks = df[df["decision"]=="BLOCK"]["temporal_risk_score"]
                verify = df[df["decision"]=="VERIFY"]["temporal_risk_score"]
                fig4 = go.Figure()
                fig4.add_trace(go.Box(y=verify.values, name="VERIFY", marker_color="#f59e0b"))
                fig4.add_trace(go.Box(y=blocks.values, name="BLOCK",  marker_color="#ef4444"))
                fig4.update_layout(title="Temporal Score by Decision")
                st.plotly_chart(dark_layout(fig4), use_container_width=True)
        else:
            st.info("Raw transaction file not found for deeper temporal analysis.")

# ════════════════════════════════════════════════════════════════════════════
# ANOMALY MAP
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Anomaly Map":
    st.markdown('<p class="header-glow">🎯 Anomaly Detection</p>', unsafe_allow_html=True)
    st.markdown("Autoencoder trained on **normal users only** — high reconstruction error = fraud.")

    high_anom = (df["anomaly_score"] > 60).sum()
    c1,c2,c3 = st.columns(3)
    c1.metric("High-Anomaly Users (>60)", f"{high_anom:,}", f"{high_anom/len(df):.1%}")
    c2.metric("Mean Anomaly Score", f"{df['anomaly_score'].mean():.1f}")
    c3.metric("Max Anomaly Score",  f"{df['anomaly_score'].max():.1f}")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="anomaly_score", nbins=60,
                           color_discrete_sequence=["#f472b6"],
                           title="Anomaly Score Distribution")
        fig.add_vline(x=60, line_dash="dash", line_color="#ef4444",
                      annotation_text="High Anomaly Threshold (60)")
        fig.add_vline(x=30, line_dash="dot",  line_color="#f59e0b",
                      annotation_text="Medium Threshold (30)")
        st.plotly_chart(dark_layout(fig), use_container_width=True)

    with col2:
        # Anomaly vs final risk score — most revealing chart
        fig2 = px.scatter(df, x="anomaly_score", y="risk_score",
                          color="decision", opacity=0.6,
                          color_discrete_map={"BLOCK":"#ef4444","VERIFY":"#f59e0b","APPROVE":"#22c55e"},
                          title="Anomaly Score vs Final Risk Score")
        fig2.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="BLOCK threshold")
        fig2.add_vline(x=60, line_dash="dash", line_color="#f472b6", annotation_text="High anomaly")
        st.plotly_chart(dark_layout(fig2), use_container_width=True)

    # Top anomalous users
    st.markdown("### 🔬 Most Anomalous Users")
    top_anom = df.nlargest(15,"anomaly_score")[
        ["user_id","anomaly_score","graph_risk_score","temporal_risk_score","risk_score","decision"]
    ].reset_index(drop=True)
    st.dataframe(top_anom, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LIVE SIMULATOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Live Simulator":
    st.markdown('<p class="header-glow">⚡ Live Transaction Simulator</p>', unsafe_allow_html=True)
    st.markdown("Adjust the sliders and click **Analyze** to get an instant risk score.")

    col1, col2 = st.columns(2)
    with col1:
        txn_amount   = st.slider("💰 Transaction Amount (₹)", 100, 100000, 5000, step=500)
        hour         = st.slider("🕐 Transaction Hour (0–23)", 0, 23, 14)
        return_ratio = st.slider("📦 Return Ratio (0=never, 1=always)", 0.0, 1.0, 0.1, 0.05)
        unique_devs  = st.slider("📱 Unique Devices Used", 1, 15, 1)
    with col2:
        unique_ips   = st.slider("🌐 Unique IPs Used", 1, 20, 1)
        txn_count    = st.slider("🔢 Total Transactions", 1, 500, 20)
        shared_users = st.slider("👥 Accounts Sharing Same Device/IP", 0, 25, 0)
        payment      = st.selectbox("💳 Payment Method",
                                    ["UPI","Credit Card","Wallet","Net Banking","Gift Card"])

    analyze = st.button("🔍 Analyze Transaction", type="primary", use_container_width=True)

    if analyze:
        night_flag = 1 if (hour >= 22 or hour <= 4) else 0
        hv_flag    = 1 if txn_amount > 15000 else 0
        burst_flag = 1 if txn_count > 150 else 0
        gift_flag  = 1 if payment == "Gift Card" else 0

        graph_score    = min((shared_users/25.0*55) + (unique_devs/15.0*25) + (unique_ips/20.0*20), 100)
        temporal_score = min((night_flag*35) + (burst_flag*25) + (return_ratio*35) + (hv_flag*15) + (gift_flag*10), 100)
        anomaly_score  = min((return_ratio*45) + (unique_devs/15.0*30) + (hv_flag*25), 100)
        risk_score     = round(0.30*graph_score + 0.40*temporal_score + 0.30*anomaly_score, 1)
        decision       = "BLOCK" if risk_score > 70 else "VERIFY" if risk_score > 30 else "APPROVE"

        st.divider()
        r1, r2, r3 = st.columns(3)
        r1.metric("🕸️ Graph Score",    f"{graph_score:.1f} / 100")
        r2.metric("⏱️ Temporal Score", f"{temporal_score:.1f} / 100")
        r3.metric("🔬 Anomaly Score",  f"{anomaly_score:.1f} / 100")

        gc1, gc2 = st.columns([1,2])
        with gc1:
            st.plotly_chart(gauge(risk_score), use_container_width=True)
            css   = {"BLOCK":"risk-block","VERIFY":"risk-verify","APPROVE":"risk-approve"}[decision]
            emoji = {"BLOCK":"🚫","VERIFY":"⚠️","APPROVE":"✅"}[decision]
            st.markdown(f'<div class="{css}"><h2>{emoji} {decision}</h2></div>', unsafe_allow_html=True)

        with gc2:
            # Component breakdown bar
            fig_bar = go.Figure(go.Bar(
                x=[graph_score, temporal_score, anomaly_score],
                y=["Graph (GNN)", "Temporal (LSTM)", "Anomaly (AE)"],
                orientation="h",
                marker_color=["#818cf8","#c084fc","#f472b6"],
                text=[f"{graph_score:.0f}",f"{temporal_score:.0f}",f"{anomaly_score:.0f}"],
                textposition="outside"
            ))
            fig_bar.update_xaxes(range=[0,110])
            fig_bar.update_layout(title="Component Score Breakdown")
            st.plotly_chart(dark_layout(fig_bar, h=220), use_container_width=True)

            st.markdown("#### 🧠 Risk Signals Detected")
            signals = []
            if shared_users > 3:   signals.append(f"🔗 Linked to {shared_users} accounts via shared device/IP")
            if night_flag:         signals.append("🌙 Late-night transaction (10PM–5AM)")
            if burst_flag:         signals.append("💥 Transaction burst behavior detected")
            if return_ratio > 0.4: signals.append(f"📦 High return ratio ({return_ratio:.0%})")
            if hv_flag:            signals.append(f"💰 High-value transaction ₹{txn_amount:,}")
            if unique_devs > 3:    signals.append(f"📱 {unique_devs} unique devices used")
            if unique_ips > 3:     signals.append(f"🌐 {unique_ips} unique IPs detected")
            if gift_flag:          signals.append("🎁 Gift card payment (high-risk method)")
            if not signals:        signals.append("✅ No significant risk signals detected")
            for s in signals:
                st.markdown(f"&nbsp;&nbsp;• {s}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("<p style='text-align:center;color:#4b5563;font-size:0.85rem'>"
            "🔺 TriNetra AI · GNN + LSTM + Autoencoder · Hybrid Fraud Intelligence</p>",
            unsafe_allow_html=True)
