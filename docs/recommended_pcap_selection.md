# Recommended PCAP Selection & Quantity Guide
## For File-Aware Network Malware Detection (Big Data Project)

This document explains **how many PCAP files you need**, **which types**, **exact recommended datasets**, and **why each category is necessary** for your upgraded architecture (Zeek + Spark + ML + Dashboard).

---

# 1. How Many PCAPs Do We Need?

To fully demonstrate:
- Zeek file extraction  
- network anomaly detection  
- file-based ML scoring  
- graph visualization  

You only need **3 carefully chosen PCAP files**:

| Type of PCAP | Quantity | Purpose | Typical Size |
|--------------|----------|----------|---------------|
| **Normal traffic** | 1 | Baseline network behavior | 100–200 MB |
| **Attack traffic** | 1 | Provide anomalies for Spark | 200–500 MB |
| **File-transfer traffic** | 1 | Extract files for ML | 50–150 MB |

Total PCAPs needed: **3**

This is **enough** for all logs, extracted files, and dashboard modules.

---

# 2. Recommended PCAP Types (Detailed Explanation)

## 2.1 Normal Traffic PCAP (Baseline)
Purpose:
- Generate realistic network logs  
- Build baseline behavior for Spark anomaly detection  
- Demonstrate normal IP-to-IP interactions for graph visualization  

Recommended sources:
- **MAWI Traffic Archive**  
  https://mawi.wide.ad.jp

Suggested MAWI sample:
- `2020/Day15 sample` or any 100–200MB trace.

---

## 2.2 Attack Traffic PCAP
Purpose:
- Provide **visible anomalies** for Spark to detect  
- Demonstrate malicious IP clusters in network graph  
- Provide realistic malicious HTTP/DNS patterns  

Recommended dataset:
- **CIC-IDS 2018**  
  https://www.unb.ca/cic/datasets/ids-2018.html

Best PCAP files from CIC-IDS 2018:
- **Thursday-WorkingHours-Morning-WebAttacks.pcap**  
- **Friday-WorkingHours-Afternoon-DDos.pcap**

Size: ~150–500MB  
These produce excellent anomalies like:
- DoS  
- DDoS  
- brute force  
- HTTP malicious scans  

---

## 2.3 File-Transfer PCAP (For Extracting Files)
Purpose:
- Generate extracted files (`EXTRACTED_xxxx`) for ML inference  
- Let Zeek build `files.log`  
- Allow Member 3 to run:
  - entropy extraction  
  - byte histogram  
  - LightGBM inference  
  - SHAP explanation  

Recommended dataset:
- **CIC-IDS 2018 Web Attack PCAPs**  
- **CTU-13 Botnet PCAPs** (some contain file transfers)

Look for PCAPs containing:
- HTTP file downloads  
- HTTP POST uploads  
- FTP transfers  
- SMTP attachments  

Suggested CIC-IDS 2018 file:
- **Thursday-WorkingHours-Morning-WebAttacks.pcap**

This PCAP almost always contains several HTTP file transfers.

---

# 3. Final Recommended PCAP Set for the Project

| Purpose | Recommended PCAP | Why It’s Good |
|--------|------------------|----------------|
| **Normal traffic** | Any MAWI daily sample | Clean, realistic baseline traffic |
| **Attack traffic** | CIC-IDS 2018 DDOS or Web Attack day | Good anomalies + diverse protocols |
| **File-transfer** | CIC-IDS 2018 WebAttacks morning | Produces extracted files for ML |

This gives:
- thousands of Zeek logs  
- 5–20 extracted files  
- realistic anomalies  
- ideal input for Spark big-data flow  
- great demonstration value  

---

# 4. Why Not Use More PCAPs?
Because:
- More PCAPs = more GB of logs = slower processing  
- Zeek log volume grows extremely fast  
- Spark needs only **a few hundred MB** to demonstrate big-data processing  
- Dashboard needs **only a handful of extracted files** for ML analysis  

3 PCAPs give you the perfect balance.

---

# 5. Optional 4th PCAP
If you want to be fancy:

**SMTP or FTP traffic PCAP**  
Purpose:
- Extract file attachments  
- Show variety in protocols  

But this is **optional** and not required.

---

# 6. Summary (What You MUST Use)
✔ Exactly **3 PCAPs**  
✔ From CIC-IDS 2018 + MAWI  
✔ Contain:
- normal traffic  
- malicious traffic  
- file transfers  

✔ Enough for:
- Zeek logs  
- Spark analysis  
- ML scoring  
- dashboard  

This setup is 100% adequate and compatible with your upgraded architecture.

