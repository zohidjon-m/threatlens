"""
Feature engineering for network anomaly detection.

Input:
    Raw Zeek DataFrame from load_logs.load_all_logs()

Output:
    IP-level feature DataFrame with columns:
        ip,
        conn_count,
        unique_dest_ips,
        total_orig_bytes,
        total_resp_bytes,
        avg_dns_entropy,
        rare_port_count,
        label (majority label per IP, mainly for evaluation)
"""

from functools import reduce
from math import log2
from typing import Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler, StandardScaler
from config import FEATURE_COLUMNS


def _compute_connection_features(df: DataFrame) -> DataFrame:
    """Connections, unique destination IPs, bytes per source IP."""
    # connection count
    conn_count = (
        df.groupBy("id_orig_h")
        .count()
        .withColumnRenamed("id_orig_h", "ip")
        .withColumnRenamed("count", "conn_count")
    )

    # unique destination IPs
    uniq_dest = (
        df.groupBy("id_orig_h")
        .agg(F.countDistinct("id_resp_h").alias("unique_dest_ips"))
        .withColumnRenamed("id_orig_h", "ip")
    )

    # bytes
    bytes_sum = (
        df.groupBy("id_orig_h")
        .agg(
            F.sum("orig_bytes").alias("total_orig_bytes"),
            F.sum("resp_bytes").alias("total_resp_bytes"),
        )
        .withColumnRenamed("id_orig_h", "ip")
    )

    # label per IP (majority label)
    label = (
        df.groupBy("id_orig_h")
        .agg(F.avg("label").alias("label_mean"))
        .withColumn("label", F.when(F.col("label_mean") >= 0.5, 1).otherwise(0))
        .select(
            F.col("id_orig_h").alias("ip"),
            "label",
        )
    )

    # join them
    dfs: Iterable[DataFrame] = [conn_count, uniq_dest, bytes_sum, label]
    base = reduce(lambda a, b: a.join(b, "ip", "outer"), dfs)

    # fill nulls with 0 in numerics
    for c in ["conn_count", "unique_dest_ips", "total_orig_bytes", "total_resp_bytes"]:
        base = base.na.fill({c: 0.0})

    base = base.na.fill({"label": 0})

    return base


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    from collections import Counter

    counts = Counter(s)
    total = len(s)
    return -sum((cnt / total) * log2(cnt / total) for cnt in counts.values())


entropy_udf = F.udf(_shannon_entropy, DoubleType())


def _compute_dns_entropy(df: DataFrame) -> DataFrame:
    """
    Compute average DNS query entropy per IP.
    Only uses rows where logtype == 'dns' and a 'query' field exists.
    """
    if "logtype" not in df.columns or "query" not in df.columns:
        # no DNS data -> return empty
        return df.select(
            F.lit(None).cast("string").alias("ip"),
            F.lit(0.0).alias("avg_dns_entropy"),
        ).limit(0)

    dns = df.filter(df.logtype == "dns")

    if "id_orig_h" not in dns.columns:
        return dns.select(
            F.lit(None).cast("string").alias("ip"),
            F.lit(0.0).alias("avg_dns_entropy"),
        ).limit(0)

    dns = dns.select("id_orig_h", "query")

    dns = dns.withColumn("entropy", entropy_udf("query"))

    dns_agg = (
        dns.groupBy("id_orig_h")
        .agg(F.avg("entropy").alias("avg_dns_entropy"))
        .withColumnRenamed("id_orig_h", "ip")
    )

    return dns_agg


def _compute_rare_ports(df: DataFrame, rarity_threshold: int = 5) -> DataFrame:
    """
    Count how many connections per source IP use 'rare' destination ports.
    Rare = ports that appear fewer than rarity_threshold times overall.
    """
    if "id.resp_p" not in df.columns or "id_orig_h" not in df.columns:
        return df.select(
            F.lit(None).cast("string").alias("ip"),
            F.lit(0.0).alias("rare_port_count"),
        ).limit(0)

    port_counts = (
        df.groupBy("id_resp_p")
        .count()
        .filter(F.col("count") < rarity_threshold)
        .select("id_resp_p")
    )

    rare = (
        df.join(port_counts, on="id_resp_p", how="inner")
        .groupBy("id_orig_h")
        .count()
        .withColumnRenamed("id_orig_h", "ip")
        .withColumnRenamed("count", "rare_port_count")
    )

    return rare


def build_features(df: DataFrame) -> DataFrame:
    """
    Main entrypoint:
    Given raw Zeek logs DataFrame -> return IP-level feature DataFrame.
    """
    conn_feats = _compute_connection_features(df)
    dns_entropy = _compute_dns_entropy(df)
    rare_ports = _compute_rare_ports(df)

    dfs = [conn_feats, dns_entropy, rare_ports]

    # Outer join everything on 'ip'
    features = reduce(lambda a, b: a.join(b, "ip", "outer"), dfs)

    # Fill nulls for any missing numeric feature
    fill_zero = {
        "avg_dns_entropy": 0.0,
        "rare_port_count": 0.0,
    }
    for col in fill_zero:
        if col in features.columns:
            features = features.na.fill({col: fill_zero[col]})

    # Ensure all feature columns exist
    for col in FEATURE_COLUMNS:
        if col not in features.columns:
            features = features.withColumn(col, F.lit(0.0))

    return features
