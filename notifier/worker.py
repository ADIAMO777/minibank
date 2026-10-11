"""Background worker: waits for transactions on a Redis queue and sends alerts.

It has no HTTP port. You only see it working through `docker logs`.
"""
import json
import os
import time

import redis

r = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
channel = os.environ.get("NOTIFY_CHANNEL", "SMS")

print(f"notifier started, sending via {channel}, waiting for jobs...", flush=True)
while True:
    try:
        _, raw = r.blpop("notifications")
        tx = json.loads(raw)
        print(
            f"[{channel}] Debit alert: account {tx['from_account']} sent "
            f"NGN {tx['amount']:,.2f} to account {tx['to_account']} (tx #{tx['id']})",
            flush=True,
        )
    except redis.exceptions.ConnectionError as e:
        print(f"redis unavailable ({e}), retrying in 3s", flush=True)
        time.sleep(3)