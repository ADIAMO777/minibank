const express = require("express");
const { Pool } = require("pg");
const { createClient } = require("redis");

const PORT = process.env.PORT || 3000;
const ACCOUNTS_URL = process.env.ACCOUNTS_API_URL; // e.g. http://accounts-api:5000

const pool = new Pool({
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});
const redis = createClient({ url: process.env.REDIS_URL });
redis.on("error", (err) => console.error("redis error:", err.message));

const app = express();
app.use(express.json());

// Express 4 doesn't catch errors from async handlers on its own, so wrap them.
const wrap = (fn) => (req, res) =>
  fn(req, res).catch((err) => {
    console.error(err);
    res.status(500).json({ error: err.message });
  });

app.get("/health", (_req, res) => res.json({ status: "ok", service: "transactions-api" }));

app.get("/transactions", wrap(async (_req, res) => {
  const { rows } = await pool.query("SELECT * FROM transactions ORDER BY id DESC LIMIT 50");
  res.json(rows.map((r) => ({ ...r, amount: Number(r.amount) })));
}));

app.post("/transactions", wrap(async (req, res) => {
  const { from, to, amount } = req.body;

  // 1. Ask accounts-api to move the money (container-to-container call by service name).
  const transfer = await fetch(`${ACCOUNTS_URL}/transfer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from, to, amount }),
  });
  if (!transfer.ok) {
    return res.status(transfer.status).json(await transfer.json());
  }

  // 2. Record the transaction.
  const { rows } = await pool.query(
    "INSERT INTO transactions (from_account, to_account, amount) VALUES ($1, $2, $3) RETURNING *",
    [from, to, amount]
  );
  const tx = { ...rows[0], amount: Number(rows[0].amount) };

  // 3. Queue a notification for the notifier worker.
  await redis.lPush("notifications", JSON.stringify(tx));

  res.status(201).json(tx);
}));

redis.connect().then(() => {
  app.listen(PORT, () => console.log(`transactions-api listening on :${PORT}`));
});