import json
import requests

from src.common.config import S3_BUCKET, COUNTRIES_API_URL
from src.common.s3_utils import upload_text, list_keys
from src.common.logger import get_logger

logger = get_logger("countries_ingestion")

S3_PREFIX = "part2/countries/"


def run():
    logger.info("Fetching countries dataset")
    r = requests.get(COUNTRIES_API_URL)
    r.raise_for_status()

    countries = r.json()

    existing_keys = list_keys(S3_BUCKET, S3_PREFIX)
    existing_files = {k.split("/")[-1] for k in existing_keys}

    for country in countries:
        code = country.get("cca3")
        if not code:
            continue

        filename = f"{code}.json"

        if filename in existing_files:
            continue

        upload_text(
            S3_BUCKET,
            f"{S3_PREFIX}{filename}",
            json.dumps(country)
        )

        logger.info(f"Uploaded {filename}")

    logger.info("Countries ingestion complete")


if __name__ == "__main__":
    run()
