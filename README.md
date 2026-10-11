# 🏦 MiniBank: Docker Lab

Welcome! This is a small banking app split into **4 separate apps**, each in its own Docker container.
Your job: get it all running on your machine and understand what each piece does.

Don't worry if it feels like a lot. Go step by step, run each command, and read what it prints.

---

## 🧩 What's inside?

| App | What it does | Built with |
|---|---|---|
| **frontend** | The website you open in your browser | HTML + Nginx |
| **accounts-api** | Creates accounts and moves money | Python |
| **transactions-api** | Records every transfer | Node.js |
| **notifier** | "Sends" an SMS alert after each transfer (prints it in the logs) | Python |
| **db** | Stores all the data | PostgreSQL (ready-made image) |
| **redis** | A queue that passes messages to the notifier | Redis (ready-made image) |

How a transfer flows:

```
You (browser) → frontend → transactions-api → accounts-api → db
                                  ↓
                                redis → notifier → "SMS sent!"
```

---

## ✅ Step 0: What you need first

1. **Docker Desktop** installed and **running** (the whale icon in your taskbar should be steady, not animating).
   Download: https://www.docker.com/products/docker-desktop/
2. **Git** installed. Download: https://git-scm.com/downloads

Check that both work. Open PowerShell (or Terminal on Mac/Linux) and run:

```
docker --version
git --version
docker run --rm hello-world
```

If you see **"Hello from Docker!"**, you're good to go. 🎉

---

## 📥 Step 1: Download the project

```
git clone https://github.com/YOUR_USER/mini-bank.git
cd mini-bank
```

`git clone` copies the project to your computer. `cd` moves you into the folder.
**Run every command after this from inside the `mini-bank` folder.**

---

## 🔐 Step 2: Create your settings file

The apps need a database username and password. We keep these in a file called `.env`.
There's a template, so just copy it:

```
cp .env.example .env
```

(Optional) Open `.env` and change `POSTGRES_PASSWORD` to something of your own.

> 💡 `.env` is never uploaded to GitHub. Passwords don't belong in a repo!

---

## 🔨 Step 3: Build the images (one at a time)

An **image** is like a recipe plus all its ingredients, packed in a box.
A **container** is that recipe actually cooking (a running copy of the image).

Each app has its own `Dockerfile`, which is the recipe. Let's build all 4:

```
docker build -t minibank/accounts-api:1.0 ./accounts-api
docker build -t minibank/transactions-api:1.0 ./transactions-api
docker build -t minibank/notifier:1.0 ./notifier
docker build -t minibank/frontend:1.0 ./frontend
```

What that means:
- `docker build`: make an image
- `-t minibank/accounts-api:1.0`: give it a name (`minibank/accounts-api`) and a version (`1.0`)
- `./accounts-api`: the folder that has the Dockerfile

Now see your images:

```
docker images
```

You should see all 4 `minibank/...` images listed. ✔

### 🧪 Try this: see layer caching
1. Open `accounts-api/app.py` and add a comment at the top, e.g. `# hello`
2. Build the accounts-api image again (same command as above)
3. Notice the `pip install` step says **CACHED** and the build is super fast. Docker reuses layers that didn't change!

You can also peek at the layers inside an image:

```
docker history minibank/accounts-api:1.0
```

---

## 🚀 Step 4: Start everything

Instead of starting 6 containers by hand, we use **Docker Compose**.
It reads `docker-compose.yml` and starts everything in the right order:

```
docker compose up -d
```

- `up`: start everything
- `-d`: run in the background so you get your terminal back

Check that everything is running:

```
docker compose ps
```

All 6 services should show **running** (db and redis also show **healthy**).

---

## 🌍 Step 5: Use the app

Open your browser and go to 👉 **http://localhost:8080**

Try this:
1. You'll see 2 accounts already there (Adaeze and Tunde)
2. Open a new account for yourself
3. Transfer money: **From 1, To 2, Amount 5000**
4. Watch the balances change and the transaction appear below

Now see the SMS alert the notifier "sent":

```
docker compose logs notifier
```

You should see something like:
`[SMS] Debit alert: account 1 sent NGN 5,000.00 to account 2 (tx #1)` 📱

---

## 🔍 Step 6: Look inside (debugging skills)

These are the commands you'll use **every day** as a DevOps engineer:

| Command | What it does |
|---|---|
| `docker compose ps` | List running containers |
| `docker compose logs accounts-api` | Show one app's logs |
| `docker compose logs -f notifier` | Follow logs live (press `Ctrl + C` to stop watching) |
| `docker compose exec accounts-api sh` | Open a shell **inside** a container (type `exit` to leave) |
| `docker inspect minibank-db-1` | Show everything about a container (IP, env vars, volumes) |
| `docker stats` | Live CPU and memory use (`Ctrl + C` to exit) |

Look inside the database directly:

```
docker compose exec db psql -U minibank -d minibank -c "SELECT * FROM accounts;"
```

### 🧪 Try this: network isolation
The frontend should **not** be able to reach the database (that's a security feature):

```
docker compose exec frontend ping -c1 db
```

It fails with "bad address". 👍 Now try it from accounts-api, which is allowed:

```
docker compose exec accounts-api python -c "import socket; print(socket.gethostbyname('db'))"
```

It prints an IP address. Why the difference? Look at the `networks:` section in `docker-compose.yml`.

---

## 💾 Step 7: Stop and start (and where the data lives)

**Stop everything but keep your data:**
```
docker compose down
```
Run `docker compose up -d` again. Your accounts and transfers are **still there**,
because the data is saved in a **volume** (a storage area that outlives containers).

**Stop everything AND delete all the data:**
```
docker compose down -v
```
The `-v` deletes the volume. Next time you start, you're back to just Adaeze and Tunde.

---

## 🔁 Step 8: After you change code

If you edit any app's code, rebuild and restart in one go:

```
docker compose up -d --build
```

---

## 🆘 Something's not working?

| Problem | Fix |
|---|---|
| `error during connect` / `cannot find the file specified` | Docker Desktop isn't running. Open it and wait until it's ready. |
| `port is already allocated` on 8080 | Something else is using port 8080. Open `.env`, change `FRONTEND_PORT=8081`, then use http://localhost:8081 |
| Website loads but shows no accounts | Run `docker compose logs accounts-api` and read the error. Usually the database isn't ready yet; wait 10 seconds and refresh. |
| A container keeps restarting or shows `Exited` | Run `docker compose logs <name>`. The answer is almost always in the logs. |
| I changed the password in `.env` and now the database fails | The old password is saved in the volume. Run `docker compose down -v`, then `docker compose up -d`. |
| `docker: command not found` | Docker isn't installed, or you need to restart your terminal after installing. |

---

## 🧠 Check yourself

Can you answer these? (We'll discuss them in class.)

1. What's the difference between an **image** and a **container**?
2. Why does each Dockerfile copy `requirements.txt` / `package.json` **before** the code?
3. How does `transactions-api` find `accounts-api` without knowing its IP address?
4. Why can't the frontend reach the database? Why is that a good thing?
5. What's the difference between `docker compose down` and `docker compose down -v`?
6. Every Dockerfile has a `USER` line, so nothing runs as root. Why might that matter? *(Hint: OpenShift 😉)*

---

## ⏭️ What's next?

1. **Push your images to Docker Hub** (we'll do this together)
2. **Kubernetes**: run these same 4 images on a cluster
3. **OpenShift**: the enterprise version of Kubernetes

Have fun, break things, and read the logs! 🚀