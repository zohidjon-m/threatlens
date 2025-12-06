"""
Output utilities: write anomaly scores to MongoDB and JSON.

Requires the MongoDB Spark connector on spark-submit, e.g.:

spark-submit \
  --packages org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  main.py
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from config import OUTPUT_DIR, OUTPUT_PARTITIONS


def prepare_network_anomaly_schema(scored_df: DataFrame) -> DataFrame:
    """
    Convert scored dataframe into the EXACT schema required by
    the `network_anomalies` MongoDB collection:

    {
      ip: string,
      anomaly_score: float,
      features: {
          num_connections: ...,
          unique_dst_ips: ...,
          avg_bytes_sent: ...,
          avg_bytes_received: ...,
          dns_entropy: ...,
          rare_ports_count: ...
      },
      timestamp: float
    }
    """

    df = scored_df.select(
        F.col("ip"),
        F.col("anomaly_score"),

        F.struct(
            F.col("conn_count").alias("num_connections"),
            F.col("unique_dest_ips").alias("unique_dst_ips"),
            F.col("total_orig_bytes").alias("avg_bytes_sent"),
            F.col("total_resp_bytes").alias("avg_bytes_received"),
            F.col("avg_dns_entropy").alias("dns_entropy"),
            F.col("rare_port_count").alias("rare_ports_count")
        ).alias("features"),

        F.current_timestamp().cast("double").alias("timestamp")
    )

    return df

def write_to_mongo(df: DataFrame, mongo_uri: str) -> None:
    """
    Write the DataFrame to MongoDB using the provided URI.
    URI format example:
        mongodb://localhost:27017/threatlens.anomaly_scores
    """
    (
        df.write.format("mongodb")
        .mode("overwrite")
        .option("uri", mongo_uri)
        .save()
    )


def write_json(df: DataFrame, relative_path: str) -> None:
    """
    Write the DataFrame as JSON to OUTPUT_DIR/relative_path.
    """
    output_path = f"{OUTPUT_DIR.rstrip('/')}/{relative_path.lstrip('/')}"
    (
        df.coalesce(OUTPUT_PARTITIONS)
        .write.mode("overwrite")
        .json(output_path)
    )
