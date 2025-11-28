# Team Task Breakdown & Weekly Execution Plan
## File-Aware Network Malware Detection System (Big Data Project)

This document defines **clear responsibilities**, **deliverables**, **weekly goals**, and **learning resources** for each of the four team members.  
The structure ensures **parallel development**, **zero bottlenecks**, and **smooth integration** by Week 3–4.

---

# 🚀 Project Roles Overview (4 Members)

Each member owns an independent subsystem:
1. **Network & Zeek**
2. **Big Data / Spark**
3. **ML Malware Detection + SHAP Explainability**
4. **Backend + Dashboard**

---

# 1. Member 1 — Network & Zeek 

## **Responsibilities**
- Select PCAP datasets (CIC-IDS 2018, CTU-13, MAWI).
- Run Zeek on PCAPs.
- Generate logs: `conn.log`, `http.log`, `dns.log`, `files.log`.
- Enable file extraction (`EXTRACTED_xxxxx` files).
- Write scripts to store logs + file metadata into MongoDB.
- Maintain directory structure for extracted files.
- Share cleaned logs & files with members 2, 3, 4.

## **Deliverables**
- Folder containing Zeek logs.
- Extracted file directory.
- MongoDB insertion script for logs.
- Documentation on dataset + commands used.

## **Weekly Plan**
### **Week 1**
- Install Zeek.
- Download PCAPs.
- Run Zeek on sample PCAPs.
- Verify file extraction works.
- Finalize dataset for project.

### **Week 2**
- Automate the processing pipeline.
- Push logs + files into MongoDB.

### **Week 3**
- Support Member 2 and 4 with real log samples.

### **Week 4**
- Optimize Zeek configs.
- Generate additional logs if needed.

## **Learning Resources**
- Zeek official docs: https://docs.zeek.org
- YouTube: “Zeek for Network Security Monitoring”
- PCAP datasets:  
  CIC-IDS 2018: https://www.unb.ca/cic/datasets/ids-2018.html  
  CTU-13: https://www.stratosphereips.org/datasets-ctu13  
  MAWI: http://mawi.wide.ad.jp/

---

# 2. Member 2 — Big Data / Spark 

## **Responsibilities**
- Load Zeek logs into Apache Spark.
- Extract features:
  - number of connections per IP
  - unique destination IPs
  - bytes sent/received
  - DNS entropy
  - rare ports count
- Train anomaly detection model (IsolationForest or KMeans).
- Write anomaly scores to MongoDB.
- Produce JSON outputs for dashboard use.

## **Deliverables**
- Spark ETL scripts for:
  - loading logs
  - cleaning logs
  - feature generation
- Anomaly detection model
- MongoDB write-back script

## **Weekly Plan**
### **Week 1**
- Install Spark.
- Load sample JSON logs.
- Begin writing ETL scripts.

### **Week 2**
- Finish feature engineering code.
- Build anomaly detection model.
- Store anomaly_score per IP into MongoDB.

### **Week 3**
- Tune anomaly detection model.
- Provide JSON outputs for Member 4.

### **Week 4**
- Optimize Spark jobs.
- Help integrate with Kafka if optional upgrade is attempted.

## **Learning Resources**
- Spark (PySpark) guide: https://spark.apache.org/docs/latest/api/python/
- Big Data tutorials: https://www.datacamp.com/courses/introduction-to-pyspark
- IsolationForest basics: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

---

# 3. Member 3 — Malware ML + SHAP Explainability 

## **Responsibilities**
- Download EMBER dataset.
- Train LightGBM malware classifier.
- Implement lightweight static feature extractor for extracted files:
  - entropy
  - file size
  - byte histogram (256 bins)
  - string statistics
- Run inference on extracted files.
- Produce SHAP explanations for each file.
- Integrate Threat Intelligence (VirusTotal, OTX, MalwareBazaar).
- Save results into MongoDB.

## **Deliverables**
- LightGBM model file.
- Feature extraction script.
- Inference script.
- SHAP explanation generator.
- Threat intelligence lookup script.
- MongoDB write-back scripts.

## **Weekly Plan**
### **Week 1**
- Download EMBER dataset.
- Perform ML model training using precomputed features.
- Learn SHAP basics.

### **Week 2**
- Implement real file feature extraction.
- Add inference pipeline.
- Produce malware_prob for all files.

### **Week 3**
- Add SHAP visualizations.
- Add Threat Intelligence integration.

### **Week 4**
- Tune the model.
- Optimize SHAP output for dashboard.

## **Learning Resources**
- EMBER dataset: https://github.com/endgameinc/ember
- LightGBM: https://lightgbm.readthedocs.io
- SHAP explainability: https://shap.readthedocs.io
- Threat Intelligence APIs:
  - OTX: https://otx.alienvault.com/api
  - MalwareBazaar: https://bazaar.abuse.ch/api/

---

# 4. Member 4 — Backend + Dashboard 

## **Responsibilities**
- Build FastAPI backend for:
  - querying alerts
  - fetching file data
  - fetching anomaly scores
  - fetching threat intel + SHAP
- Build dashboard (Streamlit or React).
- Build network graph visualization:
  - nodes = IPs
  - edges = connections
  - highlight suspicious nodes based on threat_score
- Implement correlation engine:
  ```
  threat_score = 
     0.6 * malware_prob
   + 0.25 * anomaly_score
   + 0.15 * intel_flag
  ```
- Integrate all frontend pages.

## **Deliverables**
- FastAPI backend project.
- Dashboard with:
  - Alerts List
  - File Analysis Page
  - SHAP plots
  - Threat Intel section
  - Network Graph View
  - Anomaly summary pages

## **Weekly Plan**
### **Week 1**
- Define API structure.
- Build dashboard skeleton (mock JSON data).

### **Week 2**
- Connect to MongoDB.
- Integrate ML outputs + anomaly scores.

### **Week 3**
- Implement graph visualization.
- Add SHAP panels and threat intel section.

### **Week 4**
- Full system integration.
- Final demo preparation.

## **Learning Resources**
- FastAPI: https://fastapi.tiangolo.com
- Streamlit: https://docs.streamlit.io
- PyVis (network graph): https://pyvis.readthedocs.io/
- MongoDB: https://www.mongodb.com/docs/

---

# 📅 4-Week Timeline (All Members)

## **Week 1 — Foundation Setup**
- Zeek installed, sample logs generated (Member 1)
- Spark ETL beginnings (Member 2)
- ML model trained on EMBER (Member 3)
- Backend + dashboard skeleton (Member 4)

## **Week 2 — Core Processing Complete**
- File extraction + MongoDB loader done (Member 1)
- Network anomaly model complete (Member 2)
- Static file inference pipeline complete (Member 3)
- Dashboard connected to DB (Member 4)

## **Week 3 — Integration**
- ML + anomaly + intel pipelines integrated
- SHAP outcome added
- Network graph visualization complete
- Correlation engine implemented

## **Week 4 — Testing + Report + Optional Kafka**
- System QA testing
- Write final report + slides
- Optional: Kafka real-time extension

---

# 🧠 Expected Outputs from Each Member

| Member | Output | Description |
|--------|--------|-------------|
| **1. Zeek Engineer** | `logs/`, `files/`, MongoDB loader | Foundation dataset + ingestion |
| **2. Spark Engineer** | `anomaly_score.json`, ETL scripts | Big Data + anomaly detection |
| **3. ML Engineer** | `model.pkl`, SHAP JSON, intel JSON | Malware detection + XAI + TI |
| **4. Backend/Dashboard** | API, UI, Graph, Alerts | Final visible product |

---

# 🎯 Final Notes

This task division is optimized so everyone works **independently in parallel**, with integration only needed in Week 3.  
This guarantees the system is finished even under time pressure, while leaving room for optional Kafka streaming.

