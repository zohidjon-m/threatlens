# Data Flow Documentation

This document explains **how data moves through the entire system**, from raw network traffic to final threat alerts displayed in the dashboard.  
It defines inputs, outputs, formats, intermediate transformations, and component interactions.  
All team members must follow this flow to ensure compatibility and smooth integration.

---

# 1. High-Level Pipeline Overview

```
PCAP → Zeek → Logs & Extracted Files → Spark (Big Data) → 
Network Anomalies → ML Engine → Malware Probabilities + SHAP →
Threat Intelligence → Correlation Engine → Alerts → Dashboard
```

This flow is broken down into detailed steps below.

---

# 2. Detailed Step-by-Step Data Flow

---

## **2.1 Step 1 — PCAP Input**
**Source:**  
- Offline dataset (CIC-IDS, CTU-13, UNSW-NB15)  
- Manually downloaded network traffic captures  

**Output:**  
- Raw `.pcap` files fed into Zeek

**No transformation here.**

---

## **2.2 Step 2 — Zeek Processing**
Zeek parses the PCAP and outputs:

### **Logs:**
- `conn.log`
- `http.log`
- `dns.log`
- `files.log`
- optional:
  - `ssl.log`
  - `weird.log`

All logs are emitted as **JSON-like line-based records**.

### **Extracted Files:**
Zeek reconstructs network-transferred files and stores them at:

```
/data/extracted_files/EXTRACTED_<id>
```

### **Outputs Written To:**
- Filesystem  
- `files` collection (basic metadata)

---

## **2.3 Step 3 — Log Loading Into Spark**
Spark ingests Zeek logs using:

```
spark.read.json()
```

**Input:**  
- conn.log  
- http.log  
- dns.log  
- files.log  

**Transformations:**  
- cleanup of missing fields  
- normalization of timestamps  
- flattening nested JSON objects  

**Output:**  
- clean Spark DataFrames  
- stored temporarily in memory/HDFS  

---

## **2.4 Step 4 — Feature Engineering (Spark)**
Spark computes behavioral features per IP:

### Example features:
- number of total connections  
- number of unique destination IPs  
- average bytes sent/received  
- DNS query counts  
- entropy of DNS domain names  
- rare port usage count  
- failed connections  

These are aggregated using Spark SQL / PySpark groupby operations.

**Output:**  
A Spark-generated feature vector for each IP.

---

## **2.5 Step 5 — Network Anomaly Model (Spark ML)**
Spark runs an anomaly detection algorithm:

- IsolationForest (recommended)  
- OR KMeans clustering + distance scoring  

**Input:**  
Spark feature vector (per IP)

**Output:**  
Each IP gets:

```
anomaly_score ∈ [0, 1]
```

**Stored in:**  
`network_anomalies` collection in MongoDB.

---

## **2.6 Step 6 — Static File Feature Extraction**
For each extracted file, compute local features:

- entropy  
- file size  
- byte histogram (256 bins)  
- num printable strings  
- avg string length  

**Input:**  
`/data/extracted_files/<sha256>.bin`

**Output:**  
A numerical feature vector.

---

## **2.7 Step 7 — ML Malware Prediction**
The LightGBM model outputs:

- `malware_prob`  
- SHAP explanation vector  
- top contributing features  

**Input:**  
Static feature vector

**Output Stored In MongoDB (`ml_scores`):**
```
{
  sha256,
  malware_prob,
  shap_values,
  top_features,
  timestamp
}
```

---

## **2.8 Step 8 — Threat Intelligence Enrichment**
For each file hash (sha256), query:

- VirusTotal  
- MalwareBazaar  
- AlienVault OTX  

**Output stored in `threat_intel`:**

```
known_malicious,
sources,
tags,
first_seen,
timestamp
```

---

## **2.9 Step 9 — Correlation Engine**
The engine collects data from three upstream sources:

- `ml_scores` → malware_prob  
- `network_anomalies` → anomaly_score  
- `threat_intel` → intel_flag  

And calculates:

```
threat_score = 
      0.6 * malware_prob +
      0.25 * anomaly_score +
      0.15 * intel_flag
```

**Output stored in `alerts`:**
```
ip, sha256, threat_score, timestamp
```

---

## **2.10 Step 10 — Dashboard**
Dashboard queries:

- `alerts`  
- `files`  
- `ml_scores`  
- `network_anomalies`  
- `threat_intel`  

It displays:
- threat alerts  
- file risk details  
- SHAP explanations  
- network anomaly graphs  
- IP-to-IP traffic graph  

No direct file or Spark access — only through MongoDB.

---

# 3. Data Contracts & Formats

---

## **3.1 Timestamp Rules**
- UNIX timestamp (float)
- UTC timezone **always**

---

## **3.2 File Naming Rules**
Extracted files must be stored as:

```
/data/extracted_files/<sha256>.bin
```

This ensures ML + TI + correlation reference the same filename.

---

## **3.3 Common JSON Structure Requirements**

### **IP fields**
```
src_ip, dst_ip, ip
```

### **Hash field**
```
sha256
```

### **Model fields**
```
malware_prob, anomaly_score, intel_flag
```

---

# 4. Ownership Summary (Who Produces What)

| Step | Module | Owner | Output |
|------|--------|--------|---------|
| 1 | PCAP | N/A | raw traffic |
| 2 | Zeek | Member 1 | logs + files |
| 3 | Spark Load | Member 2 | DF logs |
| 4 | Spark FE | Member 2 | IP feature vectors |
| 5 | Spark ML | Member 2 | anomaly_score |
| 6 | File FE | Member 3 | file features |
| 7 | Malware ML | Member 3 | malware_prob + SHAP |
| 8 | Threat Intel | Member 3 | intel_flag |
| 9 | Correlation | Member 4 | alerts |
| 10 | Dashboard | Member 4 | UI |

---

# 5. End-to-End Flow Diagram

```
       PCAP 
         ↓
       Zeek
         ↓
 ┌───────┬────────────────────────────┐
 │ Logs  │                             │   Extracted Files
 │       ↓                             │          ↓
 │   Spark Load → Spark FE → Anomaly ML│      ML Engine
 │       ↓            ↓                │          ↓
 │   network_anomalies                 │      ml_scores
 │                                     │
 └─────────────────────────────────────┘
                 ↓   Threat Intel
                 ↓        ↓
         Correlation Engine
                 ↓
               alerts
                 ↓
             Dashboard
```

---

# 6. Summary

This document defines the **exact flow of data** across the system, ensuring:

- every module knows its inputs and outputs  
- all components speak the same data language  
- integration is stable  
- team members can work fully in parallel  

This is the system's master data contract.
