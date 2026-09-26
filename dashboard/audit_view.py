from datetime import datetime, timezone
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Enterprise Page Config & Antigravity Spatial Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PromptArmor | Enterprise SOC Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Deep Space Cyber Mesh & Glassmorphism Stylesheet
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* Base Canvas & Spatial Atmosphere */
        .stApp {
            background-color: #06080e;
            background-image: 
                radial-gradient(at 10% 10%, rgba(14, 165, 233, 0.08) 0px, transparent 40%),
                radial-gradient(at 85% 15%, rgba(244, 63, 94, 0.08) 0px, transparent 40%),
                radial-gradient(at 50% 85%, rgba(168, 85, 247, 0.06) 0px, transparent 45%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 100% 100%, 48px 48px, 48px 48px;
            color: #f1f5f9;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }

        /* Typography Hierarchy */
        h1, h2, h3 {
            font-family: 'Chakra Petch', 'Plus Jakarta Sans', sans-serif !important;
            letter-spacing: -0.02em;
        }
        code, pre, .stCode, .tabular-mono {
            font-family: 'JetBrains Mono', monospace !important;
            font-variant-numeric: tabular-nums;
        }

        /* Top HUD Navigation Bar */
        .hud-header {
            background: rgba(13, 18, 30, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.5);
        }
        .hud-title {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .hud-subtitle {
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-top: 4px;
        }

        /* Pulsing Radar Beacon */
        .radar-ping {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: #34d399;
            text-transform: uppercase;
        }
        .radar-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
            animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse-ring {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.3); }
        }

        /* Antigravity Floating Glass KPI Cards */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-bottom: 24px;
        }
        .kpi-card {
            background: linear-gradient(135deg, rgba(18, 24, 40, 0.75) 0%, rgba(11, 15, 26, 0.85) 100%);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 16px;
            padding: 22px 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease, border-color 0.35s ease;
        }
        .kpi-card:hover {
            transform: translateY(-6px);
            border-color: rgba(255, 255, 255, 0.2);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
        }
        .kpi-blue::before { background: linear-gradient(90deg, #38bdf8, transparent); }
        .kpi-blue:hover { box-shadow: 0 20px 45px -10px rgba(56, 189, 248, 0.25); }
        .kpi-red::before { background: linear-gradient(90deg, #f43f5e, transparent); }
        .kpi-red:hover { box-shadow: 0 20px 45px -10px rgba(244, 63, 94, 0.3); }
        .kpi-amber::before { background: linear-gradient(90deg, #f59e0b, transparent); }
        .kpi-amber:hover { box-shadow: 0 20px 45px -10px rgba(245, 158, 11, 0.25); }
        .kpi-purple::before { background: linear-gradient(90deg, #a855f7, transparent); }
        .kpi-purple:hover { box-shadow: 0 20px 45px -10px rgba(168, 85, 247, 0.25); }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .kpi-label {
            color: #94a3b8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .kpi-icon {
            font-size: 18px;
            opacity: 0.9;
        }
        .kpi-number {
            font-size: 36px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
            line-height: 1;
            margin-bottom: 10px;
        }
        .kpi-meta {
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Glass Panel for Charts & Sections */
        .glass-panel {
            background: rgba(14, 20, 34, 0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 24px;
            box-shadow: 0 14px 35px -10px rgba(0, 0, 0, 0.45);
        }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 12px;
        }
        .panel-title {
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
        }
        .panel-badge {
            background: rgba(255, 255, 255, 0.06);
            color: #cbd5e1;
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        }

        /* Sidebar Mission Control */
        section[data-testid="stSidebar"] {
            background-color: rgba(9, 13, 22, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        .policy-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
            transition: all 0.25s ease;
        }
        .policy-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.15);
        }
        .policy-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            font-weight: 700;
            color: #f8fafc;
        }
        .policy-sub {
            color: #94a3b8;
            font-size: 11px;
            margin-top: 3px;
        }
        .policy-tag {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
        }

        /* Code & Streamlit Widget Customization */
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            overflow: hidden;
        }
        .stSelectbox label, .stTextInput label {
            color: #cbd5e1 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

GATEWAY_API_URL = "http://127.0.0.1:8000"
DB_PATH = "data/security_logs.db"


# -----------------------------------------------------------------------------
# Data Ingestion Engine with Fail-Closed Fallback
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3)
def fetch_audit_data() -> pd.DataFrame:
    """Retrieves live forensics data with REST primary and SQLite fallback."""
    # Attempt 1: Query Gateway REST API
    try:
        res = requests.get(
            f"{GATEWAY_API_URL}/v1/audit/logs?limit=1000", timeout=1.5
        )
        if res.status_code == 200:
            raw_data = res.json()
            if raw_data:
                df = pd.DataFrame(raw_data)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                return df
    except Exception:
        pass

    # Attempt 2: Direct SQLite Query Fallback
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM audit_events ORDER BY id DESC LIMIT 1000", conn
        )
        conn.close()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
    except Exception:
        pass

    return pd.DataFrame()


# -----------------------------------------------------------------------------
# Sidebar Navigation & Gateway Status
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <div style="background: linear-gradient(135deg, #38bdf8, #818cf8); padding: 8px; border-radius: 10px; font-size: 20px;">🛡️</div>
            <div>
                <div style="font-size: 18px; font-weight: 800; color: #fff; letter-spacing: -0.01em;">PromptArmor</div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">Autonomous LLM Gateway Sentinel</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Gateway Health Probe
    gateway_online = False
    try:
        health_resp = requests.get(f"{GATEWAY_API_URL}/health", timeout=1)
        if health_resp.status_code == 200:
            gateway_online = True
    except Exception:
        gateway_online = False

    if gateway_online:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 12px 14px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #34d399; font-weight: 700; font-size: 12px;">INGRESS PROXY</span>
                    <span style="background: #10b981; color: #022c22; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 4px;">ONLINE</span>
                </div>
                <div style="color: #94a3b8; font-size: 11px; margin-top: 4px; font-family: monospace;">127.0.0.1:8000 (Active)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 10px; padding: 12px 14px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #fb7185; font-weight: 700; font-size: 12px;">INGRESS PROXY</span>
                    <span style="background: #f43f5e; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 4px;">OFFLINE</span>
                </div>
                <div style="color: #94a3b8; font-size: 11px; margin-top: 4px; font-family: monospace;">Streaming from SQLite audit log</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px;'>Active Defense Matrix</div>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="policy-card">
            <div class="policy-header">
                <span>⚡ Layer 1: Heuristics</span>
                <span class="policy-tag" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">0 ms</span>
            </div>
            <div class="policy-sub">Regex & Keyword AST Drop</div>
        </div>
        <div class="policy-card">
            <div class="policy-header">
                <span>🔒 Layer 2: PII Scrubber</span>
                <span class="policy-tag" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">DLP Mask</span>
            </div>
            <div class="policy-sub">API Keys, JWT, Email Redaction</div>
        </div>
        <div class="policy-card">
            <div class="policy-header">
                <span>🤖 Layer 3: AI Judge</span>
                <span class="policy-tag" style="background: rgba(168, 85, 247, 0.15); color: #c084fc;">Groq Guard</span>
            </div>
            <div class="policy-sub">OWASP LLM01/LLM08 Classifier</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.button("🔄 Refresh Telemetry Stream", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# -----------------------------------------------------------------------------
# Main Operational Feed Header (HUD Glass)
# -----------------------------------------------------------------------------
df = fetch_audit_data()

st.markdown(
    f"""
    <div class="hud-header">
        <div>
            <h1 class="hud-title">🛡️ AI Security Operations Center (SOC)</h1>
            <div class="hud-subtitle">Live Ingress Telemetry &amp; Adversarial Threat Interception Monitor</div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="radar-ping">
                <span class="radar-dot"></span> Sentinel Active
            </div>
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #94a3b8;">
                UTC {datetime.now(timezone.utc).strftime('%H:%M:%S')}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("⚠️ No security audit records detected. Start the gateway and execute requests to stream telemetry.")
    st.stop()

# -----------------------------------------------------------------------------
# Section 1: Antigravity Floating Glass KPI Cards
# -----------------------------------------------------------------------------
total_events = len(df)
blocked_events = len(df[df["decision"] == "BLOCKED"])
allowed_events = len(df[df["decision"] == "ALLOWED"])
block_rate = (
    (blocked_events / total_events * 100) if total_events > 0 else 0.0
)
avg_latency = df["latency_ms"].mean() if "latency_ms" in df.columns else 0.0
pii_scrubbed_count = len(
    df[
        (df["threat_category"] == "OWASP_LLM02_LEAK")
        | (
            df["sanitized_prompt"].str.contains(
                r"\[REDACTED_", na=False, regex=True
            )
        )
    ]
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(
        f"""<div class="kpi-card kpi-blue">
<div class="kpi-header">
<span class="kpi-label">Ingress Volume</span>
<span class="kpi-icon">📊</span>
</div>
<div class="kpi-number" style="color: #38bdf8;">{total_events:,}</div>
<div class="kpi-meta" style="color: #38bdf8;">
<span>●</span> <span>Total Processed Invocations</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

with kpi_col2:
    st.markdown(
        f"""<div class="kpi-card kpi-red">
<div class="kpi-header">
<span class="kpi-label">Threat Interception</span>
<span class="kpi-icon">🎯</span>
</div>
<div class="kpi-number" style="color: #f43f5e;">{block_rate:.1f}%</div>
<div class="kpi-meta" style="color: #fb7185;">
<span>🛑</span> <span>{blocked_events} Malicious Drops</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

with kpi_col3:
    st.markdown(
        f"""<div class="kpi-card kpi-amber">
<div class="kpi-header">
<span class="kpi-label">PII Redactions</span>
<span class="kpi-icon">🔒</span>
</div>
<div class="kpi-number" style="color: #f59e0b;">{pii_scrubbed_count}</div>
<div class="kpi-meta" style="color: #fbbf24;">
<span>🛡️</span> <span>OWASP LLM02 Compliance</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

with kpi_col4:
    st.markdown(
        f"""<div class="kpi-card kpi-purple">
<div class="kpi-header">
<span class="kpi-label">Mean Latency</span>
<span class="kpi-icon">⚡</span>
</div>
<div class="kpi-number" style="color: #c084fc;">{avg_latency:.1f}<span style="font-size: 18px; font-weight: 600; color: #a855f7;">ms</span></div>
<div class="kpi-meta" style="color: #34d399;">
<span>✓</span> <span>3-Tier Hybrid Pipeline</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Section 2: Visual Telemetry Panels (Plotly Custom Neon Styling)
# -----------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns([1.35, 1])

with chart_col1:
    st.markdown(
        """
        <div class="panel-header">
            <div class="panel-title"><span>📊</span> Threat Vector Distribution</div>
            <div class="panel-badge">OWASP Top 10 for LLM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    blocked_df = df[df["decision"] == "BLOCKED"]
    threat_counts = (
        blocked_df["threat_category"]
        .value_counts()
        .reset_index()
    )
    threat_counts.columns = ["Threat Category", "Count"]

    if not threat_counts.empty:
        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                x=threat_counts["Count"],
                y=threat_counts["Threat Category"],
                orientation="h",
                marker=dict(
                    color=threat_counts["Count"],
                    colorscale=[[0, "#fb7185"], [1, "#f43f5e"]],
                    line=dict(color="rgba(244, 63, 94, 0.4)", width=1),
                    cornerradius=8,
                ),
                text=threat_counts["Count"],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=12, color="#ffffff"),
                hoverinfo="x+y",
            )
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=40, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=260,
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(family="JetBrains Mono", color="#94a3b8"),
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(family="Plus Jakarta Sans", color="#e2e8f0", size=12),
                autorange="reversed",
            ),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No threats intercepted yet in this operational session.")

with chart_col2:
    st.markdown(
        """
        <div class="panel-header">
            <div class="panel-title"><span>🍩</span> Ingress Decision Ratio</div>
            <div class="panel-badge">Allow vs Block</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    decision_counts = df["decision"].value_counts().reset_index()
    decision_counts.columns = ["Decision", "Count"]

    fig_donut = go.Figure()
    fig_donut.add_trace(
        go.Pie(
            labels=decision_counts["Decision"],
            values=decision_counts["Count"],
            hole=0.68,
            marker=dict(
                colors=["#10b981" if d == "ALLOWED" else "#f43f5e" for d in decision_counts["Decision"]],
                line=dict(color="#06080e", width=3),
            ),
            textinfo="percent",
            textfont=dict(family="JetBrains Mono", size=13, color="#ffffff"),
            hoverinfo="label+value+percent",
        )
    )
    # Donut Center HUD Annotation
    fig_donut.add_annotation(
        text=f"<b>{total_events}</b><br><span style='font-size:11px;color:#94a3b8'>REQUESTS</span>",
        x=0.5, y=0.5,
        font=dict(family="Plus Jakarta Sans", size=20, color="#ffffff"),
        showarrow=False,
    )
    fig_donut.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=260,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#cbd5e1", size=11),
        ),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 3: Forensic Event Log & Deep Packet Inspection
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="panel-header" style="margin-top: 20px;">
        <div class="panel-title"><span>📋</span> Forensic Incident Log &amp; Packet Inspection</div>
        <div class="panel-badge">Real-time Stream</div>
    </div>
    """,
    unsafe_allow_html=True,
)

filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.5, 2])
with filter_col1:
    decision_filter = st.selectbox(
        "Filter by Verdict", ["ALL", "BLOCKED", "ALLOWED"]
    )
with filter_col2:
    categories = ["ALL"] + sorted(df["threat_category"].dropna().unique().tolist())
    category_filter = st.selectbox("Filter by Category", categories)
with filter_col3:
    search_query = st.text_input("Search Prompt or Rule Trigger", placeholder="e.g. DAN, system prompt, sk-...")

filtered_df = df
if decision_filter != "ALL":
    filtered_df = filtered_df[filtered_df["decision"] == decision_filter]
if category_filter != "ALL":
    filtered_df = filtered_df[filtered_df["threat_category"] == category_filter]
if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df["raw_prompt"].str.lower().str.contains(q, na=False)
        | filtered_df["rule_triggered"].str.lower().str.contains(q, na=False)
    ]

# Display Table
display_cols = [
    "id",
    "timestamp",
    "decision",
    "threat_category",
    "rule_triggered",
    "latency_ms",
    "client_ip",
    "user_id",
]
available_cols = [col for col in display_cols if col in filtered_df.columns]

st.dataframe(
    filtered_df[available_cols],
    use_container_width=True,
    hide_index=True,
    height=270,
)

# Deep Event Forensic Inspector
st.markdown("<div style='font-size: 15px; font-weight: 700; color: #fff; margin-top: 20px; margin-bottom: 8px;'>🔬 Deep Triage Packet Inspector</div>", unsafe_allow_html=True)

if not filtered_df.empty:
    selected_id = st.selectbox(
        "Select Audit ID to Inspect Payload:", filtered_df["id"].tolist()
    )

    if selected_id:
        matching = filtered_df[filtered_df["id"] == selected_id]
        if not matching.empty:
            record = matching.iloc[0]
            
            p_col1, p_col2 = st.columns(2)

            with p_col1:
                st.markdown("**📥 Ingress Raw Prompt (Client Submission)**")
                st.code(record.get("raw_prompt", "N/A"), language="text")

            with p_col2:
                st.markdown(
                    "**📤 Egress Sanitized Prompt (Passed Downstream or Masked)**"
                )
                st.code(record.get("sanitized_prompt", "N/A"), language="text")

            # Forensic Metrics Bar
            is_blocked = record.get("decision") == "BLOCKED"
            badge_bg = "rgba(244, 63, 94, 0.15)" if is_blocked else "rgba(16, 185, 129, 0.15)"
            badge_color = "#fb7185" if is_blocked else "#34d399"
            badge_border = "rgba(244, 63, 94, 0.3)" if is_blocked else "rgba(16, 185, 129, 0.3)"

            st.markdown(
                f"""<div style="background: rgba(18, 24, 40, 0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 18px; margin-top: 10px; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; font-size: 13px;">
<div>
<span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 11px;">
{record.get('decision', 'N/A')}
</span>
</div>
<div><span style="color: #64748b; font-size: 11px; font-weight: 700;">THREAT:</span> <code style="color: #f1f5f9;">{record.get('threat_category', 'NONE')}</code></div>
<div><span style="color: #64748b; font-size: 11px; font-weight: 700;">RULE TRIGGERED:</span> <code style="color: #cbd5e1;">{record.get('rule_triggered', 'None')}</code></div>
<div><span style="color: #64748b; font-size: 11px; font-weight: 700;">CONFIDENCE:</span> <span style="font-family: monospace; font-weight: 700; color: #38bdf8;">{record.get('confidence_score', 0.0)}</span></div>
<div><span style="color: #64748b; font-size: 11px; font-weight: 700;">LATENCY:</span> <span style="font-family: monospace; color: #a855f7;">{record.get('latency_ms', 0.0):.1f} ms</span></div>
<div><span style="color: #64748b; font-size: 11px; font-weight: 700;">IP:</span> <span style="font-family: monospace; color: #94a3b8;">{record.get('client_ip', 'unknown')}</span></div>
</div>""",
                unsafe_allow_html=True,
            )
else:
    st.info("No audit records found matching the current search filters.")