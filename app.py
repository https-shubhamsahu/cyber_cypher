"""
Smart Payment Operations - Sentinel War Room
Dark, professional, technical dashboard with AI reasoning display
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import pandas as pd
import os
import json

import simulator
import agent_engine
import tools


# Page configuration
st.set_page_config(
    page_title="🛡️ Payment Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark professional theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8892b0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ccd6f6;
        font-family: 'Consolas', 'Monaco', monospace;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        border-right: 1px solid #667eea;
    }
    
    /* Code blocks */
    code {
        background-color: #1e2139 !important;
        color: #64ffda !important;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
    }
    
    /* Cards */
    .tech-card {
        background: rgba(30, 33, 57, 0.6);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Scrollable text */
    .reasoning-box {
        background: rgba(10, 14, 39, 0.8);
        border: 1px solid #64ffda;
        border-radius: 8px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        color: #8892b0;
    }
    
    .reasoning-box::-webkit-scrollbar {
        width: 8px;
    }
    
    .reasoning-box::-webkit-scrollbar-track {
        background: #1e2139;
    }
    
    .reasoning-box::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'simulator_running' not in st.session_state:
    st.session_state.simulator_running = False
    st.session_state.agent_log = []
    st.session_state.last_agent_run = None
    st.session_state.intervention_count = 0
    st.session_state.last_run_timestamp = 0


def load_transactions_from_csv(count=50):
    """Load recent transactions from CSV."""
    try:
        if os.path.exists('transactions.csv'):
            # Use on_bad_lines='skip' to handle corrupted rows
            df = pd.read_csv('transactions.csv', on_bad_lines='skip')
            if df.empty:
                return []
            return df.tail(count).to_dict('records')
        return []
    except Exception as e:
        # In streamlit, it's useful to see this in console
        print(f"Error reading transactions CSV: {e}")
        return []


def calculate_metrics():
    """Calculate real-time metrics from transactions."""
    transactions = load_transactions_from_csv(50)
    
    if not transactions:
        return {
            'success_rate': 0,
            'avg_latency': 0,
            'interventions': 0,
            'bank_latencies': {}
        }
    
    total = len(transactions)
    successful = sum(1 for t in transactions if t.get('status') == 'Success')
    
    # Per-bank latencies over time
    bank_latencies = {}
    for t in transactions:
        bank = t.get('bank', 'Unknown')
        if bank not in bank_latencies:
            bank_latencies[bank] = []
        
        try:
            ts = pd.to_datetime(t['timestamp'])
            bank_latencies[bank].append({
                'timestamp': ts,
                'latency': float(t.get('latency_ms', 0))
            })
        except (ValueError, TypeError):
            continue
    
    return {
        'success_rate': (successful / total * 100) if total > 0 else 0,
        'avg_latency': sum(float(t.get('latency_ms', 0)) for t in transactions) / total if total > 0 else 0,
        'interventions': st.session_state.intervention_count,
        'bank_latencies': bank_latencies
    }


def start_simulator():
    """Start the transaction simulator."""
    if not st.session_state.simulator_running:
        simulator.simulator.start()
        st.session_state.simulator_running = True


def stop_simulator():
    """Stop the transaction simulator."""
    simulator.simulator.stop()
    st.session_state.simulator_running = False


def run_agent_cycle():
    """Run one agent cycle and capture reasoning."""
    try:
        result = agent_engine.run_agent_cycle()
        
        # Count interventions
        if result.get('actions', []) and result['actions'][0] != 'NONE':
            st.session_state.intervention_count += len(result['actions'])
        
        st.session_state.agent_log.append(result)
        st.session_state.agent_log = st.session_state.agent_log[-10:]
        st.session_state.last_agent_run = datetime.now()
        
        return result
        
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'reasoning': f'Error: {str(e)}',
            'reasoning_details': None,
            'actions': [],
            'feedback': {'status': 'error'}
        }


def toggle_hdfc_chaos():
    """Toggle HDFC bank degradation."""
    config = tools.get_config()
    hdfc = next((b for b in config['banks'] if b['id'] == 'hdfc'), None)
    
    if hdfc:
        current_status = hdfc.get('health_status', 'healthy')
        new_status = 'degraded' if current_status == 'healthy' else 'healthy'
        tools.update_bank_health('hdfc', new_status)
        return new_status
    return None


# Header with glowing effect
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">
        🛡️ PAYMENT SENTINEL
    </h1>
    <p style="color: #64ffda; font-size: 1.2rem; font-family: 'Consolas', monospace;">
        AI-Powered Autonomous Payment Operations
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Sentinel Mind
with st.sidebar:
    st.markdown("### 🧠 SENTINEL MIND")
    st.markdown("*AI Reasoning Stream*")
    
    # Auto-run controls
    col_a, col_b = st.columns([0.7, 0.3])
    with col_a:
        manual_run = st.button("🚀 Run Analysis", use_container_width=True)
    with col_b:
        auto_run = st.checkbox("20s", value=False, help="Auto-run every 20 seconds")
    
    # Logic for running analysis
    should_run = False
    
    if manual_run:
        should_run = True
    elif auto_run:
        time_since = time.time() - st.session_state.last_run_timestamp
        if time_since > 20:
            should_run = True
        else:
            # Show countdown
            st.caption(f"Next run in {int(20 - time_since)}s...")
    
    if should_run:
        if st.session_state.simulator_running or os.path.exists('transactions.csv'):
            with st.spinner("🤖 Sentinel Analyzing..."):
                run_agent_cycle()
                st.session_state.last_run_timestamp = time.time()
                st.rerun()
        else:
            st.warning("Start simulator first!")
            
    # Auto-refresh loop if enabled
    if auto_run:
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔗 EXTERNAL LINKS")
    # In cloud deployment, provide the URL of the separate Checkout app
    checkout_url = os.getenv("CHECKOUT_URL", "https://cybercypher-checkout.streamlit.app/")
    st.link_button("🛒 Open Customer Checkout", checkout_url, use_container_width=True)
    
    st.markdown("---")
    st.markdown("**Latest Analysis:**")
    
    # Try to load from disk (background process)
    disk_state = agent_engine.read_agent_state()
    if disk_state:
        # Check if disk state is newer than session state
        last_session_time = st.session_state.last_agent_run
        disk_time = None
        try:
            disk_time = datetime.fromisoformat(disk_state.get('timestamp', ''))
        except:
            pass
            
        if not last_session_time or (disk_time and disk_time > last_session_time):
            # Update session with disk state
            st.session_state.agent_log.append(disk_state)
            st.session_state.agent_log = st.session_state.agent_log[-10:]
            st.session_state.last_agent_run = disk_time
    
    if st.session_state.agent_log:
        latest = st.session_state.agent_log[-1]
        structured = latest.get('reasoning_details', {}) or {}
        
        # Check for errors in raw reasoning
        raw_reasoning = latest.get('reasoning', '')
        if "Error" in raw_reasoning or "Rate Limit" in raw_reasoning:
            decision = "RATE_LIMIT"
            status_color = "#EF4444"
            structured = {}
        else:
            decision = structured.get('decision', 'ANALYZING')
            status_color = "#10B981" if decision == "NO_ACTION" else "#F59E0B"
            if decision == "INTERVENE":
                status_color = "#EF4444"
            
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.8); border-left: 4px solid {status_color}; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">
            <div style="color: #8892b0; font-size: 0.8rem; letter-spacing: 1px;">DECISION</div>
            <div style="color: {status_color}; font-weight: 800; font-size: 1.5rem;">{decision}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence (only if valid)
        if structured:
            confidence = structured.get('confidence_score', 0.0)
            st.progress(confidence, text=f"Confidence: {confidence*100:.0f}%")
        else:
            st.warning(f"System Alert: {raw_reasoning[:100]}...")
        
        # Hypothesis
        if structured.get('hypothesis'):
            st.markdown(f"**🧐 Hypothesis:**")
            st.info(structured['hypothesis'])
            
        # Analysis Box
        obs_text = f"**ANALYSIS:**\n{structured.get('analysis', 'No analysis available.')}"
        
        st.markdown(f"""
        <div class="reasoning-box">
            <div style="color: #64ffda; font-weight: bold; margin-bottom: 10px;">
                [{latest.get('timestamp', '')}] ANALYSIS STREAM
            </div>
            <div style="color: #ccd6f6; white-space: pre-wrap; font-family: monospace;">
{obs_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions
        if latest.get('actions') and latest['actions'][0] != 'NONE':
            st.markdown(f"**⚡ ACTIONS TAKEN:**")
            for action in latest['actions']:
                st.markdown(f"```python\n{action}\n```")
        
        timestamp = latest.get('timestamp', '')
    else:
        st.info("No analysis yet. Run the agent to see reasoning.")
    
    st.markdown("---")
    
    # Launch checkout demo
    st.link_button(
        "🚀 Launch Checkout Demo",
        "http://localhost:8502",
        use_container_width=True
    )

# Main dashboard area
# Top row - KPI Cards
col1, col2, col3 = st.columns(3)

metrics = calculate_metrics()

with col1:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    success_color = "normal" if metrics['success_rate'] >= 90 else "inverse"
    st.metric(
        "SYSTEM SUCCESS RATE",
        f"{metrics['success_rate']:.1f}%",
        delta=f"{'✓' if metrics['success_rate'] >= 90 else '⚠'} Target: 95%",
        delta_color=success_color
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    latency_color = "normal" if metrics['avg_latency'] < 300 else "inverse"
    st.metric(
        "SYSTEM LATENCY",
        f"{metrics['avg_latency']:.0f} ms",
        delta=f"{'✓' if metrics['avg_latency'] < 300 else '⚠'} Threshold: 300ms",
        delta_color=latency_color
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.metric(
        "ACTIVE INTERVENTIONS",
        f"{metrics['interventions']}",
        delta="AI-driven optimizations"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Middle - Real-time Latency Chart
st.markdown("### 📊 REAL-TIME BANK LATENCY ANALYSIS")

bank_latencies = metrics.get('bank_latencies', {})

if bank_latencies:
    fig = go.Figure()
    
    colors = {
        'HDFC Bank': '#ef4444',
        'SBI Bank': '#f59e0b',
        'ICICI Bank': '#10b981',
        'BOB Bank': '#3b82f6',
        'AXIS Bank': '#8b5cf6',
        'IDFC Bank': '#ec4899',
        'PNB Bank': '#6366f1'
    }
    
    for bank, data in bank_latencies.items():
        if data:
            timestamps = [d['timestamp'] for d in data]
            latencies = [d['latency'] for d in data]
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=latencies,
                mode='lines+markers',
                name=bank,
                line=dict(
                    color=colors.get(bank, '#64ffda'),
                    width=3
                ),
                marker=dict(size=6),
                hovertemplate=f'<b>{bank}</b><br>Latency: %{{y:.0f}}ms<br>Time: %{{x}}<extra></extra>'
            ))
    
    # Add threshold line
    fig.add_hline(
        y=300,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical Threshold (300ms)",
        annotation_position="right"
    )
    
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(30, 33, 57, 0.6)',
        plot_bgcolor='rgba(10, 14, 39, 0.8)',
        font=dict(color='#ccd6f6', family='Consolas, Monaco, monospace'),
        xaxis=dict(
            gridcolor='rgba(102, 126, 234, 0.2)',
            showgrid=True,
            title="Time"
        ),
        yaxis=dict(
            gridcolor='rgba(102, 126, 234, 0.2)',
            showgrid=True,
            title="Latency (ms)"
        ),
        legend=dict(
            bgcolor='rgba(30, 33, 57, 0.8)',
            bordercolor='#667eea',
            borderwidth=1
        ),
        hovermode='x unified',
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💫 Awaiting transaction data... Start the simulator to begin monitoring.")

st.markdown("<br>", unsafe_allow_html=True)

# Live Logs Section
st.markdown("### 📡 LIVE TRAFFIC LOGS")

recent_transactions = load_transactions_from_csv(15)
if recent_transactions:
    df_logs = pd.DataFrame(recent_transactions)
    
    # Clean up
    if not df_logs.empty:
        # Sort descending by timestamp (if available) or index
        df_logs = df_logs.iloc[::-1]  # Reverse order to show newest first
        
        # Format Timestamp
        if 'timestamp' in df_logs.columns:
            try:
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%H:%M:%S')
            except:
                pass

        # Select columns
        cols_msg = ['timestamp', 'txn_id', 'bank', 'method', 'amount', 'status', 'latency_ms', 'error_code']
        # Filter only existing columns
        cols_to_use = [c for c in cols_msg if c in df_logs.columns]
        df_display = df_logs[cols_to_use].copy()
        
        # Rename
        rename_map = {
            'timestamp': 'TIME',
            'txn_id': 'TXN ID',
            'bank': 'BANK',
            'method': 'METHOD',
            'amount': 'INR',
            'status': 'STATUS',
            'latency_ms': 'LATENCY',
            'error_code': 'ERROR'
        }
        df_display.rename(columns=rename_map, inplace=True)
        
        # Styled Dataframe
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "STATUS": st.column_config.TextColumn(
                    "STATUS",
                ),
                "LATENCY": st.column_config.NumberColumn(
                    "LATENCY",
                    format="%d ms"
                ),
                "INR": st.column_config.NumberColumn(
                    "INR",
                    format="₹%d"
                )
            }
        )
else:
    st.info("Waiting for transactions...")

st.markdown("<br>", unsafe_allow_html=True)

# Bottom - Control Panel
st.markdown("### ⚙️ SENTINEL CONTROL PANEL")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.markdown("**🔄 Simulator Control**")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(
            "▶️ START" if not st.session_state.simulator_running else "⏸️ STOP",
            use_container_width=True,
            key="sim_toggle"
        ):
            if st.session_state.simulator_running:
                stop_simulator()
            else:
                start_simulator()
            st.rerun()
    
    with col_b:
        simulator_status = "🟢 RUNNING" if st.session_state.simulator_running else "🔴 STOPPED"
        st.markdown(f"**Status:** {simulator_status}")
    
    st.caption("📊 Transaction rate: 1 per 2 seconds")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.markdown("**🛡️ Governance & Chaos**")
    
    config = tools.get_config()
    safe_mode = config.get('global_config', {}).get('safe_mode', False)
    
    if st.button(f"{'🔓 DISABLE' if safe_mode else '🔒 ENABLE'} SAFE MODE", use_container_width=True):
        config['global_config']['safe_mode'] = not safe_mode
        tools.save_config(config)
        st.rerun()
    
    st.caption(f"Status: {'**DRY RUN ONLY**' if safe_mode else '**AUTONOMOUS**'}")
    st.markdown("---")
    
    # Chaos
    hdfc = next((b for b in config['banks'] if b['id'] == 'hdfc'), None)
    hdfc_status = hdfc.get('health_status', 'unknown') if hdfc else 'unknown'
    
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button(
            "💥 BREAK HDFC" if hdfc_status == 'healthy' else "🔧 HEAL HDFC",
            use_container_width=True,
            key="chaos_toggle"
        ):
            new_status = toggle_hdfc_chaos()
            st.rerun()
    
    with col_d:
        status_emoji = "🟢" if hdfc_status == 'healthy' else "🟡" if hdfc_status == 'degraded' else "🔴"
        st.markdown(f"**HDFC:** {status_emoji} {hdfc_status.upper()}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Auto-run agent
# Auto-run agent logic removed - handled by background sentinel_loop.py
# if auto_run and ...

# Auto-refresh for live updates
if st.session_state.simulator_running or os.path.exists('transactions.csv'):
    time.sleep(2)
    st.rerun()
