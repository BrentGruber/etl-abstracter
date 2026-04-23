CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO customers (first_name, last_name, email, status)
VALUES
    ('Brent', 'Gruber', 'brent@example.com', 'active'),
    ('Ada', 'Lovelace', 'ada@example.com', 'active'),
    ('Grace', 'Hopper', 'grace@example.com', 'active')
ON CONFLICT (email) DO NOTHING;
