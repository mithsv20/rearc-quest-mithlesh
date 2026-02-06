import boto3
import csv
import json
import logging
from io import StringIO

from src.common.config import S3_BUCKET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lambda_analytics")

COVID_PREFIX = "part1/covid_timeseries/"
COUNTRIES_PREFIX = "part2/countries/"


def run():
    s3 = boto3.client("s3")

    # -----------------------
    # Load confirmed cases
    # -----------------------

    objs = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=COVID_PREFIX
    )

    covid_key = [
        o["Key"]
        for o in objs.get("Contents", [])
        if "time_series_covid19_confirmed_global.csv" in o["Key"]
    ][0]

    csv_obj = s3.get_object(Bucket=S3_BUCKET, Key=covid_key)
    csv_text = csv_obj["Body"].read().decode("utf-8")

    reader = csv.DictReader(StringIO(csv_text))

    country_cases = {}

    for row in reader:
        country = row["Country/Region"]
        latest_val = list(row.values())[-1]
        country_cases[country] = country_cases.get(country, 0) + int(float(latest_val))

    # -----------------------
    # Load countries
    # -----------------------

    objs = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=COUNTRIES_PREFIX
    )

    countries = []

    for obj in objs.get("Contents", []):
        if not obj["Key"].endswith(".json"):
            continue

        body = s3.get_object(
            Bucket=S3_BUCKET,
            Key=obj["Key"]
        )["Body"].read().decode("utf-8")

        c = json.loads(body)

        countries.append({
            "country": c["name"]["common"],
            "population": c.get("population"),
            "region": c.get("region")
        })

    # -----------------------
    # Join + Compute
    # -----------------------

    results = []

    for c in countries:
        name = c["country"]
        pop = c["population"]

        if name not in country_cases or not pop:
            continue

        total = country_cases[name]
        rate = round((total / pop) * 100, 2)

        results.append({
            "country": name,
            "region": c["region"],
            "population": pop,
            "total_cases": total,
            "infection_rate_pct": rate
        })

    top20 = sorted(
        results,
        key=lambda x: x["infection_rate_pct"],
        reverse=True
    )[:20]

    for r in top20:
        logger.info(r)

    return top20

if __name__ == '__main__':
    run()