#THE DIRECTORIES ARE WSL2 COMPATIBLE NOT WINDOWS
# Base directory where Zeek logs live
BASE_DIR = r"/mnt/d/sejong_major/projects/threatlens/dataset"

# Relative folder names inside BASE_DIR
LOGS_BASELINE_DIR = "logs_baseline"
LOGS_FILETRANSFER_DIR = "logs_filetransfer"
LOGS_MALICIOUS_DIR = "logs_malicious"

# Output directory (for JSON/parquet, etc.)
OUTPUT_DIR = "/mnt/d/sejong_major/projects/threatlens/dataset/output"

# MongoDB connection (used by write_outputs.py)
# Example full URI for a collection:
#   "mongodb://localhost:27017/threatlens.anomaly_scores"
MONGO_URI = "...."

# KMeans parameters
KMEANS_K = 2            # 2 clusters: normal vs suspicious-ish
KMEANS_MAX_ITER = 50
KMEANS_SEED = 42

# Columns that will be used as features in anomaly model
FEATURE_COLUMNS = [
    "conn_count",
    "unique_dest_ips",
    "total_orig_bytes",
    "total_resp_bytes",
    "avg_dns_entropy",
    "rare_port_count",
]

# Control how many partitions to use for final outputs
OUTPUT_PARTITIONS = 1
