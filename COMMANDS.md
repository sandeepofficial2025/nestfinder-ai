# 📖 NestFinder AI — Operations & CLI Command Reference

This document provides a complete step-by-step reference for all commands used to build, test, run, record, deploy, and publish the **NestFinder AI** agent.

---

## 📋 Table of Contents
1. [Environment & API Key Setup](#1-environment--api-key-setup)
2. [Local Server & Agent Execution](#2-local-server--agent-execution)
3. [Agent Runtime Deployment (Cloud Run / Vertex AI)](#3-agent-runtime-deployment)
4. [Demo Recording & GIF Optimization](#4-demo-recording--gif-optimization)
5. [GitHub Authentication & Repository Publishing](#5-github-authentication--repository-publishing)

---

## 1. Environment & API Key Setup

### Environment Variables
To run NestFinder AI locally or deploy it, set the following environment variables:

```bash
# Enable Vertex AI for Gemini models
export GOOGLE_GENAI_USE_VERTEXAI="true"

# Google Cloud Project & Region
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-03-eb3066a4dd0c"
export GOOGLE_CLOUD_LOCATION="us-west1"

# Google Maps API Key (Geocoding & Places APIs)
export GOOGLE_MAPS_API_KEY="AIzaSyD8nAc_uqxvk32WM9MAQm4k9fg1YWn1UZE"

# Agent Engine Reasoning Engine Resource Name
export AGENT_ENGINE_RESOURCE_NAME="projects/132971172205/locations/us-west1/reasoningEngines/7787889238049030144"
export AGENT_DIRECTORY="app"
```

### Install Dependencies
```bash
# Install root agent dependencies
pip install -r requirements.txt

# Install frontend proxy dependencies
pip install -r frontend/requirements.txt
```

---

## 2. Local Server & Agent Execution

### Start Local Frontend Proxy
Run the FastAPI web application from the `frontend/` folder on `http://localhost:8080`:

```bash
cd frontend
python main.py
```

### Test Local Endpoints
```bash
# Health check
curl -I http://localhost:8080/

# Test agent chat endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search 2BR apartments in SoHo under $4000"}'
```

---

## 3. Agent Runtime Deployment

### Deploy Agent to Vertex AI Reasoning Engine
Deploy or update the agent on Google Cloud Vertex AI using `agents-cli`:

```bash
agents-cli deploy \
  --no-confirm-project \
  --update-env-vars GOOGLE_MAPS_API_KEY=AIzaSyD8nAc_uqxvk32WM9MAQm4k9fg1YWn1UZE
```

### Deploy Frontend to Cloud Run
Deploy the FastAPI frontend proxy to Google Cloud Run:

```bash
gcloud run deploy nestfinder-frontend \
  --source ./frontend \
  --region us-west1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/132971172205/locations/us-west1/reasoningEngines/7787889238049030144",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```

---

## 4. Demo Recording & GIF Optimization

### 1. Install Recording & Video Processing Libraries
```bash
pip install playwright imageio-ffmpeg moviepy numpy gTTS
playwright install chromium
```

### 2. Run Playwright Automated Demo Recording
Execute the automated browser recording script (`record_demo.py`):
```bash
python record_demo.py
```

### 3. Convert Video Recording to Looping GIF
Convert `.webm` screen recording to an optimized 720p 10fps `demo.gif` using `ffmpeg`:

```bash
ffmpeg -y -i recordings/*.webm \
  -vf "fps=10,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 demo.gif
```

---

## 5. GitHub Authentication & Repository Publishing

### 1. Device Code Authentication
To authenticate GitHub CLI without browser redirects:

```bash
gh auth login --hostname github.com --git-protocol https --web
```
*Follow the on-screen prompt: open `https://github.com/login/device` and enter your one-time device code.*

### 2. Initialize Git & Create Initial Commit
```bash
git init
git branch -M main
git config user.name "Developer"
git config user.email "developer@example.com"
git add .
git commit -m "Initial commit: NestFinder AI agent with ADK, A2UI, Firestore, Maps, and Multimodal Tools"
```

### 3. Create Public Repository & Push Code
```bash
gh repo create nestfinder-ai --public --source=. --remote=origin --push
```
*Remote repository published to: `https://github.com/sandeepofficial2025/nestfinder-ai`*
