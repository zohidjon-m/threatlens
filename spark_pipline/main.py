"""
Entry point for Member 2 Spark job.

Steps:
1. Create SparkSession.
2. Load all Zeek logs.
3. Build IP-level features.
4. Train KMeans anomaly model and score IPs.
5. Write scores to MongoDB and JSON.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, isnan
from config import MONGO_URI
from load_logs import load_all_logs
from feature_engineering import build_features
from train_anomaly import train_kmeans_and_score
from write_outputs import write_to_mongo, write_json, prepare_network_anomaly_schema

import sys
import os
def create_spark() -> SparkSession:
    """
    Create SparkSession.
    """
    spark = (
        SparkSession.builder
        .appName("ThreatLens-AnomalyPipeline")
        .config(
            "spark.jars.packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0"
        )
        .config("spark.mongodb.write.connection.uri", MONGO_URI)
        .config("spark.mongodb.read.connection.uri", MONGO_URI)
        .getOrCreate()
    )
    return spark


def main():

    spark = create_spark()

    # 1. Load logs
    raw_logs = load_all_logs(spark)

    # 2. Build IP-level features
    feature_df = build_features(raw_logs)

    # 3. Train and score anomaly model
    scored_df = train_kmeans_and_score(feature_df)

    # 4. Convert to schema-compliant format
    anomaly_df = prepare_network_anomaly_schema(scored_df)

    # 5. Save to MongoDB
    write_to_mongo(anomaly_df, MONGO_URI)

    # 6. Save JSON for dashboard
    write_json(anomaly_df, "network_anomalies_json")

    spark.stop()


if __name__ == "__main__":
    main()
