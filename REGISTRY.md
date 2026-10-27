# 📦 MiniBank: Pushing Your Images to Amazon ECR

Welcome back! 👋 In Phase 1 you built 4 MiniBank images and ran them on your own laptop.
That's great, but there's a problem: **those images only exist on YOUR machine.**

Kubernetes (Phase 2) and OpenShift (Phase 3) run on *other* machines, and they need to
download your images from somewhere. That "somewhere" is a **container registry**.

We'll use **Amazon ECR (Elastic Container Registry)**, the private registry in our class AWS account.

By the end of this guide you will:
- ✅ Have the AWS CLI installed and logged in as **you**
- ✅ Have 4 private repositories in ECR with your name on them
- ✅ Have pushed all 4 MiniBank images (version `1.0`) to the cloud
- ✅ Have checked your images for security vulnerabilities

⏱️ Time needed: about 30–45 minutes

---

## 🧠 First, a quick picture

```
Your laptop                              AWS (ECR)
──────────────────────────────           ──────────────────────────────────────
minibank/frontend:1.0          ─push─▶   ada/minibank-frontend:1.0
minibank/accounts-api:1.0      ─push─▶   ada/minibank-accounts-api:1.0
minibank/transactions-api:1.0  ─push─▶   ada/minibank-transactions-api:1.0
minibank/notifier:1.0          ─push─▶   ada/minibank-notifier:1.0
                                                 ▲
                                                 │ pull
                                          Kubernetes / OpenShift (later!)
```

A full image name in ECR looks long and scary, but it's just 4 parts:

```
123456789012.dkr.ecr.us-east-1.amazonaws.com / ada / minibank-frontend : 1.0
└──────────── registry (our AWS account) ──┘   └┬┘   └──── repo ─────┘  └tag┘
                                            your name
```

We all share **one** AWS account, so everyone puts their own name in front (`ada/...`, `tunde/...`).
That way nobody overwrites anyone else's work. 🙂

---

## 🎒 What you need before starting

Your instructor will give you these. Keep them private!

| Item | Example |
|---|---|
| Your AWS **username** (lowercase) | `ada` |
| Your **Access Key ID** | `AKIA...` |
| Your **Secret Access Key** | `wJalr...` (shown only once!) |
| The class **region** | `<CLASS-REGION>` |

You also need, from Phase 1:
- Docker Desktop running 🐳
- The `minibank` folder with your 4 images built

> 🔐 **Security rule #1:** Your access keys are like your ATM PIN.
> **Never** paste them into code, commit them to Git, screenshot them, or share them in the group chat.
> If you think they've leaked, tell your instructor immediately so they can be disabled.

---

## Step 1: Install the AWS CLI 🛠️

Open a **PowerShell** terminal in VS Code and run:

```powershell
winget install --id Amazon.AWSCLI -e --source winget
```

👉 **Close and reopen VS Code** (so it picks up the new command), then check:

```powershell
aws --version
```

You should see something like `aws-cli/2.x.x Python/3.x Windows/...`. 🎉

---

## Step 2: Log in to AWS as yourself 🔑

```powershell
aws configure
```

It will ask you 4 questions. Answer like this:

```
AWS Access Key ID [None]:      <paste your Access Key ID>
AWS Secret Access Key [None]:  <paste your Secret Access Key>
Default region name [None]:    <CLASS-REGION>
Default output format [None]:  json
```

Now ask AWS "who am I?":

```powershell
aws sts get-caller-identity
```

✅ You should see JSON ending in something like `"Arn": "arn:aws:iam::123456789012:user/ada"`.
If you see **your** username there, you're in!

> 💡 Your keys are saved in `C:\Users\<you>\.aws\credentials`. That's outside the minibank folder, so Git will never see them. Good.

---

## Step 3: Set your variables 📝

Instead of typing the long registry name 20 times, we'll store things in PowerShell variables.
**Change `ada` to YOUR username**, then paste the whole block:

```powershell
$REGION   = "<CLASS-REGION>"
$ME       = "ada"   # 👈 CHANGE THIS to your AWS username (lowercase!)
$ACCOUNT  = aws sts get-caller-identity --query Account --output text
$REGISTRY = "$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"
$TAG      = "1.0"
$SERVICES = "frontend","accounts-api","transactions-api","notifier"
```

Check it worked:

```powershell
$REGISTRY
```

You should see something like `123456789012.dkr.ecr.us-east-1.amazonaws.com`.

> ⚠️ Variables disappear when you close the terminal. If you open a new terminal later,
> **paste this block again** before continuing.

---

## Step 4: Make sure your local images exist 🐳

```powershell
docker images minibank/*
```

You should see these 4, all with tag `1.0`:

```
REPOSITORY                  TAG
minibank/frontend           1.0
minibank/accounts-api       1.0
minibank/transactions-api   1.0
minibank/notifier           1.0
```

Missing some? Go into your `minibank` folder and rebuild:

```powershell
cd minibank
docker compose build
```

> 💡 Where do these names come from? Open `docker-compose.yml` and look at the `image:` line
> under each service, e.g. `image: minibank/accounts-api:1.0`.

---

## Step 5: Create your 4 repositories in ECR 🏗️

A **repository** is like a folder in ECR that holds all versions of one image.
We need one per service:

```powershell
foreach ($svc in $SERVICES) {
  aws ecr create-repository `
    --repository-name "$ME/minibank-$svc" `
    --region $REGION `
    --image-scanning-configuration scanOnPush=true
}
```

You'll see 4 blocks of JSON, one per repo. ✅

> 💡 `scanOnPush=true` tells AWS to **automatically check every image for known security
> vulnerabilities (CVEs)** when you push it. Banks care a LOT about this.

---

## Step 6: Let Docker log in to ECR 🔓

Docker needs a password to push to a private registry. AWS gives us a temporary one:

```powershell
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY
```

✅ You should see: **`Login Succeeded`**

> ⏰ This login only lasts **12 hours**. If pushing fails tomorrow with "no basic auth credentials",
> just run this step again.

---

## Step 7: Tag and push your images 🚀

**Tagging** gives your local image its "cloud address" (like writing the delivery address on a parcel).
**Pushing** actually sends it.

```powershell
foreach ($svc in $SERVICES) {
  docker tag  "minibank/${svc}:$TAG" "$REGISTRY/$ME/minibank-${svc}:$TAG"
  docker push "$REGISTRY/$ME/minibank-${svc}:$TAG"
}
```

You'll see layers uploading: `Pushed`, `Pushed`, `Layer already exists`...
The first push takes a few minutes. ☕

> 💡 Notice that `Layer already exists` shows up a lot? Images share base layers, so Docker only uploads
> what's new. That's why images are built in layers!

---

## Step 8: Check your images are really in the cloud ☁️

**From the terminal:**

```powershell
foreach ($svc in $SERVICES) {
  aws ecr describe-images --repository-name "$ME/minibank-$svc" --region $REGION `
    --query "imageDetails[].{Tag:imageTags[0],SizeBytes:imageSizeInBytes,Pushed:imagePushedAt}" --output table
}
```

**From the AWS Console (website):**
1. Sign in at `https://<ACCOUNT_ID>.signin.aws.amazon.com/console` with your username + console password
2. Make sure the region (top-right) is **`<CLASS-REGION>`**
3. Search for **ECR** → **Repositories** → find the ones starting with **your name**

---

## Step 9: Look at your security scan results 🛡️

```powershell
foreach ($svc in $SERVICES) {
  Write-Host "`n=== $svc ===" -ForegroundColor Cyan
  aws ecr describe-image-scan-findings --repository-name "$ME/minibank-$svc" `
    --image-id imageTag=$TAG --region $REGION `
    --query "imageScanFindings.findingSeverityCounts"
}
```

You'll see counts like `{ "HIGH": 1, "MEDIUM": 4, "LOW": 7 }` (or `null` if nothing was found 🎉).

> 📝 **Write down** which of your 4 images has the most findings. We'll discuss why in class.

---

## Step 10: Prove it works by pulling from the cloud 🔁

Delete one image from your laptop, then download it back from ECR:

```powershell
docker rmi "$REGISTRY/$ME/minibank-notifier:$TAG"
docker pull "$REGISTRY/$ME/minibank-notifier:$TAG"
```

If the pull succeeds, **any machine with permission can now get your image.** That's
exactly what Kubernetes will do in Phase 2. 🎉🎉

---

## 🔄 Later: pushing a new version

Changed some code? Don't overwrite `1.0`. Make a **new version**:

1. In `docker-compose.yml`, change the `image:` tags of the services you changed from `:1.0` to `:1.1`
2. Rebuild and push:

```powershell
docker compose build
$TAG = "1.1"
foreach ($svc in $SERVICES) {
  docker tag  "minibank/${svc}:$TAG" "$REGISTRY/$ME/minibank-${svc}:$TAG"
  docker push "$REGISTRY/$ME/minibank-${svc}:$TAG"
}
```

> 💡 **Why not just use `latest`?** Because "latest" changes silently. If something breaks in
> production, you need to know *exactly* which version is running and be able to roll back to `1.0`.

---

## 🆘 Troubleshooting

| You see... | What it means | Fix |
|---|---|---|
| `'aws' is not recognized` | VS Code doesn't see the new install | Close and reopen VS Code |
| `Unable to locate credentials` | You haven't logged in | Run `aws configure` again (Step 2) |
| `InvalidClientTokenId` / `SignatureDoesNotMatch` | Access key typo | Run `aws configure` and paste the keys carefully |
| `AccessDeniedException` on create-repository | `$ME` doesn't match your AWS username | Check spelling and lowercase, then redo Step 3 |
| `InvalidParameterException` ... repository name | Uppercase letters in the name | Repo names must be **lowercase** |
| `RepositoryAlreadyExistsException` | You already created it | That's fine! Continue to the next step |
| `no basic auth credentials` / `denied` on push | Docker login expired (12h) or wrong region | Redo Step 6 |
| `No such image` / `does not exist locally` on tag | Local image name or tag is different | Run `docker images minibank/*` and compare with `$TAG` |
| `RepositoryNotFoundException` | Skipped Step 5, or wrong region | Check `$REGION`, then redo Step 5 |
| `$REGISTRY` is empty / weird errors after reopening terminal | Variables were lost | Re-paste the Step 3 block |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Start Docker Desktop and wait for 🟢 |

Still stuck? Copy the **exact** error message (not a screenshot of your keys!) and ask in class.

---

## 🧹 Cleaning up (only when your instructor says so)

ECR costs a little money for storage, so at the end of the course:

```powershell
foreach ($svc in $SERVICES) {
  aws ecr delete-repository --repository-name "$ME/minibank-$svc" --region $REGION --force
}
```

⚠️ This permanently deletes your images. **Don't** do it before Phase 2 and 3, because we need them!

---

## 🤔 Check yourself

Try to answer these without looking back:

1. Why can't Kubernetes just use the images on your laptop?
2. Break this name into its parts: `123456789012.dkr.ecr.us-east-1.amazonaws.com/tunde/minibank-notifier:1.1`
3. What's the difference between `docker tag` and `docker push`?
4. Why does everyone put their own name in front of their repository names?
5. Your push failed this morning but worked yesterday. What's the most likely reason?
6. Why do we use `1.0`, `1.1` instead of `latest`?
7. What does `scanOnPush` do, and why would a bank care?
8. Where are your AWS keys stored on your laptop, and why is it important they are NOT in the minibank folder?

---

## ⏭️ What's next?

In **Phase 2: Kubernetes**, each MiniBank service becomes a **Deployment** that pulls *your*
image from ECR. Because ECR is **private**, Kubernetes will also need a login.
You'll learn how to give it one with an **imagePullSecret**. 🚢

Great work! 💪
