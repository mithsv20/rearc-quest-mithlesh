from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum as spark_sum,
    round as spark_round,
    broadcast
)

from src.common.config import S3_BUCKET
from src.common.logger import get_logger

logger = get_logger("spark_part3")

COVID_PATH = f"s3a://{S3_BUCKET}/part1/covid_timeseries/"
COUNTRIES_PATH = f"s3a://{S3_BUCKET}/part2/countries_parquet/"
OUTPUT_PATH = f"s3a://{S3_BUCKET}/part3/outputs/infection_rate_report/"


def create_spark():
    return (
        SparkSession.builder
        .appName("infection-rate-analytics")
        .getOrCreate()
    )


def main():
    spark = create_spark()

    # -------- Load COVID (Column Pruning) --------
    covid_df = spark.read.option("header", True).csv(
        COVID_PATH + "time_series_covid19_confirmed_global.csv"
    )

    latest_col = covid_df.columns[-1]

    covid_agg = (
        covid_df
        .select("Country/Region", latest_col)
        .groupBy("Country/Region")
        .agg(
            spark_sum(col(latest_col).cast("long"))
            .alias("total_cases")
        )
        .filter(col("total_cases") > 0)
        .withColumnRenamed("Country/Region", "country")
    )

    # -------- Load Countries (Parquet) --------
    countries_df = (
        spark.read.parquet(COUNTRIES_PATH)
        .select("country", "population", "region")
    )

    # -------- Join (Broadcast small table) --------
    joined = (
        covid_agg
        .join(broadcast(countries_df), "country")
    )

    # -------- Metrics --------
    final_df = (
        joined
        .withColumn(
            "infection_rate_percentage",
            spark_round(
                (col("total_cases") / col("population")) * 100,
                2
            )
        )
        .select(
            "country",
            "region",
            "population",
            "total_cases",
            "infection_rate_percentage"
        )
        .orderBy(col("infection_rate_percentage").desc())
        .limit(20)
    )

    # -------- Write Output --------
    (
        final_df
        .coalesce(1)
        .write
        .mode("overwrite")
        .csv(OUTPUT_PATH, header=True)
    )

    logger.info("Optimized infection rate report generated")

    spark.stop()


if __name__ == "__main__":
    main()
