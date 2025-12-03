import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from pyvis.network import Network

# --- CONFIGURATION & AESTHETICS ---
API_URL = "http://localhost:8000"
st.set_page_config(page_title="ThreatLens: Malware Detection", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* Global Styling */
        .stApp { 
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0f1419 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Animated gradient overlay */
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Page fade-in animation */
        @keyframes page-fade-in {
            0% { 
                opacity: 0;
                transform: translateY(20px);
            }
            100% { 
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Shimmer effect for loading */
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        /* Pulse glow animation */
        @keyframes pulse-glow {
            0%, 100% { 
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 
                            0 0 20px rgba(96, 165, 250, 0.1) inset;
            }
            50% { 
                box-shadow: 0 10px 40px rgba(96, 165, 250, 0.3), 
                            0 0 30px rgba(96, 165, 250, 0.2) inset;
            }
        }
        
        /* Slide in from left animation */
        @keyframes slide-in-left {
            0% {
                opacity: 0;
                transform: translateX(-40px);
            }
            100% {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Slide in from right animation */
        @keyframes slide-in-right {
            0% {
                opacity: 0;
                transform: translateX(40px);
            }
            100% {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Scale up animation */
        @keyframes scale-up {
            0% {
                opacity: 0;
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        /* Apply fade-in to main content */
        .block-container {
            animation: page-fade-in 0.6s ease-out;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Main Title Styling */
        h1 {
            background: linear-gradient(120deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: -0.02em;
            padding-bottom: 1rem;
            animation: gradient-shift 3s ease infinite;
        }
        
        /* Subheader Styling */
        h2, h3 {
            color: #f3f4f6;
            font-weight: 600;
            margin-top: 2rem;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
            /* Add slide-in animation to subheaders */
            animation: slide-in-left 0.5s ease-out;
        }
        
        h4 {
            color: #d1d5db;
            font-weight: 500;
            margin-top: 1rem;
            /* Add slide-in animation to h4 */
            animation: slide-in-left 0.6s ease-out;
        }
        
        /* Enhanced Metric Cards with glassmorphism */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.9) 100%);
            backdrop-filter: blur(12px);
            padding: 1.75rem;
            border-radius: 20px;
            border: 1px solid rgba(96, 165, 250, 0.25);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 
                        0 0 20px rgba(96, 165, 250, 0.1) inset;
            /* Enhanced transition with spring-like timing */
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            overflow: hidden;
            /* Add scale-up entrance animation with staggered timing */
            animation: scale-up 0.6s ease-out backwards;
        }
        
        /* Stagger metric card animations */
        div[data-testid="stMetric"]:nth-child(1) { animation-delay: 0.1s; }
        div[data-testid="stMetric"]:nth-child(2) { animation-delay: 0.2s; }
        div[data-testid="stMetric"]:nth-child(3) { animation-delay: 0.3s; }
        div[data-testid="stMetric"]:nth-child(4) { animation-delay: 0.4s; }
        
        div[data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(96, 165, 250, 0.15) 0%, transparent 70%);
            opacity: 0;
            /* Smoother transition for glow effect */
            transition: opacity 0.5s ease, transform 0.5s ease;
            transform: scale(0.8);
        }
        
        div[data-testid="stMetric"]:hover::before {
            opacity: 1;
            transform: scale(1);
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-8px) scale(1.03);
            border-color: rgba(96, 165, 250, 0.6);
            box-shadow: 0 20px 60px rgba(96, 165, 250, 0.35),
                        0 0 40px rgba(96, 165, 250, 0.2) inset;
        }
        
        /* Add active state for click feedback */
        div[data-testid="stMetric"]:active {
            transform: translateY(-4px) scale(1.01);
            transition: all 0.1s ease;
        }
        
        div[data-testid="stMetric"] label {
            color: #9ca3af !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            /* Add smooth color transition */
            transition: color 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover label {
            color: #d1d5db !important;
        }
        
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #60a5fa !important;
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            font-family: 'JetBrains Mono', monospace;
            text-shadow: 0 0 20px rgba(96, 165, 250, 0.3);
            /* Add smooth scale transition on hover */
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), 
                        text-shadow 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover [data-testid="stMetricValue"] {
            transform: scale(1.05);
            text-shadow: 0 0 30px rgba(96, 165, 250, 0.5);
        }
        
        /* Styled Dataframes */
        .dataframe {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            border-radius: 12px;
            overflow: hidden;
            /* Add fade-in animation to tables */
            animation: page-fade-in 0.7s ease-out 0.3s backwards;
        }
        
        /* Table Header Styling */
        thead tr th {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
            color: #e5e7eb !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1rem !important;
            border-bottom: 2px solid rgba(96, 165, 250, 0.3) !important;
            /* Add hover transition to headers */
            transition: all 0.3s ease;
        }
        
        thead tr th:hover {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%) !important;
            color: #f3f4f6 !important;
        }
        
        tbody tr {
            /* Enhanced transition with bouncy effect */
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        tbody tr:hover {
            background: rgba(96, 165, 250, 0.08) !important;
            transform: scale(1.02) translateX(4px);
            /* Add glow effect on hover */
            box-shadow: 0 4px 20px rgba(96, 165, 250, 0.2);
        }
        
        tbody td {
            /* Add smooth transition to table cells */
            transition: padding 0.3s ease;
        }
        
        tbody tr:hover td {
            padding-left: 1.25rem !important;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.875rem 2.5rem;
            font-weight: 600;
            font-size: 1rem;
            /* Enhanced spring animation */
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4),
                        0 0 15px rgba(139, 92, 246, 0.2) inset;
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            /* Faster ripple effect */
            transition: width 0.5s ease, height 0.5s ease;
        }
        
        .stButton > button:hover::before {
            width: 400px;
            height: 400px;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.08);
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.6),
                        0 0 30px rgba(139, 92, 246, 0.4) inset;
            letter-spacing: 0.05em;
        }
        
        .stButton > button:active {
            transform: translateY(-2px) scale(1.04);
            /* Quick transition for click feedback */
            transition: all 0.1s ease;
        }
        
        /* Input Field Styling */
        .stTextInput > div > div > input {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.6) 0%, rgba(17, 24, 39, 0.6) 100%);
            backdrop-filter: blur(8px);
            border: 1.5px solid rgba(96, 165, 250, 0.3);
            border-radius: 14px;
            color: #f3f4f6;
            padding: 0.875rem 1.25rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            /* Smoother transitions for all properties */
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                        transform 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .stTextInput > div > div > input:hover {
            border-color: rgba(96, 165, 250, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #60a5fa;
            box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.25),
                        0 6px 20px rgba(96, 165, 250, 0.3);
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.8) 0%, rgba(17, 24, 39, 0.8) 100%);
            transform: translateY(-2px) scale(1.01);
        }
        
        .stTextInput > label {
            color: #d1d5db !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            margin-bottom: 0.5rem !important;
            /* Add smooth color transition */
            transition: color 0.3s ease;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1419 0%, #1a1f35 50%, #111827 100%);
            border-right: 1px solid rgba(96, 165, 250, 0.25);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
            /* Add slide-in animation to sidebar */
            animation: slide-in-left 0.5s ease-out;
        }
        
        section[data-testid="stSidebar"] .stRadio > label {
            color: #d1d5db;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        section[data-testid="stSidebar"] .stRadio > div {
            gap: 0.75rem;
        }
        
        section[data-testid="stSidebar"] .stRadio > div > label {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.6) 0%, rgba(17, 24, 39, 0.6) 100%);
            backdrop-filter: blur(8px);
            padding: 1rem 1.25rem;
            border-radius: 14px;
            border: 1px solid rgba(96, 165, 250, 0.15);
            /* Enhanced transition with spring effect */
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            cursor: pointer;
            font-weight: 500;
            position: relative;
            overflow: hidden;
        }
        
        /* Add shimmer effect on hover */
        section[data-testid="stSidebar"] .stRadio > div > label::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -100%;
            width: 100%;
            height: 200%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(96, 165, 250, 0.2), 
                transparent);
            transition: left 0.5s ease;
        }
        
        section[data-testid="stSidebar"] .stRadio > div > label:hover::before {
            left: 100%;
        }
        
        section[data-testid="stSidebar"] .stRadio > div > label:hover {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
            border-color: rgba(96, 165, 250, 0.5);
            transform: translateX(8px) scale(1.02);
            box-shadow: 0 6px 20px rgba(96, 165, 250, 0.25),
                        0 0 20px rgba(96, 165, 250, 0.1) inset;
        }
        
        /* Add active/selected state */
        section[data-testid="stSidebar"] .stRadio > div > label:active {
            transform: translateX(4px) scale(1);
            transition: all 0.1s ease;
        }
        
        /* Slider Styling */
        .stSlider > div > div > div {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            /* Add transition to slider track */
            transition: all 0.3s ease;
        }
        
        .stSlider > div > div > div > div {
            background: white;
            box-shadow: 0 2px 8px rgba(96, 165, 250, 0.4);
            /* Add smooth transition to slider thumb */
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        .stSlider > div > div > div > div:hover {
            transform: scale(1.2);
            box-shadow: 0 4px 12px rgba(96, 165, 250, 0.6);
        }
        
        .stSlider > div > div > div > div:active {
            transform: scale(1.1);
        }
        
        /* Divider Styling */
        hr {
            margin: 2.5rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, rgba(96, 165, 250, 0.4) 20%, rgba(139, 92, 246, 0.4) 80%, transparent 100%);
            box-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
            /* Add fade-in animation to dividers */
            animation: page-fade-in 0.8s ease-out 0.2s backwards;
        }
        
        /* Alert/Info Box Styling */
        .stAlert {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.7) 0%, rgba(17, 24, 39, 0.7) 100%);
            backdrop-filter: blur(10px);
            border-radius: 14px;
            border-left: 4px solid #60a5fa;
            padding: 1.25rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3),
                        0 0 20px rgba(96, 165, 250, 0.1) inset;
            /* Add slide-in animation to alerts */
            animation: slide-in-right 0.5s ease-out;
            transition: all 0.3s ease;
        }
        
        .stAlert:hover {
            transform: translateX(-4px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4),
                        0 0 25px rgba(96, 165, 250, 0.15) inset;
        }
        
        /* Success/Warning/Error Messages */
        .stSuccess {
            border-left-color: #10b981 !important;
        }
        
        .stWarning {
            border-left-color: #f59e0b !important;
        }
        
        .stError {
            border-left-color: #ef4444 !important;
        }
        
        /* Markdown text color */
        .stMarkdown {
            color: #e5e7eb;
            line-height: 1.6;
        }
        
        /* Plotly chart container */
        .js-plotly-plot {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            /* Add scale-up animation to charts */
            animation: scale-up 0.7s ease-out 0.2s backwards;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        .js-plotly-plot:hover {
            transform: scale(1.01);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5),
                        0 0 30px rgba(96, 165, 250, 0.1);
        }
        
        /* Column container animation */
        [data-testid="column"] {
            animation: page-fade-in 0.6s ease-out backwards;
        }
        
        [data-testid="column"]:nth-child(1) { animation-delay: 0.1s; }
        [data-testid="column"]:nth-child(2) { animation-delay: 0.2s; }
        [data-testid="column"]:nth-child(3) { animation-delay: 0.3s; }
        [data-testid="column"]:nth-child(4) { animation-delay: 0.4s; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ ThreatLens: Network Malware Detection System")

# Sidebar Navigation
page = st.sidebar.radio("Navigate", ["🚨 Alerts Overview", "📄 File Analysis", "🕸️ Network Graph"])

# --- PAGE 1: ALERTS OVERVIEW ---
if page == "🚨 Alerts Overview":
    st.subheader("Real-Time Security Alerts")
    
    try:
        response = requests.get(f"{API_URL}/alerts")
        if response.status_code == 200:
            alerts = response.json()
            df = pd.DataFrame(alerts)
            
            # --- METRICS ROW ---
            col1, col2, col3, col4 = st.columns(4)
            
            # Safe access to 'type' column
            ransomware_count = 0
            if 'type' in df.columns:
                ransomware_count = len(df[df['type'].str.contains("Ransomware", case=False, na=False)])
            
            col1.metric("Total Alerts", len(df))
            col2.metric("Critical Threats", len(df[df['severity'] == 'critical']))
            col3.metric("Avg Threat Score", f"{df['threat_score'].mean():.2f}")
            col4.metric("Active Ransomware", ransomware_count)

            # --- MAIN TABLE ---
            st.divider()
            st.markdown("#### 📋 Live Alert Log")
            
            # Color Map for Severity
            def highlight_severity(val):
                colors = {
                    'critical': 'background-color: #7f1d1d; color: #fca5a5',
                    'high': 'background-color: #7c2d12; color: #fdba74',
                    'medium': 'background-color: #713f12; color: #fde047',
                    'low': 'background-color: #064e3b; color: #6ee7b7'
                }
                return colors.get(val, '')

            # Display optimized table
            st.dataframe(
                df.style.applymap(highlight_severity, subset=['severity']),
                use_container_width=True,
                column_config={
                    "timestamp": st.column_config.NumberColumn("Timestamp", format="%f"),
                    "threat_score": st.column_config.ProgressColumn("Threat Score", min_value=0, max_value=1, format="%.2f"),
                }
            )
        else:
            st.error("Backend offline. Please run `python backend.py`.")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")

# --- PAGE 2: FILE ANALYSIS (ML + SHAP) ---
elif page == "📄 File Analysis":
    st.subheader("🔍 Deep File Inspection")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # Default value from mock data
        file_hash = st.text_input("Enter SHA256 Hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        analyze_btn = st.button("Analyze File", type="primary")
    
    if analyze_btn:
        try:
            resp = requests.get(f"{API_URL}/file/{file_hash}")
            if resp.status_code == 200:
                data = resp.json()
                meta = data['metadata']
                analysis = data['analysis']
                
                # --- VISUALIZATION: ANIMATED GAUGE ---
                prob = analysis['malware_prob'] * 100
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = prob,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Malware Probability", 'font': {'size': 24, 'color': '#e5e7eb', 'family': 'Inter'}},
                    number = {'suffix': "%", 'font': {'color': "#60a5fa", 'size': 48, 'family': 'JetBrains Mono'}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#4b5563"},
                        'bar': {'color': "#ef4444", 'thickness': 0.8},
                        'bgcolor': "rgba(31, 41, 55, 0.3)",
                        'borderwidth': 3,
                        'bordercolor': "rgba(96, 165, 250, 0.3)",
                        'steps': [
                            {'range': [0, 30], 'color': "rgba(16, 185, 129, 0.2)"},
                            {'range': [30, 70], 'color': "rgba(251, 191, 36, 0.2)"},
                            {'range': [70, 100], 'color': "rgba(239, 68, 68, 0.2)"}
                        ],
                        'threshold': {
                            'line': {'color': "#8b5cf6", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=300,
                    font={'color': "#e5e7eb", 'family': 'Inter'}
                )
                
                with col1:
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.info(f"**MIME Type:** {meta.get('mime_type', 'Unknown')}\n\n**Size:** {meta.get('size', 0)} bytes")

                with col2:
                    st.subheader("🤖 Explainable AI (SHAP)")
                    st.markdown("*Why did the model flag this file?*")
                    
                    shap_data = analysis.get('top_features', [])
                    if shap_data:
                        shap_df = pd.DataFrame(shap_data)
                        
                        fig_bar = go.Figure(go.Bar(
                            x=shap_df['contrib'],
                            y=shap_df['name'],
                            orientation='h',
                            marker=dict(
                                color=shap_df['contrib'],
                                colorscale='RdBu_r',
                                showscale=True,
                                colorbar=dict(
                                    title=dict(
                                        text="Impact",
                                        font=dict(color='#e5e7eb', family='Inter', size=14)
                                    ),
                                    tickfont=dict(color='#e5e7eb', family='Inter'),
                                    thickness=15,
                                    len=0.7,
                                    bgcolor='rgba(17, 24, 39, 0.5)',
                                    bordercolor='rgba(96, 165, 250, 0.3)',
                                    borderwidth=1
                                ),
                                line=dict(color='rgba(96, 165, 250, 0.4)', width=1.5)
                            ),
                            hovertemplate='<b>%{y}</b><br>Contribution: %{x:.3f}<extra></extra>'
                        ))
                        
                        fig_bar.update_layout(
                            title={
                                'text': "Feature Contribution Analysis",
                                'font': {'size': 20, 'color': '#f3f4f6', 'family': 'Inter', 'weight': 600},
                                'x': 0.05
                            },
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(17, 24, 39, 0.3)",
                            height=400,
                            xaxis=dict(
                                showgrid=True, 
                                gridcolor='rgba(96, 165, 250, 0.15)',
                                gridwidth=1,
                                title=dict(text='SHAP Value', font=dict(color='#9ca3af', family='Inter', size=13)),
                                tickfont=dict(color='#9ca3af', family='JetBrains Mono', size=11),
                                zeroline=True,
                                zerolinecolor='rgba(96, 165, 250, 0.3)',
                                zerolinewidth=2
                            ),
                            yaxis=dict(
                                showgrid=False,
                                tickfont=dict(color='#e5e7eb', family='JetBrains Mono', size=11)
                            ),
                            font={'color': "#e5e7eb", 'family': 'Inter'},
                            margin=dict(l=20, r=20, t=50, b=40),
                            hoverlabel=dict(
                                bgcolor="rgba(31, 41, 55, 0.95)",
                                font_size=12,
                                font_family="Inter",
                                bordercolor="rgba(96, 165, 250, 0.5)"
                            )
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("File hash not found in database.")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- PAGE 3: NETWORK GRAPH ---
elif page == "🕸️ Network Graph":
    st.subheader("🕸️ Network Threat Propagation")
    
    st.sidebar.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    '>
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>
            <span style='font-size: 24px;'>🎛️</span>
            <h3 style='margin: 0; font-size: 18px; font-weight: 600; color: #60a5fa;'>Graph Controls</h3>
        </div>
        <p style='margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.5;'>
            Adjust the threat threshold to filter nodes and reduce visual clutter.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add spacing
    st.sidebar.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    
    # Improved slider with session state to prevent crashes
    if 'min_score' not in st.session_state:
        st.session_state.min_score = 0.5
    
    min_score = st.sidebar.slider(
        "Threat Threshold",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.min_score,
        step=0.01,
        help="Filter out nodes with threat scores below this threshold",
        key="threshold_slider"
    )
    
    # Update session state
    st.session_state.min_score = min_score
    
    # Display current threshold with better styling
    st.sidebar.markdown(f"""
    <div style='
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        text-align: center;
    '>
        <div style='font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;'>Current Threshold</div>
        <div style='font-size: 28px; font-weight: 700; color: #10b981;'>{min_score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        resp = requests.get(f"{API_URL}/alerts", timeout=5)
        resp.raise_for_status()
        alerts = resp.json()
        
        # Validate alerts data
        if not alerts or not isinstance(alerts, list):
            st.warning("No alert data available.")
        else:
            net = Network(height='600px', width='100%', bgcolor='#0e1117', font_color='white')
            net.barnes_hut(gravity=-2000, central_gravity=0.3, spring_length=100)
            
            added_nodes = set()
            filtered_count = 0
            
            for alert in alerts:
                if not isinstance(alert, dict) or 'threat_score' not in alert:
                    continue
                    
                if alert['threat_score'] < min_score:
                    filtered_count += 1
                    continue
                    
                src_ip = alert.get('ip', 'Unknown')
                
                if alert.get('severity') == 'critical':
                    color = '#ef4444'
                    size = 25
                elif alert.get('severity') == 'high':
                    color = '#f97316'
                    size = 18
                else:
                    color = '#10b981'
                    size = 10
                
                if src_ip not in added_nodes:
                    net.add_node(src_ip, label=src_ip, title=f"Threat: {alert['threat_score']}", color=color, value=size, borderWidth=2)
                    added_nodes.add(src_ip)
                
                dst_ip = f"C2-{src_ip.split('.')[-1]}" 
                if dst_ip not in added_nodes:
                    net.add_node(dst_ip, label="C2 Server", color='#3b82f6', shape='triangle', size=15) 
                    added_nodes.add(dst_ip)
                
                net.add_edge(src_ip, dst_ip, color='#4b5563', width=2)

            if filtered_count > 0:
                st.info(f"Filtered out {filtered_count} node(s) below threshold {min_score:.2f}")
            
            if len(added_nodes) == 0:
                st.warning(f"No nodes meet the threshold criteria ({min_score:.2f}). Try lowering the threshold.")
            else:
                net.save_graph('graph.html')
                with open('graph.html', 'r', encoding='utf-8') as f:
                    html_string = f.read()
                
                components.html(html_string, height=620, scrolling=False)
        
    except requests.exceptions.Timeout:
        st.error("Connection timeout. Please ensure the backend is running.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Please run `python backend.py`.")
    except Exception as e:
        st.error(f"Graph Error: {str(e)}")
        st.info("Try adjusting the threshold or reloading the page.")
