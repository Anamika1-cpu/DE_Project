import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def random_salary():
    val = random.randint(20000, 120000)
    formats = [
        f"{val}",
        f"${val}",
        f"${val:,}",
        f"{val:,}",
        f"₹{val:,}",
        ""
    ]
    return random.choice(formats)

def random_email(first, last):
    good = [
        f"{first}.{last}@company.com",
        f"{first}{last}@company.com",
        f"{first}_{last}@COMPANY.COM",
    ]
    bad = [
        f"{first}@company",
        f"{first}.{last}company.com",
        "",
        None
    ]
    return random.choice(good + bad)

def random_hire_date():
    if random.random() < 0.05:
        return (datetime.today() + timedelta(days=random.randint(10, 500))).date()
    return fake.date_between(start_date="-10y", end_date="today")

def random_birth_date():
    return fake.date_between(start_date="-60y", end_date="-18y")

def generate(n=1200):
    rows = []
    for i in range(n):
        emp_id = 1000 + i

        first = fake.first_name()
        last = fake.last_name()

        if random.random() < 0.2:
            first = first.lower()
        if random.random() < 0.2:
            last = last.upper()

        dept = random.choice(["IT", "Analytics", "HR", "Finance", "Sales", "marketing", "it"])
        status = random.choice(["Active", "active", "INACTIVE", "", None])

        row = {
            "employee_id": emp_id,
            "first_name": first if random.random() > 0.02 else "",
            "last_name": last if random.random() > 0.02 else None,
            "email": random_email(first, last),
            "hire_date": random_hire_date(),
            "job_title": random.choice(["Software Engineer", "Data Analyst", "Manager", "Data Engineer"]),
            "department": dept,
            "salary": random_salary(),
            "manager_id": random.choice([2001, 2002, 2003, None, ""]),
            "address": fake.street_address() if random.random() > 0.05 else "",
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip_code": fake.postcode(),
            "birth_date": random_birth_date(),
            "status": status
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    dup_rows = df.sample(20, random_state=42)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df

if __name__ == "__main__":
    df = generate(1200)
    df.to_csv("data/employees_raw.csv", index=False)
    print("Generated: data/employees_raw.csv", len(df))
