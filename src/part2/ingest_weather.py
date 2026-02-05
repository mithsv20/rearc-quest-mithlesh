import json
import requests

from common.config import S3_BUCKET, WEATHER_API_URL, CITIES
from common.s3_utils import upload_text, list_keys
from common.logger import get_logger

logger = get_logger("weather_ingestion")

S3_PREFIX = "part2/weather/"


def main():
    existing_keys = list_keys(S3_BUCKET, S3_PREFIX)
    existing_files = {k.split("/")[-1] for k in existing_keys}

    for city, coords in CITIES.items():
        filename = f"{city}.json"

        if filename in existing_files:
            logger.info(f"{filename} already exists. Skipping.")
            continue

        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current_weather": True
        }

        logger.info(f"Fetching weather for {city}")
        r = requests.get(WEATHER_API_URL, params=params)
        r.raise_for_status()

        upload_text(
            S3_BUCKET,
            f"{S3_PREFIX}{filename}",
            json.dumps(r.json())
        )

        logger.info(f"Uploaded {filename}")

    logger.info("Weather ingestion complete")


if __name__ == "__main__":
    main()
