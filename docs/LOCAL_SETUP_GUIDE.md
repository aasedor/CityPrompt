# Local Development Setup Guide

A step-by-step guide to get the 3D Development Platform running on your computer. This guide assumes zero prior experience with development tools.

---

## Table of Contents

1. [What You're Setting Up](#1-what-youre-setting-up)
2. [Install Required Software](#2-install-required-software)
3. [Get API Keys](#3-get-api-keys)
4. [Download the Project Code](#4-download-the-project-code)
5. [Configure Environment Variables](#5-configure-environment-variables)
6. [Start the Application](#6-start-the-application)
7. [Verify Everything Works](#7-verify-everything-works)
8. [Day-to-Day Development](#8-day-to-day-development)
9. [Troubleshooting](#9-troubleshooting)
10. [Cloud Services We Use](#10-cloud-services-we-use)

---

## 1. What You're Setting Up

This project is a web application that turns architectural documents into interactive 3D models. It has several parts that all work together:

| Component | What It Does |
|-----------|-------------|
| **Frontend** | The website you see in the browser (React, Three.js, Mapbox maps) |
| **Backend API** | The server that handles requests, user accounts, data (Python/FastAPI) |
| **Celery Worker** | A background process that handles slow tasks like AI 3D generation |
| **PostgreSQL** | The database that stores users, projects, buildings, zones |
| **PostGIS** | A database extension that adds map/geospatial support |
| **Redis** | A fast in-memory store used for background task queuing |
| **MinIO** | Local file storage (simulates cloud storage on your machine) |

You don't need to understand all of these right now. Docker (which you'll install below) bundles everything together so it all starts with one command.

---

## 2. Install Required Software

### 2.1 Install Git

Git is a tool that lets multiple people work on the same code and track changes.

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download the installer and run it
3. Click **Next** through all the defaults (the default options are fine)
4. On the "Adjusting your PATH environment" screen, keep the recommended option selected
5. Click **Install**, then **Finish**

**Mac:**
1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
2. Type `git --version` and press Enter
3. If Git isn't installed, macOS will prompt you to install it — follow the prompts

**How to verify:** Open a terminal (see box below) and type:
```
git --version
```
You should see something like `git version 2.43.0`.

> **What is a terminal?**
> A terminal (also called "command prompt" or "command line") is a text-based way to interact with your computer. Instead of clicking icons, you type commands.
>
> - **Windows:** Press `Win + S`, type "Git Bash", and open it. Use Git Bash for all commands in this guide (not Command Prompt or PowerShell).
> - **Mac:** Press `Cmd + Space`, type "Terminal", press Enter.

### 2.2 Install Docker Desktop

Docker runs each service (database, API, frontend, etc.) in isolated containers so you don't have to install them individually.

1. Go to https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for your operating system
3. Run the installer
4. **Windows users:** During installation, make sure "Use WSL 2 instead of Hyper-V" is checked
5. After installation, **restart your computer**
6. Open Docker Desktop — you'll see a whale icon in your system tray/menu bar
7. Wait for it to say "Docker Desktop is running"

**How to verify:** Open a terminal and type:
```
docker --version
docker compose version
```
You should see version numbers for both (Docker 24+ and Compose v2+).

> **Windows users:** If Docker asks you to install or update WSL 2, follow its instructions. WSL 2 is a Windows feature that Docker needs.

### 2.3 Install Node.js

Node.js runs JavaScript outside the browser. The frontend build tools need it.

1. Go to https://nodejs.org/
2. Download the **LTS** version (the one that says "Recommended For Most Users")
3. Run the installer, accept all defaults
4. **Windows users:** Make sure "Add to PATH" is checked during installation

**How to verify:** Open a **new** terminal and type:
```
node --version
npm --version
```
You should see `v20.x.x` (or higher) and `10.x.x` (or higher).

### 2.4 Install Python

Python runs the backend API and AI processing.

1. Go to https://www.python.org/downloads/
2. Download Python **3.11** or **3.12** (not 3.13 — some libraries don't support it yet)
3. Run the installer
4. **IMPORTANT (Windows):** Check the box that says **"Add Python to PATH"** at the bottom of the first screen before clicking Install
5. Click "Install Now"

**How to verify:** Open a **new** terminal and type:
```
python --version
```
You should see `Python 3.11.x` or `3.12.x`.

> **Mac users:** If `python` doesn't work, try `python3` instead. You may want to install via Homebrew: `brew install python@3.11`

### 2.5 Install a Code Editor (Recommended)

You'll need a text editor to view and edit code. We recommend:

**Visual Studio Code (VS Code):**
1. Go to https://code.visualstudio.com/
2. Download and install
3. Recommended extensions to install (click the Extensions icon on the left sidebar, search and install each):
   - **Python** (by Microsoft)
   - **ESLint** (by Microsoft)
   - **Tailwind CSS IntelliSense** (by Tailwind Labs)
   - **GitLens** (by GitKraken)

---

## 3. Get API Keys

The application uses three external services that require API keys. You'll need to create free accounts and generate keys.

### 3.1 Anthropic (Claude AI) — Required

Claude AI interprets uploaded architectural documents and extracts building data.

1. Go to https://console.anthropic.com/
2. Click **Sign Up** and create an account
3. Add a payment method (you'll get $5 free credit to start)
4. Go to **API Keys** in the left sidebar
5. Click **Create Key**
6. Give it a name like "3d-platform-dev"
7. **Copy the key** — it starts with `sk-ant-...`
8. Save it somewhere safe (you'll need it in Step 5)

### 3.2 Mapbox — Required

Mapbox provides the satellite map tiles and geocoding for the site planner.

1. Go to https://www.mapbox.com/
2. Click **Sign Up** and create an account (free tier: 50,000 map loads/month)
3. After signing in, you'll land on your account page
4. Your **default public token** is shown on the main page — it starts with `pk.`
5. **Copy the token**
6. Save it somewhere safe

### 3.3 Meshy.ai — Optional

Meshy generates AI-powered 3D models from text or image prompts. This is optional — the platform can generate basic procedural 3D models without it.

1. Go to https://www.meshy.ai/
2. Click **Sign Up** and create an account (free tier: 5 credits/day)
3. Go to your account **Settings** > **API**
4. Click **Create API Key**
5. **Copy the key**
6. Save it somewhere safe

---

## 4. Download the Project Code

### 4.1 Clone the Repository

Open your terminal and navigate to where you want the project. Then run:

```bash
cd ~/Desktop
git clone https://github.com/beemanbesh/3D-Maps.git
cd 3D-Maps
```

> **What does this do?**
> - `cd ~/Desktop` — moves to your Desktop folder
> - `git clone ...` — downloads all the project code from GitHub
> - `cd 3D-Maps` — moves into the project folder

You should now have a `3D-Maps` folder on your Desktop.

### 4.2 Open in VS Code (Optional)

If you installed VS Code:
```bash
code .
```
This opens the entire project in VS Code. You can also open VS Code manually and go to **File > Open Folder** and select the `3D-Maps` folder.

---

## 5. Configure Environment Variables

Environment variables are settings (like API keys and passwords) that the application reads when it starts. They're stored in a file called `.env` which is **never uploaded to GitHub** (to keep your keys secret).

### 5.1 Create Your .env File

In your terminal (make sure you're in the project folder):

```bash
cp .env.example .env
```

> **What does this do?** It copies the template file `.env.example` to a new file called `.env`. The template has placeholder values that you'll replace with your real keys.

### 5.2 Edit the .env File

Open the `.env` file in your code editor (or any text editor). Find these three lines and replace the placeholder values with your real API keys from Step 3:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token-here
MESHY_API_KEY=
```

Replace them with your actual keys:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...your-real-key...xxxxx
MAPBOX_ACCESS_TOKEN=pk.eyJ1Ijoixxxxxxx...your-real-token...xxxxx
MESHY_API_KEY=your-meshy-key-here
```

**Leave everything else as-is.** The other values (database passwords, Redis URL, etc.) are defaults that work with Docker out of the box.

Save and close the file.

> **IMPORTANT:** Never share your `.env` file or commit it to Git. It contains secret keys that could cost you money if exposed.

---

## 6. Start the Application

### 6.1 Make Sure Docker Desktop Is Running

Look for the Docker whale icon in your system tray (Windows) or menu bar (Mac). If it's not there, open Docker Desktop and wait for it to start.

### 6.2 Start All Services

In your terminal, make sure you're in the project folder, then run:

```bash
docker compose up -d
```

> **What does this do?**
> - `docker compose` — the tool that manages multiple containers
> - `up` — start all the services defined in `docker-compose.yml`
> - `-d` — run in the background (so you get your terminal back)

**The first time you run this, it will take 5-15 minutes** because Docker needs to:
- Download base images (Python, Node.js, PostgreSQL, Redis, MinIO)
- Install all Python and JavaScript dependencies
- Set up the database

You'll see a lot of text scrolling. This is normal.

### 6.3 Watch the Progress

To see what's happening:

```bash
docker compose logs -f
```

This shows real-time logs from all services. Press `Ctrl + C` to stop watching (this stops the log view, not the services).

To watch a specific service:
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery-worker
```

### 6.4 Check That Everything Started

```bash
docker compose ps
```

You should see all services with status **"running"**:

```
NAME                   STATUS
devplatform-db         running (healthy)
devplatform-redis      running (healthy)
devplatform-minio      running
devplatform-backend    running
devplatform-celery     running
devplatform-frontend   running
```

If any service shows "exited" or "restarting", see [Troubleshooting](#9-troubleshooting).

---

## 7. Verify Everything Works

Open your web browser and check each service:

| What to Check | URL | What You Should See |
|--------------|-----|-------------------|
| Frontend | http://localhost:5173 | The application's login/home page |
| API Health | http://localhost:8000/health | `{"status":"healthy","version":"0.1.0"}` |
| API Docs | http://localhost:8000/docs | Interactive Swagger documentation |
| MinIO Console | http://localhost:9001 | MinIO login page (user: `minioadmin`, password: `minioadmin`) |

### Quick Functionality Test

1. Open http://localhost:5173
2. Click **Register** and create an account (this is local only — just use any email/password)
3. Log in with your new account
4. Create a new project
5. Open the project — you should see the 3D viewer and site planner map
6. If the map loads with satellite imagery, Mapbox is working

---

## 8. Day-to-Day Development

### Starting Your Day

```bash
# 1. Open Docker Desktop (if not already running)
# 2. Open your terminal and navigate to the project
cd ~/Desktop/3D-Maps

# 3. Start all services
docker compose up -d

# 4. Open VS Code
code .
```

### Stopping at End of Day

```bash
docker compose down
```

This stops all containers but **keeps your data** (database, uploaded files).

### Pulling Latest Changes

When someone else pushes code updates:

```bash
# 1. Save your own changes first
git add .
git commit -m "My changes"

# 2. Pull the latest code
git pull

# 3. Rebuild containers (if dependencies changed)
docker compose up -d --build
```

### Making Changes

- **Frontend code** (`frontend/src/`): Changes auto-reload in the browser (hot module replacement)
- **Backend code** (`backend/app/`): Changes auto-reload the API server
- **Database changes**: If someone adds a migration, run:
  ```bash
  docker compose exec backend alembic upgrade head
  ```

### Resetting Everything

If something goes wrong and you want a fresh start:

```bash
# Stop everything and delete all data (database, uploads, etc.)
docker compose down -v

# Start fresh
docker compose up -d
```

> **Warning:** `docker compose down -v` deletes all local data (accounts, projects, uploaded files). Only use this for a fresh start.

### Running Without Docker (Advanced)

If you prefer running services directly on your machine (useful for debugging):

**Terminal 1 — Backend API:**
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows Git Bash: source venv/Scripts/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Celery Worker:**
```bash
cd backend
source venv/bin/activate    # Windows Git Bash: source venv/Scripts/activate
celery -A app.tasks.worker worker --loglevel=info
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

> **Note:** When running without Docker, you still need PostgreSQL, Redis, and MinIO running somewhere (either via Docker or installed locally). The Docker approach is much simpler.

---

## 9. Troubleshooting

### "docker: command not found"

Docker Desktop isn't installed or isn't running. Install it from https://www.docker.com/products/docker-desktop/ and make sure it's started.

### "port 5432 already in use"

Another PostgreSQL instance is running on your machine. Either stop it, or change the port in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Use 5433 on your machine instead
```

### Backend keeps restarting

Check the logs:
```bash
docker compose logs backend
```

Common causes:
- Missing API keys in `.env` (check Step 5)
- Database not ready yet (wait 30 seconds and check again)

### Frontend shows blank page

Check the browser console for errors (press `F12`, click "Console" tab). Common causes:
- API server not running — check `docker compose ps`
- Missing `MAPBOX_ACCESS_TOKEN` in `.env`

### "Cannot connect to Docker daemon"

Docker Desktop isn't running. Open Docker Desktop and wait for it to start.

### Changes not appearing

- **Frontend:** Try a hard refresh (`Ctrl + Shift + R`)
- **Backend:** Check if the container is running: `docker compose ps`
- **Dependencies changed:** Rebuild: `docker compose up -d --build`

### Need to completely reset

```bash
docker compose down -v
docker compose up -d --build
```

---

## 10. Cloud Services We Use

These are the external services the project relies on. The team has active accounts for each.

### Currently Active Services

| Service | Purpose | Plan | Cost | URL |
|---------|---------|------|------|-----|
| **GitHub** | Code hosting & version control | Free | Free | https://github.com/beemanbesh/3D-Maps |
| **Render.com** | Cloud hosting (production) | Multiple services | ~$21/mo total | https://dashboard.render.com |
| **Anthropic** | Claude AI for document analysis | Pay-as-you-go | Usage-based | https://console.anthropic.com |
| **Mapbox** | Satellite maps & geocoding | Free tier | Free (50K loads/mo) | https://www.mapbox.com |
| **Meshy.ai** | AI 3D model generation | Free tier | Free (5 credits/day) | https://www.meshy.ai |
| **Cloudflare R2** | Cloud file storage (production) | Free tier | Free (10GB/10M reads) | https://dash.cloudflare.com |

### Render.com Services (Production)

These run the live/deployed version of the app:

| Render Service | Type | Plan | Cost/mo | What It Does |
|---------------|------|------|---------|-------------|
| `3d-platform-frontend` | Static Site | Free | $0 | Hosts the React app |
| `3d-platform-api` | Web Service | Standard | $7 | Runs the FastAPI backend |
| `3d-platform-worker` | Background Worker | Standard | $7 | Runs Celery task processing |
| `3d-platform-db` | PostgreSQL | Basic 256MB | $7 | Database with PostGIS |
| `3d-platform-redis` | Key Value (Redis) | Starter | $7 | Task queue & caching |

### What You Need for Local Development

For local development, you only need **API keys** — you do NOT need Render, Cloudflare, or any cloud infrastructure. Docker simulates all infrastructure locally:

| Cloud Service | Local Equivalent (via Docker) |
|--------------|------------------------------|
| Render PostgreSQL | Local PostgreSQL container |
| Render Redis | Local Redis container |
| Cloudflare R2 | Local MinIO container (S3-compatible) |

**API keys you DO need locally:**
- `ANTHROPIC_API_KEY` — for AI document analysis
- `MAPBOX_ACCESS_TOKEN` — for map tiles in the site planner
- `MESHY_API_KEY` — for AI 3D generation (optional)

---

## Quick Reference

### Useful Commands

| Command | What It Does |
|---------|-------------|
| `docker compose up -d` | Start all services in background |
| `docker compose down` | Stop all services (keep data) |
| `docker compose down -v` | Stop all services and DELETE all data |
| `docker compose ps` | Show status of all services |
| `docker compose logs -f` | Watch all logs (Ctrl+C to stop watching) |
| `docker compose logs -f backend` | Watch backend logs only |
| `docker compose up -d --build` | Rebuild and restart (after dependency changes) |
| `docker compose exec backend alembic upgrade head` | Apply database migrations |
| `git pull` | Download latest code from GitHub |
| `git status` | See what files you've changed |
| `git add .` | Stage all your changes |
| `git commit -m "message"` | Save your changes locally |
| `git push` | Upload your changes to GitHub |

### Access Points (Local Development)

| Service | URL |
|---------|-----|
| Frontend App | http://localhost:5173 |
| API Documentation | http://localhost:8000/docs |
| API Health Check | http://localhost:8000/health |
| MinIO Storage Console | http://localhost:9001 |

### Default Credentials (Local Only)

| Service | Username | Password |
|---------|----------|----------|
| PostgreSQL | `devuser` | `devpassword` |
| MinIO | `minioadmin` | `minioadmin` |
