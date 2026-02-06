import requests
import json

from pyspark.sql import SparkSession

from src.common.config import S3_BUCKET, COUNTRIES_API_URL
from src.common.logger import get_logger

logger = get_logger("countries_ingestion")

S3_PATH = f"s3a://{S3_BUCKET}/part2/countries_parquet/"


def main():
    spark = (
        SparkSession.builder
        .appName("countries-ingestion")
        .getOrCreate()
    )

    logger.info("Fetching countries dataset")

    response = requests.get(COUNTRIES_API_URL)
    response.raise_for_status()
    countries = response.json()  # list of dicts

    # Convert each country object to JSON string
    rdd = spark.sparkContext.parallelize(
        [json.dumps(c) for c in countries]
    )

    raw_df = spark.read.json(rdd)

    curated = (
        raw_df
        .selectExpr(
            "name.common as country",
            "cca3 as country_code",
            "population",
            "region"
        )
        .filter("population is not null")
    )

    (
        curated
        .repartition("region")
        .write
        .mode("overwrite")
        .partitionBy("region")
        .parquet(S3_PATH)
    )

    logger.info("Countries written to parquet successfully")

    spark.stop()


if __name__ == "__main__":
    main()
