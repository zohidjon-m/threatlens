"""
Load and normalize Zeek logs into a single Spark DataFrame.

The output DataFrame has at least:
- id.orig_h (source IP)
- id.resp_h (destination IP)
- id.resp_p (destination port)
- orig_bytes
- resp_bytes
- logtype
- label (0 = benign, 1 = malicious)
"""

import os
from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config import (
    BASE_DIR,
    LOGS_BASELINE_DIR,
    LOGS_FILETRANSFER_DIR,
    LOGS_MALICIOUS_DIR,
)


def _load_dir_with_label(
    spark: SparkSession,
    dir_path: str,
    label: int,
) -> DataFrame:
    """
    Load all .log files under dir_path (JSON Zeek logs),
    attach 'label' and 'logtype' columns.
    """
    RELEVANT_LOGS = {"conn.log", "http.log", "dns.log", "files.log"}
    files = [
        f for f in os.listdir(dir_path)
        if f.endswith(".log") and f in RELEVANT_LOGS
    ]
    if not files:
        raise RuntimeError(f"No .log files found in {dir_path}")

    dfs = []
    for fname in files:
        fpath = os.path.join(dir_path, fname)

        df = spark.read.json(fpath)

        # sanitize column names (dots → underscores)
        for c in df.columns:
            if "." in c:
                df = df.withColumnRenamed(c, c.replace(".", "_"))

        # attach metadata
        df = df.withColumn("label", F.lit(label))
        df = df.withColumn("logtype", F.lit(fname.replace(".log", "")))

        dfs.append(df)

    # union all logs in this directory
    base = dfs[0]
    for d in dfs[1:]:
        base = base.unionByName(d, allowMissingColumns=True)

    return base


def load_all_logs(spark: SparkSession) -> DataFrame:
    """
    Load baseline, filetransfer and malicious logs into a single DataFrame.
    Labels:
        baseline -> 0
        filetransfer -> 0
        malicious -> 1
    """
    label_map: Dict[str, int] = {
        LOGS_BASELINE_DIR: 0,
        LOGS_FILETRANSFER_DIR: 0,
        LOGS_MALICIOUS_DIR: 1,
    }

    dfs = []

    for subdir, label in label_map.items():
        full = os.path.join(BASE_DIR, subdir)
        df = _load_dir_with_label(spark, full, label)
        dfs.append(df)

    # union everything
    base = dfs[0]
    for d in dfs[1:]:
        base = base.unionByName(d, allowMissingColumns=True)

    # normalize some important numeric columns
    # if missing, they'll be null -> cast to double

    if "id_resp_p" in base.columns:
        base = base.withColumn("id_resp_p", F.col("id_resp_p").cast("int"))
    else:
        base = base.withColumn("id_resp_p", F.lit(None).cast("int"))

    for col in ["orig_bytes", "resp_bytes"]:
        if col in base.columns:
            base = base.withColumn(col, F.col(col).cast("double"))
        else:
            base = base.withColumn(col, F.lit(0.0))

    return base

# def main():
#         spark = SparkSession.builder.appName("demo").getOrCreate()
#         df = load_all_logs(spark)
#         print("\n=== RAW LOGS SCHEMA ===")
#         df.printSchema()
#
#         print("\n=== RAW LOGS SAMPLE ===")
#         df.show(10, truncate=True)
#
# if __name__ == "__main__":
#     main()