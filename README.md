Employee Data Pipeline – Spark & PostgreSQL (Dockerized)
📌 Project Overview

This project implements an end-to-end data engineering pipeline using Apache Spark and PostgreSQL, fully containerized with Docker.

The pipeline:

Generates raw employee data with intentional data quality issues

Cleans, validates, and transforms the data using Apache Spark

Loads the cleaned data into a PostgreSQL table

Demonstrates practical data engineering skills including data quality enforcement, transformations, and Docker orchestration

This project was developed as part of a Data Engineering Assignment focused on real-world data processing scenarios.

🛠 Tech Stack

Apache Spark (PySpark) – data cleaning & transformations

PostgreSQL – relational data storage

Docker & Docker Compose – containerized environment

Python – data generation & Spark job

JDBC – Spark → PostgreSQL connectivity

🏗 Architecture
employees_raw.csv
        ↓
Apache Spark (Data Cleaning & Transformation)
        ↓
employees_clean (PostgreSQL)


All services (Spark & PostgreSQL) run inside Docker containers.

📂 Project Structure
employee-pipeline/ <br />
│ <br />
├── data/ <br />
│   ├── employees_raw.csv <br />
│   └── employees_clean_sample.csv <br />
│ <br />
├── postgres/ <br />
│   └── init.sql <br />
│ <br />
├── scripts/ <br />
│   └── generate_data.py <br />
│ <br />
├── spark/ <br />
│   ├── jobs/ <br />
│   │   └── employee_cleaning.py <br />
│   └── jars/ <br />
│       └── postgresql.jar <br />
│ <br />
├── docker-compose.yml <br />
└── README.md <br />

🧪 Sample Data Generation

The raw dataset is generated using Python + Faker.

Characteristics of the raw data:

1000+ employee records

Duplicate employee_id values

Missing critical fields

Invalid email formats

Future hire dates (logical errors)

Salary values with currency symbols and commas

Mixed-case categorical values

Null values in non-critical columns

This simulates real-world dirty data.

🔍 Data Cleaning & Transformations (Spark)
Data Quality Checks

Removed duplicate records based on employee_id

Dropped records with missing mandatory fields

Filtered invalid email formats

Removed future or invalid hire dates

Handled unparseable numeric values

Transformations

Standardized names to Proper Case

Converted emails to lowercase

Cleaned salary values and converted to numeric

Parsed dates explicitly to avoid schema inference issues

Calculated:

Employee age

Tenure (years of service)

Created salary bands:

Junior: < 50k

Mid: 50k–80k

Senior: > 80k

Data Enrichment

Added full_name

Extracted email_domain

Normalized department and status fields

🗄 Database Design
Table: employees_clean
CREATE TABLE employees_clean (
    employee_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    email_domain VARCHAR(50),
    hire_date DATE NOT NULL,
    job_title VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    salary_band VARCHAR(20),
    manager_id INTEGER,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    birth_date DATE,
    age INTEGER,
    tenure_years DECIMAL(3,1),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

📊 Row Count Explanation (IMPORTANT)
Stage	Record Count
Raw input data	~1200
Final cleaned data	637
Why rows were reduced:

Duplicate employee IDs

Missing mandatory fields

Invalid email formats

Future or invalid hire dates

Data type parsing failures

This reduction is expected and intentional, demonstrating effective data quality enforcement.

🚀 How to Run the Pipeline
1️⃣ Generate Raw Data (Local Machine)
py scripts/generate_data.py

2️⃣ Start Docker Containers
docker compose up -d


Ensure both containers are running:

spark_container

employee_postgres

3️⃣ Run Spark Job
docker exec -it spark_container spark-submit \
  --jars /home/jovyan/jars/postgresql.jar \
  /home/jovyan/jobs/employee_cleaning.py

4️⃣ Verify Data in PostgreSQL
docker exec -it employee_postgres psql -U admin -d employee_db \
  -c "SELECT COUNT(*) FROM employees_clean;"

🧯 Error Handling & Logging

Spark job logs record counts at each major stage

Explicit schema casting is applied before JDBC writes

Date parsing is handled safely using defined formats

Common Spark–JDBC errors were handled and resolved during development

🧠 Key Learnings

Importance of explicit schema handling in Spark

Silent failures in date parsing can cause data loss

JDBC writes require strict data type alignment

Dockerized Spark environments vary significantly across images

Real-world pipelines often discard large portions of bad data
