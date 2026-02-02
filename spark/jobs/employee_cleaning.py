from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, trim, lower, initcap, regexp_replace,
    current_date, datediff, concat_ws, split,
    when, round, to_date
)
from pyspark.sql.types import DoubleType, IntegerType

spark = SparkSession.builder \
    .appName("Employee Cleaning Final") \
    .getOrCreate()

# --------------------------------------------------
# READ CSV (NO inferSchema)
# --------------------------------------------------
df = spark.read \
    .option("header", True) \
    .option("inferSchema", False) \
    .csv("/home/jovyan/data/employees_raw.csv")

print("STEP 1 - RAW COUNT:", df.count())

# --------------------------------------------------
# BASIC CLEANING (NO DATE FILTER YET)
# --------------------------------------------------
df = df.dropDuplicates(["employee_id"])

df = df.filter(col("employee_id").isNotNull())
df = df.filter(trim(col("first_name")) != "")
df = df.filter(trim(col("last_name")) != "")
df = df.filter(col("email").isNotNull())

print("STEP 2 - AFTER BASIC FILTERS:", df.count())

# --------------------------------------------------
# SAFE DATE PARSING (EXPLICIT FORMAT)
# --------------------------------------------------
df = df.withColumn(
    "hire_date",
    to_date(col("hire_date"), "yyyy-MM-dd")
)

df = df.withColumn(
    "birth_date",
    to_date(col("birth_date"), "yyyy-MM-dd")
)

print("STEP 3 - AFTER DATE PARSING:", df.count())

# Remove future hire dates ONLY
df = df.filter(col("hire_date").isNotNull())
df = df.filter(col("hire_date") <= current_date())

print("STEP 4 - AFTER HIRE DATE FILTER:", df.count())

# --------------------------------------------------
# NAME STANDARDIZATION
# --------------------------------------------------
df = df.withColumn("first_name", initcap(trim(col("first_name"))))
df = df.withColumn("last_name", initcap(trim(col("last_name"))))

# --------------------------------------------------
# EMAIL CLEANING (SAFE)
# --------------------------------------------------
df = df.withColumn("email", lower(trim(col("email"))))
df = df.filter(col("email").contains("@"))

# --------------------------------------------------
# SALARY CLEANING
# --------------------------------------------------
df = df.withColumn(
    "salary",
    regexp_replace(col("salary"), r"[$₹,]", "")
)

df = df.withColumn(
    "salary",
    when(trim(col("salary")) == "", None)
    .otherwise(col("salary").cast(DoubleType()))
)

# --------------------------------------------------
# AGE & TENURE
# --------------------------------------------------
df = df.withColumn(
    "age",
    when(col("birth_date").isNull(), None)
    .otherwise((datediff(current_date(), col("birth_date")) / 365.25)
               .cast(IntegerType()))
)

df = df.withColumn(
    "tenure_years",
    round(datediff(current_date(), col("hire_date")) / 365.25, 1)
)

# --------------------------------------------------
# SALARY BAND
# --------------------------------------------------
df = df.withColumn(
    "salary_band",
    when(col("salary") < 50000, "Junior")
    .when((col("salary") >= 50000) & (col("salary") <= 80000), "Mid")
    .when(col("salary") > 80000, "Senior")
)

# --------------------------------------------------
# ENRICHMENT
# --------------------------------------------------
df = df.withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))
df = df.withColumn("email_domain", split(col("email"), "@").getItem(1))

df = df.withColumn(
    "department",
    initcap(lower(trim(col("department"))))
)

df = df.withColumn(
    "status",
    when(col("status").isNull() | (trim(col("status")) == ""), "Active")
    .otherwise(initcap(lower(trim(col("status")))))
)

from pyspark.sql.types import IntegerType, DoubleType

# --------------------------------------------------
# EXPLICIT TYPE CASTING (VERY IMPORTANT)
# --------------------------------------------------
df = df.withColumn("employee_id", col("employee_id").cast(IntegerType()))
df = df.withColumn("manager_id", col("manager_id").cast(IntegerType()))
df = df.withColumn("age", col("age").cast(IntegerType()))
df = df.withColumn("tenure_years", col("tenure_years").cast(DoubleType()))
df = df.withColumn("salary", col("salary").cast(DoubleType()))


# --------------------------------------------------
# FINAL SELECT
# --------------------------------------------------
final_df = df.select(
    "employee_id",
    "first_name",
    "last_name",
    "full_name",
    "email",
    "email_domain",
    "hire_date",
    "job_title",
    "department",
    "salary",
    "salary_band",
    "manager_id",
    "address",
    "city",
    "state",
    "zip_code",
    "birth_date",
    "age",
    "tenure_years",
    "status"
)

print("STEP 5 - FINAL COUNT:", final_df.count())

# --------------------------------------------------
# LOAD TO POSTGRES
# --------------------------------------------------
jdbc_url = "jdbc:postgresql://employee_postgres:5432/employee_db"

final_df.write \
    .mode("append") \
    .jdbc(
        jdbc_url,
        "employees_cleann",
        properties={
            "user": "admin",
            "password": "admin",
            "driver": "org.postgresql.Driver"
        }
    )
final_df.limit(20).coalesce(1).write.mode("overwrite").csv("/home/jovyan/data/employees_clean_sample")

print("✅ DATA LOADED SUCCESSFULLY")
spark.stop()
