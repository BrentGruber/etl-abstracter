CREATE TABLE IF NOT EXISTS customers_replica (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
