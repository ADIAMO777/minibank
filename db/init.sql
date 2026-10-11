-- Runs once, the first time the Postgres volume is created.
CREATE TABLE IF NOT EXISTS accounts (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    balance    NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transactions (
    id           SERIAL PRIMARY KEY,
    from_account INT NOT NULL REFERENCES accounts(id),
    to_account   INT NOT NULL REFERENCES accounts(id),
    amount       NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO accounts (name, balance) VALUES
    ('Adaeze Okafor', 50000.00),
    ('Tunde Bakare',  25000.00);