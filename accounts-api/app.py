import os
from decimal import Decimal

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)


def db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def row(r):
    return {**r, "balance": float(r["balance"]), "created_at": r["created_at"].isoformat()}


@app.get("/health")
def health():
    return {"status": "ok", "service": "accounts-api"}


@app.get("/accounts")
def list_accounts():
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM accounts ORDER BY id")
        return jsonify([row(r) for r in cur.fetchall()])


@app.post("/accounts")
def create_account():
    body = request.get_json(force=True)
    name = (body.get("name") or "").strip()
    balance = Decimal(str(body.get("balance", 0)))
    if not name or balance < 0:
        return {"error": "name is required and balance must be >= 0"}, 400
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s) RETURNING *", (name, balance))
        return row(cur.fetchone()), 201


@app.post("/transfer")
def transfer():
    """Internal endpoint called by transactions-api. Moves money atomically."""
    body = request.get_json(force=True)
    src, dst = int(body["from"]), int(body["to"])
    amount = Decimal(str(body["amount"]))
    if src == dst or amount <= 0:
        return {"error": "invalid transfer"}, 400
    with db() as conn, conn.cursor() as cur:
        # Lock both rows in a fixed order to avoid deadlocks.
        cur.execute("SELECT id, balance FROM accounts WHERE id IN (%s, %s) ORDER BY id FOR UPDATE", (src, dst))
        balances = dict(cur.fetchall())
        if len(balances) != 2:
            return {"error": "account not found"}, 404
        if balances[src] < amount:
            return {"error": "insufficient funds"}, 409
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, src))
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, dst))
    return {"status": "ok"}