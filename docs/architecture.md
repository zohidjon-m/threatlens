# System Architecture Documentation

## 1. Purpose

This document defines the complete architecture of the File-Aware Network Malware Detection System.  
It describes all major components, their responsibilities, data flows, interfaces, and deployment structure.

The architecture is designed for:
- network traffic analysis (Zeek)
- big data processing (Spark)
- machine-learning malware detection (EMBER + LightGBM)
- explainability (SHAP)
- threat intelligence enrichment
- graph-based network visualization
- consolidated threat scoring
- optional real-time streaming (Kafka – non-core)

---

## 2. High-Level Architecture Diagram (Text Version)

```
             ┌────────────────────┐
             │       PCAPs        │
             └─────────┬──────────┘
                       │
                (1) Zeek Engine
                       │
         ┌─────────────┼────────────────┬──────────────┐
         │              │                │               │
   conn.log        http.log         dns.log         files.log
         │              │                │               │
         └─────── Structured Logs & Extracted Files ─────┘
                       │
                (2) Data Ingestion
                       │
          Files → MongoDB (`files`)
          Logs  → Spark (HDFS/local)
                       │
              (3) Big Data Processing
                       │
         Spark → anomaly_score → MongoDB (`network_anomalies`)
                       │
        (4) Malware ML Engine (EMBER → LightGBM)
                       │
      file_features → malware_prob + shap → MongoDB (`ml_scores`)
                       │
        (5) Threat Intelligence (VirusTotal/OTX)
                       │
       intel_flag → MongoDB (`threat_intel`)
                       │
            (6) Correlation Engine (FastAPI)
                       │
     malware_prob + anomaly_score + intel_flag → threat_score
                       │
             MongoDB (`alerts`) ← stored results
                       │
           (7) Dashboard (Streamlit / React)
                       │
        Visualizations: Alerts, SHAP, Graph, Anomalies
```

---

## 3. Component Descriptions

### **3.1 Zeek Pipeline**
- Input: PCAP files
- Output: structured logs + extracted files
- Responsible for:
  - parsing network protocols (HTTP, DNS, SSL, SMTP)
  - extracting transferable files from traffic
  - generating event logs that Spark and ML pipeline consume

---

### **3.2 Spark Big Data Pipeline**
- Input: Zeek logs (conn/http/dns/logs)
- Output: anomaly_score per IP
- Responsibilities:
  - load logs from filesystem
  - compute behavioral features:
    - number of connections
    - bytes sent/received
    - unique destination IPs
    - DNS entropy (detect DGAs)
    - rare port usage
  - run anomaly detection model (IsolationForest / KMeans)
  - publish results to MongoDB (`network_anomalies`)

---

### **3.3 ML Malware Detection Engine**
- Model: LightGBM trained on EMBER dataset
- Responsibilities:
  - extract lightweight static features from Zeek files:
    - entropy
    - byte histogram (256 bins)
    - number of printable strings
    - average string length
  - infer malware probability
  - compute SHAP explainability vector
  - store results to MongoDB (`ml_scores`)

---

### **3.4 Threat Intelligence Integration**
- Query external services:
  - VirusTotal (public API)
  - MalwareBazaar
  - AlienVault OTX
- Responsibilities:
  - enrich file hashes with TI results
  - mark known malicious hashes
  - store into MongoDB (`threat_intel`)

---

### **3.5 Correlation Engine (FastAPI Service)**
- Combines signals from:
  - `ml_scores`
  - `network_anomalies`
  - `threat_intel`
  - `files`
- Computes:
```
threat_score = 
    0.6 * malware_prob +
    0.25 * anomaly_score +
    0.15 * intel_flag
```
- Writes alerts to MongoDB (`alerts`)

---

### **3.6 Dashboard**
Built with Streamlit (or React + FastAPI)

Pages:
1. **Overview**
2. **Alerts Table**
3. **File Analysis (ML + SHAP + TI)**
4. **Network Anomaly Visualization**
5. **Network Graph Visualization**

---

## 4. Optional Component (NOT Core)

### **Kafka Streaming Layer**
If time permits:
- Zeek logs forwarded to Kafka topics
- Spark Streaming consumes logs in micro-batches
- Real-time anomaly and file scoring pipeline
- Live dashboard updates

This is **optional only**.

---

## 5. Technology Stack Summary

### **Traffic Analysis**
- Zeek

### **Big Data**
- Apache Spark (batch mode)
- HDFS or local filesystem

### **Machine Learning**
- LightGBM
- EMBER dataset
- SHAP

### **Threat Intelligence**
- VirusTotal API
- OTX
- MalwareBazaar

### **Storage**
- MongoDB

### **Backend**
- FastAPI

### **Dashboard / UI**
- Streamlit or React

### **Optional Streaming**
- Kafka (optional)
- Spark Streaming (optional)

---

## 6. Deployment Architecture

### **Local Deployment**
- Zeek runs on local PCAP files
- Spark runs in local mode
- MongoDB local instance
- FastAPI backend
- Streamlit dashboard

### **Extended Deployment (if ambitious)**
- Spark on standalone cluster
- MongoDB Atlas
- Kafka broker cluster
- Deployed dashboard

---

## 7. Component Interaction Table

| Component | Inputs | Outputs | Stored In | Consumed By |
|----------|--------|---------|-----------|--------------|
| Zeek | PCAP | logs + files | FS/Mongo | Spark, ML |
| Spark | logs | anomaly_score | MongoDB | Correlation |
| ML Engine | files | malware_prob + shap | MongoDB | Correlation |
| Threat Intel | sha256 | intel_flag | MongoDB | Correlation |
| Correlation Engine | all signals | threat_score | MongoDB | Dashboard |
| Dashboard | API | visualizations | N/A | Users |

---

## 8. Final Notes

This architecture supports:
- scalable log processing  
- ML-based malware detection  
- explainable security decisions  
- integrated threat intel  
- unified risk scoring  
- optional real-time extensions  

The design aligns with enterprise NDR/SIEM systems while remaining implementable within a 3–4 week academic timeline.
