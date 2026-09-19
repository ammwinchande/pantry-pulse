# AWS Deployment Guide for PantryPulse

This guide details how to deploy PantryPulse on AWS for your hackathon live demo. The app is backed by a **PostgreSQL** datastore, selected purely via the `DATABASE_URL` environment variable — no code changes.

> **Cost note:** the app itself is cheap (App Runner ≈ **$0.40/day**). A managed PostgreSQL database (RDS `db.t4g.micro`, single-AZ) adds roughly **$12–20/month** (~$0.10–0.17/hr). For a short demo window the total stays well under **$1**. If you want to hold the line at ~$0.50, skip the RDS step and let the app use its SQLite default — see the note at the end.

---

## 🏆 Option A: AWS App Runner (Recommended — Quickest & Cheapest)

**Why App Runner?**
- **Cost**: Approximately **$0.007/GB-hour** when active, and **drops to near $0** when idle. Even running for the entire hackathon evaluation period, it typically consumes **less than $0.50** of your $100 credit.
- **HTTPS URL**: Automatically provisions an SSL certificate and public domain: `https://<random-id>.<region>.awsapprunner.com`.
- **Zero Server Management**: No EC2 instances or SSH keys to configure.

### Step 0 — Create the RDS PostgreSQL instance

1. Go to **RDS** → **Create database** → **Standard create**.
2. **Engine:** PostgreSQL. **Template:** **Micro** (or **Free tier** if available in your region).
3. **Instance:** `db.t4g.micro` (single-AZ — cheapest; multi-AZ costs ~2×).
4. **Settings:**
   - **DB name:** `pantrypulse`
   - **Master username:** `pantrypulse`
   - **Master password:** a strong password (save it — needed for `DATABASE_URL`).
5. **Connectivity:**
   - **Public accessibility:** **Yes** (so App Runner can reach it).
   - **Security group:** create a new one, e.g. `pantrypulse-rds`, allowing inbound **TCP 5432**.
6. Click **Create database** and wait for status **Available** (~5–10 min).
7. Note the **endpoint** from the DB's **Connectivity** tab, e.g. `pantrypulse-xxxx.c9abcdef.us-west-2.rds.amazonaws.com`.

> The backend creates its tables and seeds demo data on first boot (`SEED_ON_STARTUP=true`), so you do **not** need to run migrations manually.

### Step-by-Step Deployment via AWS Web Console:

1. **Push your code to GitHub**:
   Make sure your repo is pushed to GitHub (e.g. `github.com/your-username/pantry-pulse`).

2. **Open AWS App Runner**:
   - Go to the [AWS Management Console](https://console.aws.amazon.com/).
   - Search for **App Runner** and click **Create an App Runner service**.

3. **Source Configuration**:
   - **Repository type**: Select **Source code repository**.
   - **Connect to GitHub**: Click **Add new** to authorize AWS to access your repository.
   - Select your repository and branch (`main`).
   - **Deployment trigger**: Select **Manual** (to prevent accidental builds during testing).

4. **Build Settings**:
   - **Configuration file**: Choose **Configure all settings here**.
   - **Runtime**: Select **Python 3**.
   - **Build command**:
     ```bash
     pip install uv && cd frontend && npm install && npm run build && cd ../backend && uv pip install --system -r requirements.txt
     ```
   - **Start command**:
     ```bash
     cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
     ```
   - **Port**: Enter `8000`.

5. **Alternative (Using Dockerfile directly)**:
   - If using ECR (Elastic Container Registry) or App Runner Docker build:
     - Point App Runner to the repository's `Dockerfile`.
     - App Runner will build the multi-stage Docker image and launch on port `8000`.

6. **Service Configuration**:
   - **Service name**: `pantry-pulse`
   - **Virtual CPU & Memory**: `1 vCPU, 2 GB` (minimum tier, cheapest).
   - **Environment variables** (add these):

     | Variable           | Value                                                                         |
     | ------------------ | ----------------------------------------------------------------------------- |
     | `PORT`             | `8000`                                                                        |
     | `STATIC_DIR`       | `/app/frontend/dist`                                                          |
     | `DATABASE_URL`     | `postgresql+psycopg://pantrypulse:<password>@<rds-endpoint>:5432/pantrypulse` |
     | `SEED_ON_STARTUP`  | `true`                                                                        |
     | `JWT_SECRET_KEY`   | a long random string (e.g. `openssl rand -hex 32`)                            |
     | `MAILTRAP_API_KEY` | your Mailtrap API key (password-reset emails)                                 |
     | `AWS_REGION`       | `us-west-2` (or your region)                                                  |

   - Click **Next**, review, and click **Create & deploy**.

   > The `psycopg` PostgreSQL driver is already in `backend/requirements.txt`, so the image is ready to talk to RDS.

7. **Allow App Runner to reach RDS**:
   - In **App Runner** → your service → **Network**, note the security group App Runner created.
   - In **RDS** → your DB → **Security** → the `pantrypulse-rds` security group → **Inbound rules** → **Edit**, add: **Type** Custom TCP, **Port** `5432`, **Source** = the App Runner security group (or its VPC CIDR).

8. **Grab your Live Demo Link**:
   - In 3–5 minutes, App Runner will show **Status: Running** and provide your `Default domain` (e.g. `https://7x9abc123.us-east-1.awsapprunner.com`).
   - Open it and log in with the seeded demo coordinator (`coordinator@pantrypulse.org` / `Coordinator123!`).
   - Paste this URL directly into your Devpost submission!

---

## 🛡️ Cost Protection & Safety Tips

1. **Set an AWS Budget Alert**:
   - In AWS Console, go to **Billing and Cost Management** $\rightarrow$ **Budgets**.
   - Create a budget for **$5.00**. Set it to email you if actual or forecasted costs reach 80% ($4.00).
2. **Pause Service After Judging**:
   - Once hackathon judging completes, go to App Runner $\rightarrow$ **Actions** $\rightarrow$ **Pause**.
   - A paused App Runner service incurs **$0.00** compute charges.
3. **Delete the RDS Instance When Done**:
   - A running RDS instance keeps billing even if the app is paused. After judging, go to **RDS** → your DB → **Actions** → **Delete** (skip the snapshot if you don't need the data) to stop database charges.

---

## 🌐 Option B: AWS Lightsail (fixed-cost VM, Docker Compose + Postgres)

If you prefer a 100% fixed-cost virtual machine where you can never be billed extra, the repo's `docker-compose.yml` already defines a **PostgreSQL** service alongside the app — the whole stack (including the database) runs on one machine.
1. In AWS Console, open **Amazon Lightsail**.
2. Click **Create instance** $\rightarrow$ select **Linux/Unix** $\rightarrow$ **OS Only** $\rightarrow$ **Ubuntu 22.04 or 24.04**.
3. Select the **$7.00/month** plan (2 GB RAM, 1 vCPU, 50 GB SSD). (512 MB is too tight for Postgres + the app.)
4. In the browser-based SSH terminal:
   ```bash
   git clone https://github.com/your-username/pantry-pulse.git
   cd pantry-pulse
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose
   sudo docker-compose up -d --build
   ```
   The compose file sets `DATABASE_URL=postgresql+psycopg://pantry:pantry@postgres:5432/pantry-pulse` for the app and persists the database in a named volume. The app waits for Postgres to be healthy before starting.
5. In Lightsail **Networking** tab, add a firewall rule to allow port **8000** (or port 80).
6. Your live demo is available at `http://<your-lightsail-public-ip>:8000`. Log in with the seeded demo coordinator (`coordinator@pantrypulse.org` / `Coordinator123!`).

---

## 💡 Want to stay under ~$0.50? Use SQLite

PostgreSQL is the right choice for a real deployment, but it's the main cost driver above. If the demo window is short and you want to minimize spend, skip the RDS step (Option A) or the Postgres service (Option B) and leave `DATABASE_URL` unset — the app then defaults to SQLite and runs on App Runner alone at ~$0.40/day. The code is identical either way; only the environment variable changes.
