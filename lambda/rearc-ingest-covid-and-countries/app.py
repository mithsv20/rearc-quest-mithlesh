from src.part1.ingest_covid import run as run_covid
from src.part2.ingest_countries import run as run_countries


def lambda_handler(event, context):
    run_covid()
    run_countries()
    return {"status": "covid and countries ingestion completed"}
