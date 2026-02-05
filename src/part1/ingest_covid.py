import requests

from src.common.config import (
    S3_BUCKET,
    COVID_TIMESERIES_URL,
    COVID_TIMESERIES_API
)
from src.common.s3_utils import upload_text, list_keys
from src.common.logger import get_logger

logger = get_logger("covid_timeseries_sync")

S3_PREFIX = "part1/covid_timeseries/"


def fetch_source_filenames():
    response = requests.get(COVID_TIMESERIES_API)
    response.raise_for_status()

    data = response.json()

    return [
        item["name"]
        for item in data
        if item["type"] == "file" and item["name"].endswith(".csv")
    ]


def main():
    logger.info("Fetching file list from GitHub API...")
    source_files = fetch_source_filenames()

    logger.info(f"Found {len(source_files)} source files")

    existing_keys = list_keys(S3_BUCKET, S3_PREFIX)
    existing_files = {k.split("/")[-1] for k in existing_keys}

    new_files = [f for f in source_files if f not in existing_files]

    logger.info(f"{len(new_files)} new files to upload")

    for filename in new_files:
        url = f"{COVID_TIMESERIES_URL}{filename}"
        logger.info(f"Downloading {filename}")

        r = requests.get(url)
        r.raise_for_status()

        upload_text(
            S3_BUCKET,
            f"{S3_PREFIX}{filename}",
            r.text
        )

        logger.info(f"Uploaded {filename}")

    logger.info("Sync completed")


if __name__ == "__main__":
    main()
