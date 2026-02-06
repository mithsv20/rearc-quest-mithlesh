
---

# Rearc Quest – Data Engineering Assignment

## Overview

This project implements an end-to-end, serverless data pipeline that ingests public COVID-19 and country metadata, stores the data in Amazon S3, and produces analytical reports showing countries with the highest COVID-19 infection rates.

The solution demonstrates:

- Modular Python and PySpark ingestion
- Serverless orchestration using AWS Lambda, SQS, and EventBridge
- Scalable analytics using Spark (locally) and lightweight Python analytics (Lambda)
- Event-driven architecture and operational monitoring

---

## Architecture

Daily Schedule (EventBridge)  
→ Lambda A (COVID + Countries ingestion)  
→ S3 (raw datasets)  
→ S3 Event Notification  
→ SQS Queue  
→ Lambda B (analytics & reporting)

---

## Project Structure

```

src/
├── common/
│     ├── config.py
│     ├── logger.py
│     └── s3_utils.py
│
├── part1/
│     └── ingest_covid.py
│
├── part2/
│     ├── ingest_countries_python.py
│     └── ingest_countries_spark.py
│
├── part3/
│     ├── analytics_spark.py
│     ├── analytics_pandas.py
│     └── analytics_lambda.py
│
lambda/
├── rearc-ingest-covid-and-countries/
│     └── app.py
└── rearc-generate-infection-report/
      └── app.py

```

---

## Local Setup

### Prerequisites

- Python 3.11
- pip
- AWS CLI configured
- Java 11+ (for Spark)
- PySpark (for Spark-based analytics)

### Install Dependencies

```bash
pip install -r requirements.txt
````

---

## Run Locally

### Part 1 – Ingest COVID Data

```bash
python -m src.part1.ingest_covid
```

### Part 2 – Ingest Countries (Python)

```bash
python -m src.part2.ingest_countries_python
```

### Part 3 – Analytics (Pandas)

```bash
python -m src.part3.analytics_pandas
```

### Part 3 – Analytics (Spark)

```bash
python -m src.part3.analytics_spark
```

---

## AWS Deployment (Console)

### Lambda A – Ingestion

* Runtime: Python 3.11
* Handler:

```
lambda.rearc-ingest-covid-and-countries.app.lambda_handler
```

* Layer: requests

### Lambda B – Analytics

* Runtime: Python 3.11
* Handler:

```
lambda.rearc-generate-infection-report.app.lambda_handler
```

* Layer: requests

---

## Event Wiring

1. EventBridge rule triggers Lambda A daily
2. S3 bucket sends ObjectCreated events (part2/countries/*.json) to SQS
3. SQS triggers Lambda B

---

## Monitoring

* CloudWatch Alarm on Lambda B Errors
* SNS Email notifications for failures

---

## Output

Lambda B logs top 20 countries by infection rate:

```
country | region | population | total_cases | infection_rate_pct
```

Logs are available in CloudWatch.

---

## Notes

* Spark implementation is included for scalable analytics.
* Pure Python implementation is used in Lambda for reliability and minimal dependencies.
* No hard-coded filenames are used; the pipeline dynamically discovers data in S3.

---

## Author
Mithlesh Vishwakarma
