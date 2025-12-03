# Integration Plan

This document defines the official integration strategy for the File-Aware Network Malware Detection System.  
It ensures that independently developed modules connect smoothly during final assembly.

The integration process must follow the order and rules defined here.

---

# 1. Integration Objectives

- Integrate Zeek → MongoDB ingestion
- Integrate Spark anomaly results
- Integrate ML malware predictions + SHAP
- Integrate threat intelligence lookups
- Integrate correlation engine
- Integrate dashboard with unified API
- Validate data contracts between all modules
- Perform end-to-end testing before final demo

The goal is **a fully functional, stable, and consistent end-to-end system**.

---

# 2. Integration Timeline (Recommended)

### **Week 1**
- Zeek pipeline ready
- Spark pipeline skeleton ready
- ML training finished
- Dashboard skeleton ready

### **Week 2**
- Zeek logs flow into MongoDB
- ML scoring runs on extracted files
- Spark anomaly scoring outputs saved to MongoDB

### **Week 3**
- Correlation engine integrates all signals
- Dashboard connected to backend API
- Graph visualization loaded with mock data → then real data
- Threat intel added

### **Week 4**
- End-to-end integration
- Error handling + validation
- Load testing with full PCAP dataset
- Final demo preparation

---

# 3. Integration Dependencies

| Component | Depends On | Reason |
|-----------|-------------|--------|
| Spark pipeline | Zeek logs | Needs parsed log data |
| ML engine | Zeek extraction | Needs files to score |
| Threat intel | ML engine | Needs file hashes |
| Correlation engine | Spark + ML + TI | Must combine all signals |
| Dashboard | API | Must query integrated backend |
| API | All modules | Needs consistent schema |

---

# 4. Integration Interfaces (Critical Contracts)

These must be fixed before integration begins.

## **4.1 MongoDB Collection Contracts**
Each module writes data in the agreed schemas:
- `files`
- `ml_scores`
- `network_anomalies`
- `threat_intel`
- `alerts`

All fields must follow the schema defined in `db_schema.md`.

**No renaming, restructuring, or omitting fields after Week 1.**

---

## **4.2 API Contract**
Backend → Dashboard communication uses the structure defined in `api_spec.yaml`.

**No endpoint name or response structure changes during integration.**

---

## **4.3 File Storage Contract**
Extracted files must be stored as:

```
/data/extracted_files/<sha256>.bin
```

ML engine, TI module, and correlation engines all rely on this.

---

## **4.4 Timestamp Standards**
All timestamps must:
- be UNIX float seconds
- use UTC
- be stored under `timestamp` field

---

# 5. Integration Steps (Technical)

---

## **Step 1 — Integrate Zeek → MongoDB**
- Verify `files` collection receives proper metadata
- Validate sha256, src_ip, dst_ip, file_path correctness
- Test 10 random entries manually

**Output:** Zeek → DB ingestion works reliably

---

## **Step 2 — Integrate Spark → MongoDB**
- Spark loads logs from Zeek output directory
- Compute features → anomaly scores
- Write to `network_anomalies`
- Validate same IP addresses match Zeek's logs

**Output:** Behavioral data stored and consistent

---

## **Step 3 — Integrate ML Engine → MongoDB**
- ML loads extracted files (sha256.bin)
- Generates malware_prob + SHAP
- Writes to `ml_scores`
- Ensure hash names match Zeek extraction

**Output:** ML pipeline linked to Zeek

---

## **Step 4 — Integrate Threat Intelligence**
- ML engine triggers TI lookup
- TI results stored under `threat_intel`
- Verify format: known_malicious, sources, tags

**Output:** Enriched threat context online

---

## **Step 5 — Integrate Correlation Engine**
The correlation engine must:

- join `files`, `ml_scores`, `network_anomalies`, `threat_intel`
- compute `threat_score`
- write results to `alerts`
- produce stable API responses

**Output:** Unified alert entries

---

## **Step 6 — Integrate Backend API**
1. Connect MongoDB queries  
2. Provide endpoints using `/alerts`, `/files/{sha256}`, `/ip/{address}`, `/graph`  
3. Add pagination + filters if needed  
4. Validate responses match OpenAPI spec  

**Output:** Fully operational backend

---

## **Step 7 — Integrate Dashboard**
1. Connect dashboard pages to API  
2. Populate:
   - Alerts table
   - File analysis panel
   - SHAP visualization
   - Network anomaly charts
   - Network graph visualization
3. Add loading indicators and error messages

**Output:** Complete user-facing interface

---

# 6. Integration Testing

## **6.1 Test Plan**
- Unit test each module independently
- Integration test each pair of modules
- Run end-to-end pipeline with small PCAP (100 MB)
- Run final full dataset test (1–3 GB PCAP)

## **6.2 What to Check**
- Hash consistency
- Timestamp consistency
- DB connection stability
- API latency (<200 ms)
- Dashboard rendering data correctly
- No missing documents across collections

---

# 7. Failure Handling & Fallbacks

### If Zeek fails:  
Use pre-generated logs

### If Spark job fails:  
Fallback to cached anomaly results

### If ML engine fails:  
Return `"malware_prob": null` but keep system running

### If TI API rate limits:  
Mark `"intel_flag": false`, continue pipeline

### If dashboard fails:  
Backend still serves data via API

---

# 8. Final Demo Checklist

- end-to-end run works with real PCAP  
- dashboard updates live or near-live  
- threat alerts appear with:
  - malware score
  - anomaly score
  - threat intel result
- SHAP explanation is visible  
- graph visualization shows risky IPs  
- no errors or missing fields in logs  
- API returns consistent JSON  

---

# 9. Summary

This integration plan ensures:
- independent module development  
- smooth merging of pipelines  
- stable data contracts  
- predictable behavior  
- clean end-to-end execution  

Following this plan prevents last-week integration disasters.
