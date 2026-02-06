
---

# 📘 Rearc Quest – Data Engineering Assignment

This repository contains my solution for the Rearc Data Engineering Quest.
The solution implements an end-to-end data pipeline that:

* Ingests public COVID-19 time-series data
* Ingests country metadata from a REST API
* Stores curated datasets in Amazon S3
* Computes analytics using Apache Spark
* Produces a business-meaningful infection-rate report

The solution emphasizes scalability, idempotency, clean architecture, and production-style practices.

---

## 🏗 Architecture Overview

**Part 1**
Ingest COVID time-series CSV files from public GitHub → S3

**Part 2**
Ingest country metadata (population, region) from REST Countries API → curated Parquet in S3 (partitioned by region)

**Part 3**
Spark analytics (Dockerized):

* Aggregate latest confirmed cases by country
* Join with population dataset
* Compute infection rate (%)
* Output Top 20 countries by infection rate

---

## 📂 Project Structure

```
rearc-quest-mithlesh/
│
├── src/
│   ├── common/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── s3_utils.py
│   │
│   ├── part1/
│   │   └── ingest_covid.py
│   │
│   ├── part2/
│   │   └── ingest_countries.py
│   │
│   └── part3/
│       └── analytics.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

* Python 3.9+
* AWS Account (Free Tier)
* AWS CLI configured
* Docker Desktop

Verify:

```bash
aws --version
docker --version
python --version
```

---

## 🔐 AWS Configuration

Configure credentials:

```bash
aws configure
```

Confirm:

```bash
aws s3 ls
```

---

## 🪣 S3 Bucket

Create a bucket (example):

```bash
aws s3 mb s3://quest-mithlesh
```

Update bucket name in:

```
src/common/config.py
```

---

## 🐍 Local Python Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

# ▶ Part 1 – COVID Data Ingestion

Uploads latest COVID time-series files to S3 and keeps them in sync.

```bash
python -m src.part1.ingest_covid
```

Verify:

```bash
aws s3 ls s3://quest-mithlesh/part1/covid_timeseries/
```

---

# ▶ Part 2 – Countries Metadata Ingestion (Parquet)

Runs inside Spark container.

Build image:

```bash
docker build -t rearc-spark .
```

Run ingestion:

```bash
docker run -it \
-v $(pwd):/app \
-v ~/.aws:/root/.aws \
-e PYTHONPATH=/app \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
rearc-spark \
/opt/spark/bin/spark-submit \
--conf spark.hadoop.fs.s3a.access.key=$AWS_ACCESS_KEY_ID \
--conf spark.hadoop.fs.s3a.secret.key=$AWS_SECRET_ACCESS_KEY \
/app/src/part2/ingest_countries.py
```

Verify:

```bash
aws s3 ls s3://quest-mithlesh/part2/countries_parquet/
```

You should see partitioned folders:

```
region=Asia/
region=Europe/
region=Africa/
...
```

---

# ▶ Part 3 – Spark Analytics (Docker)

Produces Top 20 countries by infection rate.

```bash
docker run -it \
-v $(pwd):/app \
-v ~/.aws:/root/.aws \
-e PYTHONPATH=/app \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
rearc-spark \
/opt/spark/bin/spark-submit \
--conf spark.hadoop.fs.s3a.access.key=$AWS_ACCESS_KEY_ID \
--conf spark.hadoop.fs.s3a.secret.key=$AWS_SECRET_ACCESS_KEY \
/app/src/part3/analytics_lambda.py
```

Verify output:

```bash
aws s3 ls s3://quest-mithlesh/part3/outputs/infection_rate_report/
```

---

## 📊 Output Schema

```
country
region
population
total_cases
infection_rate_pct
```

---

## 💡 Design Choices

* Parquet for analytical storage
* Partitioning by region
* Broadcast join for small dimension table
* Column pruning & early filtering
* Dockerized Spark for reproducible execution
* No hard-coded filenames
* Idempotent ingestion

---

## 🔁 Re-running Pipeline

The pipeline is safe to re-run:

* Part 1 syncs only new files
* Part 2 overwrites curated Parquet
* Part 3 overwrites final report

---

## 🚀 Future Enhancements

* Orchestration with Airflow / Step Functions
* CI pipeline for linting & tests
* Data quality checks
* IAM role-based auth

---

If you want, next we can move to **Part 4 (Automation / IaC)** and add a lightweight orchestration layer.
