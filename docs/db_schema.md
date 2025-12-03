# Database Schema (MongoDB)

This document defines the **official MongoDB schema** for all collections used in the File-Aware Network Malware Detection System.  
All team members must strictly follow these schemas so that pipelines integrate correctly.

MongoDB is chosen because:
- Zeek logs are JSON-like  
- Flexible schema needed for evolving ML features  
- Fast reads for dashboard queries  
- Natural fit for time-series security records  

---

# 1. Collections Overview

The system uses **five core collections**:

1. `files` – metadata for extracted files from Zeek  
2. `ml_scores` – malware classification results & SHAP explainability  
3. `network_anomalies` – Spark-computed anomaly scores per IP  
4. `threat_intel` – external intelligence enrichment (VirusTotal, OTX, etc.)  
5. `alerts` – final correlated threat alerts for dashboard visualization  

---

# 2. Collection Schemas

---

## 2.1 `files`
Stores metadata for each file extracted by Zeek.

### Fields
- `fuid`: string — Zeek File Unique ID  
- `sha256`: string — SHA256 hash  
- `mime_type`: string — File MIME type  
- `size`: int — File size in bytes  
- `src_ip`: string — IP address of sender  
- `dst_ip`: string — IP address of receiver  
- `timestamp`: float — UNIX timestamp (UTC)  
- `file_path`: string — Local file path  
- `zeek_session`: string — Zeek connection UID  

### Example
```json
{
  "fuid": "FZH5x93Pb2",
  "sha256": "bb1f2e4b6c3d...c29",
  "mime_type": "application/x-dosexec",
  "size": 58112,
  "src_ip": "10.0.0.12",
  "dst_ip": "8.8.8.8",
  "timestamp": 1730002312.22,
  "file_path": "/data/extracted_files/bb1f2e4b6c3d.bin",
  "zeek_session": "CQ2h1J3Ena1"
}
```

---

## 2.2 `ml_scores`
Stores malware ML predictions + SHAP explainability.

### Fields
- `sha256`: string  
- `malware_prob`: float  
- `shap_values`: object  
- `top_features`: object  
- `model_version`: string  
- `timestamp`: float  

### Example
```json
{
  "sha256": "bb1f2e4b6c3d...c29",
  "malware_prob": 0.927,
  "shap_values": {
    "entropy": 0.31,
    "byte_histogram_23": 0.18,
    "num_strings": -0.12
  },
  "top_features": {
    "entropy": "High entropy suggests obfuscation or packing",
    "byte_histogram_23": "Unusual byte frequency distribution"
  },
  "model_version": "lightgbm_v1.2",
  "timestamp": 1730002320.12
}
```

---

## 2.3 `network_anomalies`
Spark-computed anomaly score per IP.

### Fields
- `ip`: string  
- `anomaly_score`: float  
- `features`: object  
- `timestamp`: float  

### Example
```json
{
  "ip": "10.0.0.12",
  "anomaly_score": 0.74,
  "features": {
    "num_connections": 153,
    "unique_dst_ips": 28,
    "avg_bytes_sent": 30211.4,
    "avg_bytes_received": 9341.7,
    "dns_entropy": 4.23,
    "rare_ports_count": 5
  },
  "timestamp": 1730002491.01
}
```

---

## 2.4 `threat_intel`
Threat Intelligence enrichment information.

### Fields
- `sha256`: string  
- `known_malicious`: bool  
- `sources`: array(string)  
- `tags`: array(string)  
- `first_seen`: string  
- `timestamp`: float  

### Example
```json
{
  "sha256": "bb1f2e4b6c3d...c29",
  "known_malicious": true,
  "sources": ["VirusTotal", "OTX"],
  "tags": ["ransomware", "packed", "trojan"],
  "first_seen": "2023-04-12",
  "timestamp": 1730002500.19
}
```

---

## 2.5 `alerts`
Final correlated alerts.

### Fields
- `ip`: string  
- `sha256`: string  
- `malware_prob`: float  
- `anomaly_score`: float  
- `intel_flag`: bool  
- `threat_score`: float  
- `timestamp`: float  

### Example
```json
{
  "ip": "10.0.0.12",
  "sha256": "bb1f2e4b6c3d...c29",
  "malware_prob": 0.927,
  "anomaly_score": 0.74,
  "intel_flag": true,
  "threat_score": 0.86,
  "timestamp": 1730002505.88
}
```

---

# 3. Relationships

- `files.sha256` ↔ `ml_scores.sha256`  
- `files.sha256` ↔ `threat_intel.sha256`  
- `files.src_ip` ↔ `network_anomalies.ip`  
- `alerts` consolidates all signals  

---

# 4. Rules & Constraints

- All timestamps must be UNIX (float, UTC)  
- SHA256 is the primary key across collections  
- Field names must not change once development starts  
- Dashboard only reads from DB — no direct file access  
