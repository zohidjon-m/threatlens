import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from pyvis.network import Network
import os

# --- CONFIGURATION & AESTHETICS ---
API_URL = os.getenv("API_URL", "http://localhost:8000")
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
        
        /* Slide in animations */
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
            animation: slide-in-left 0.5s ease-out;
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
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: scale-up 0.6s ease-out backwards;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-8px) scale(1.03);
            border-color: rgba(96, 165, 250, 0.6);
            box-shadow: 0 20px 60px rgba(96, 165, 250, 0.35),
                        0 0 40px rgba(96, 165, 250, 0.2) inset;
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
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4),
                        0 0 15px rgba(139, 92, 246, 0.2) inset;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.08);
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.6),
                        0 0 30px rgba(139, 92, 246, 0.4) inset;
        }
        
        /* File uploader styling */
        .stFileUploader {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.6) 0%, rgba(17, 24, 39, 0.6) 100%);
            backdrop-filter: blur(8px);
            border: 2px dashed rgba(96, 165, 250, 0.4);
            border-radius: 16px;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: rgba(96, 165, 250, 0.7);
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1419 0%, #1a1f35 50%, #111827 100%);
            border-right: 1px solid rgba(96, 165, 250, 0.25);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
            animation: slide-in-left 0.5s ease-out;
        }
        
        /* Dataframes */
        .dataframe {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            border-radius: 12px;
            overflow: hidden;
            animation: page-fade-in 0.7s ease-out 0.3s backwards;
        }
        
        thead tr th {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
            color: #e5e7eb !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1rem !important;
            border-bottom: 2px solid rgba(96, 165, 250, 0.3) !important;
        }
        
        tbody tr {
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        tbody tr:hover {
            background: rgba(96, 165, 250, 0.08) !important;
            transform: scale(1.02) translateX(4px);
            box-shadow: 0 4px 20px rgba(96, 165, 250, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ ThreatLens: Network Malware Detection System")

# Sidebar Navigation
page = st.sidebar.radio("Navigate", [
    "🚨 Alerts Overview", 
    "📄 File Analysis", 
    "🕸️ Network Graph", 
    "📤 Dataset Upload" 
])


if page == "🚨 Alerts Overview":
    st.subheader("Real-Time Security Alerts")
    
    if st.button("🔄 Run Correlation Engine"):
        with st.spinner("Correlating events..."):
            try:
                requests.post(f"{API_URL}/run-analysis")
                st.success("Analysis complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    try:
        response = requests.get(f"{API_URL}/alerts")
        if response.status_code == 200:
            alerts = response.json()
            if not alerts:
                st.info("No alerts found.")
            else:
                df = pd.DataFrame(alerts)
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Alerts", len(df))
                c2.metric("Critical Threats", len(df[df['severity'] == 'critical']) if 'severity' in df.columns else 0)
                c3.metric("Avg Threat Score", f"{df['threat_score'].mean():.2f}" if 'threat_score' in df.columns else "0.0")
                
                st.dataframe(df, use_container_width=True)
        else:
            st.error("Backend connection failed.")
    except Exception as e:
        st.error(f"Backend offline: {e}")

# --- PAGE 2: FILE ANALYSIS (ML + SHAP) ---
elif page == "📄 File Analysis":
    st.subheader("File-Level Malware Analysis")
    
    # 1. Input Area (Hash Only)
    sha256_input = st.text_input("Enter SHA256 Hash", placeholder="e.g., a1b2c3d4e5f6...")
    
    if st.button("Analyze File"):
        if sha256_input:
            try:
                response = requests.get(f"{API_URL}/file/{sha256_input.strip()}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    col1, col2 = st.columns(2)
                    
                    # Left Column: Metadata
                    with col1:
                        st.markdown("#### File Metadata")
                        meta = data.get('metadata', {})
    
                        mc1, mc2 = st.columns(2)
                        mc3, mc4 = st.columns(2)
    
                        with mc1: 
                            st.metric("📂 File Type", meta.get("file_type", "Unknown"))
                        with mc2: 
                            st.metric("📏 File Size", str(meta.get("file_size", "N/A")))
                        with mc3: 
                            st.metric("🧩 Entropy", str(meta.get("entropy", "N/A")))
                        with mc4: 
                            imphash = meta.get("import_hash", "N/A")
                            display_hash = f"{imphash[:8]}..." if imphash and len(str(imphash)) > 8 else imphash
                            st.metric("#️⃣ Import Hash", display_hash)
                    
                    
                    # Right Column: ML Analysis
                    with col2:
                        st.markdown("#### 🧠 ML & SHAP Analysis")
                        analysis = data.get('analysis', {})
                        
                        # Classification Badge
                        classification = analysis.get('classification', 'Unknown')
                        st.markdown(f"""
                            <div style="background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(248, 113, 113, 0.4); border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px;">
                                <p style="margin:0; font-size:0.8rem; color:#fca5a5;">Classification</p>
                                <p style="margin:0; font-size:1.2rem; font-weight:bold; color:white;">{classification}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # SHAP Chart
                        shap_data = analysis.get('shap_values', {})
                        if shap_data:
                            features = list(shap_data.keys())
                            values = list(shap_data.values())
                            
                            fig = go.Figure(go.Bar(
                                x=values, y=features, orientation='h',
                                marker_color=['#ef4444' if v > 0 else '#22c55e' for v in values]
                            ))
                            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), 
                                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                            font_color='white')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No SHAP explainability data available.")

                else:
                    st.error("File not found in database.")
            except Exception as e:
                st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter a SHA256 hash.")


# --- PAGE 3: NETWORK GRAPH ---
elif page == "🕸️ Network Graph":
    st.subheader("Network Topology & Threat Visualization")

    def get_severity_label(score):
        if score > 0.8: return "Critical"
        elif score > 0.6: return "High"
        elif score > 0.3: return "Medium"
        else: return "Normal"

    severity_colors = {"Critical": "#b91c1c", "High": "#ef4444", "Medium": "#f59e0b", "Normal": "#10b981", "C2": "#ffffff"}

    # --- CONTROLS ---
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    with c1:
        view_mode = st.radio("Mode", ["Full Topology", "Single IP"], horizontal=True, label_visibility="collapsed")
    with c2:
        selected_severities = st.multiselect("Filter Severity", ["Critical", "High", "Medium", "Normal"], default=[], placeholder="Select Severity (Empty = All)")
        filter_list = selected_severities if selected_severities else ["Critical", "High", "Medium", "Normal"]
    with c3:
        threshold = st.slider("Min Anomaly Score", 0.0, 1.0, 0.0, step=0.01)

    st.divider()

    # --- MODE 1: SINGLE IP (RESTORED GRAPH) ---
    if view_mode == "Single IP":
        c_search, c_btn = st.columns([3, 1])
        with c_search:
            ip_input = st.text_input("IP Address", "192.168.1.5", label_visibility="collapsed")
        with c_btn:
            fetch_btn = st.button("Fetch Graph", use_container_width=True)

        # Logic to handle both button click and persistent state
        if fetch_btn:
            try:
                resp = requests.get(f"{API_URL}/network/{ip_input}")
                if resp.status_code == 200:
                    st.session_state['single_data'] = resp.json()
                else:
                    st.error("IP Not Found")
                    st.session_state.pop('single_data', None)
            except Exception as e:
                st.error(f"Error: {e}")

        # If data exists, draw the graph
        if 'single_data' in st.session_state:
            data = st.session_state['single_data']
            score = data.get('anomaly_score', 0)
            sev = get_severity_label(score)

            # APPLY FILTERS (Severity + Threshold)
            if (score >= threshold) and (sev in filter_list):
                c_metrics, c_graph = st.columns([1, 3])
                
                with c_metrics:
                    st.metric("Anomaly Score", f"{score:.3f}")
                    st.metric("Severity", sev)
                    st.json(data.get('features', {}))

                with c_graph:
                    net = Network(height='500px', width='100%', bgcolor='#0e1117', font_color='white')
                    
                    # Central Node
                    net.add_node(ip_input, label=ip_input, color=severity_colors.get(sev, "#555"), size=30, title=f"Score: {score}")
                    
                    # Neighbor Nodes (Simulated based on connection count)
                    feat = data.get('features', {})
                    count = int(feat.get('unique_dst_ips', 0))
                    
                    for i in range(min(count, 15)):
                        neighbor_ip = f"10.0.0.{i+10}"
                        net.add_node(neighbor_ip, size=15, color="#555", title="Connected Host")
                        net.add_edge(ip_input, neighbor_ip, color="rgba(255,255,255,0.2)")

                    path = 'html_files'
                    if not os.path.exists(path): os.makedirs(path)
                    net.save_graph(f'{path}/single_graph.html')
                    with open(f'{path}/single_graph.html', 'r', encoding='utf-8') as f:
                        components.html(f.read(), height=520)
            else:
                st.warning(f"IP found, but hidden by filters. (Score: {score:.2f}, Severity: {sev})")

    # --- MODE 2: FULL TOPOLOGY (C2 SERVER LOGIC) ---
    elif view_mode == "Full Topology":
        if 'full_net_data' not in st.session_state:
            if st.button("Load Full Topology"):
                with st.spinner("Fetching data..."):
                    try:
                        resp = requests.get(f"{API_URL}/network-all?limit=300")
                        if resp.status_code == 200:
                            st.session_state['full_net_data'] = resp.json()
                            st.rerun()
                    except Exception as e: st.error(str(e))
        else:
            if st.button("🔄 Refresh"):
                st.session_state.pop('full_net_data', None)
                st.rerun()

        if 'full_net_data' in st.session_state:
            data_pack = st.session_state['full_net_data']
            all_nodes = data_pack.get('nodes', [])
            total = data_pack.get('total_count', 0)
            
            filtered = []
            for node in all_nodes:
                score = node.get('anomaly_score', 0)
                sev = get_severity_label(score)
                if score >= threshold and sev in filter_list:
                    filtered.append((node, sev))

            st.caption(f"Showing **{len(filtered)}** nodes (Total DB: {total})")

            if filtered:
                net = Network(height='650px', width='100%', bgcolor='#0e1117', font_color='white')
                net.force_atlas_2based()
                
                if "Critical" in filter_list or "High" in filter_list:
                    net.add_node("C2_SERVER", label="C2 SERVER (Attacker)", color="#ffffff", shape="diamond", size=40)
                
                if "Normal" in filter_list:
                    net.add_node("GATEWAY", label="Corp Gateway", color="#10b981", shape="square", size=25)

                for node_data, sev in filtered:
                    ip = node_data.get('ip')
                    # Add the IP node first
                    net.add_node(ip, label=ip, title=f"{sev}\nScore: {node_data.get('anomaly_score'):.2f}", color=severity_colors.get(sev, "#555"), size=15)
                    
                    # Connect based on severity
                    if sev == "Critical": 
                        net.add_edge(ip, "C2_SERVER", color="#b91c1c", width=2)
                    elif sev == "High": 
                        net.add_edge(ip, "C2_SERVER", color="#ef4444", dashes=True)
                    elif sev == "Normal": 
                        net.add_edge(ip, "GATEWAY", color="#064e3b")

                path = 'html_files'
                if not os.path.exists(path): os.makedirs(path)
                net.save_graph(f'{path}/full_graph.html')
                with open(f'{path}/full_graph.html', 'r', encoding='utf-8') as f:
                    components.html(f.read(), height=670)
            else:
                st.warning("No nodes match filter.")

elif page == "📤 Dataset Upload":
    st.subheader("Upload Training Datasets")
    st.markdown("Upload your malicious, baseline, and file transfer datasets to train the system")
    
    # Dataset statistics
    try:
        response = requests.get(f"{API_URL}/stats/dataset")
        if response.status_code == 200:
            stats = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", stats['total_records'])
            col2.metric("Malicious", stats['malicious_records'])
            col3.metric("Baseline", stats['baseline_records'])
            col4.metric("File Transfer", stats['file_transfer_records'])
    except:
        st.warning("Could not connect to backend. Make sure the API is running.")
    
    st.divider()
    
    # Upload sections
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🦠 Malicious Dataset")
        malicious_file = st.file_uploader("Upload malicious data (CSV/JSON/LOG)", type=['csv', 'json', 'log'], key='malicious')
        if malicious_file and st.button("Upload Malicious", key='btn_malicious'):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (malicious_file.name, malicious_file, malicious_file.type)}
                    response = requests.post(f"{API_URL}/upload/malicious", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### ✅ Baseline Dataset")
        baseline_file = st.file_uploader("Upload baseline data (CSV/JSON/LOG)", type=['csv', 'json', 'log'], key='baseline')
        if baseline_file and st.button("Upload Baseline", key='btn_baseline'):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (baseline_file.name, baseline_file, baseline_file.type)}
                    response = requests.post(f"{API_URL}/upload/baseline", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col3:
        st.markdown("### 📁 File Transfer Dataset")
        file_transfer_file = st.file_uploader("Upload file transfer data (CSV/JSON/LOG)", type=['csv', 'json', 'log'], key='file_transfer')
        if file_transfer_file and st.button("Upload File Transfer", key='btn_file_transfer'):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (file_transfer_file.name, file_transfer_file, file_transfer_file.type)}
                    response = requests.post(f"{API_URL}/upload/file-transfer", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.divider()
    st.info("💡 **Tip:** Upload CSV, JSON, or Zeek LOG files. The system will automatically parse and store them in MongoDB.")
