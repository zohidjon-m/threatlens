"""
Train a KMeans anomaly model on IP-level features and score IPs.

We treat anomaly_score as the distance to the closest cluster center.
Higher distance -> more anomalous.
"""

from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from config import FEATURE_COLUMNS, KMEANS_K, KMEANS_MAX_ITER, KMEANS_SEED


def train_kmeans_and_score(features_df: DataFrame) -> DataFrame:
    """
    Input:
        features_df: DataFrame with columns:
            ip, FEATURE_COLUMNS..., label

    Output:
        DataFrame with columns:
            ip,
            FEATURE_COLUMNS...,
            prediction (cluster id),
            anomaly_score (distance to cluster center),
            label
    """
    # Assemble features into a vector
    assembler = VectorAssembler(
        inputCols=FEATURE_COLUMNS,
        outputCol="features",
    )

    df_vec = assembler.transform(features_df)

    # Scale features (IMPORTANT FIX)
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features",
        withStd=True,
        withMean=True
    )
    scaler_model = scaler.fit(df_vec)
    df_scaled = scaler_model.transform(df_vec)

    # Train KMeans
    km = KMeans(
        featuresCol="scaled_features",
        predictionCol="prediction",
        k=KMEANS_K,
        maxIter=KMEANS_MAX_ITER,
        seed=KMEANS_SEED,
    )

    model = km.fit(df_scaled)

    # Get raw prediction with distances
    # transform() does NOT give distances by default; we compute manually
    centers = model.clusterCenters()

    # add prediction
    pred_df = model.transform(df_scaled)

    # UDF to compute distance to center
    from pyspark.sql.types import DoubleType
    from pyspark.ml.linalg import DenseVector

    def dist_to_center(pred, feat):
        if pred is None or feat is None:
            return 0.0
        center = centers[int(pred)]
        if isinstance(feat, DenseVector):
            v = feat
        else:
            v = DenseVector(feat)
        return float(sum((v[i] - center[i]) ** 2 for i in range(len(center))) ** 0.5)

    from pyspark.sql.functions import udf

    dist_udf = udf(dist_to_center, DoubleType())

    scored = pred_df.withColumn(
        "anomaly_score",
        dist_udf(F.col("prediction"), F.col("scaled_features")),
    )

    # Severity categorization based on anomaly_score
    def categorize(score):
        if score > 1:
            return "critical"
        elif score > 0.2:
            return "high"
        elif score > 0.05:
            return "medium"
        elif score > 0.015:
            return "low"
        else:
            return "normal"

    categorize_udf = F.udf(categorize, StringType())

    scored = scored.withColumn("severity", categorize_udf(F.col("anomaly_score")))

    return scored
