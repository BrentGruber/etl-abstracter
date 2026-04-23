import os
import random
import string
import time
from datetime import datetime, timezone

import psycopg2

INTERVAL = int(os.environ.get("UPDATE_INTERVAL_SECONDS", "15"))

FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Ivy", "Maya"]
LAST_NAMES = ["Smith", "Johnson", "Lee", "Brown", "Wilson", "Moore", "Clark", "Davis"]
STATUSES = ["active", "inactive", "trial"]


def random_email(first_name: str, last_name: str) -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{first_name.lower()}.{last_name.lower()}.{suffix}@example.com"


def main() -> None:
    while True:
        try:
            conn = psycopg2.connect()
            conn.autocommit = True
            with conn.cursor() as cur:
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                email = random_email(first_name, last_name)
                status = random.choice(STATUSES)
                cur.execute(
                    """
                    INSERT INTO customers (first_name, last_name, email, status, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (first_name, last_name, email, status, datetime.now(timezone.utc)),
                )
            conn.close()
            print(f"inserted synthetic customer at {datetime.now(timezone.utc).isoformat()}", flush=True)
        except Exception as exc:
            print(f"generator error: {exc}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
