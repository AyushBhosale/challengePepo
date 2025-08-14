
# Peppo

This project is designed to Generate videos based on large context. It allows users to generate videos, e.g., upload files, interact with data, chat with AI. The system is built using React for frontend, FastAPI for backend, cloud for Video model sora and embedding model Ada ensuring speed, reliability, scalability, or other key benefits.


## Demo

**frontend:-**
https://frontend-pepo-latest.onrender.com

**backend:-**
https://pepo-backend-latest.onrender.com

## Tech Stack

**Client:** React

**Server:** Fastapi

**Ai Models and Cloud:** Azure

**Deployment:** Docker, Render


## Code & Set-Up

**CodeBase:-** https://github.com/AyushBhosale/challengePepo

**Docker Images**

Server Side:- https://hub.docker.com/repository/docker/ayushbhosale/pepo-backend/general

Client Side:- https://hub.docker.com/repository/docker/ayushbhosale/frontend-pepo/general

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (CMD)
.venv\Scripts\activate.bat
# Linux / macOS
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run the FastAPI server
uvicorn main:app --reload

# React setup 
# 1. Navigate to the frontend folder
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev




```
## Current Limitations

1. Since It's deployed on free tier its facing problem cold start.
2. Seondly there's a bug by which I able to access the my backend from any chrome I am currently working on it. 
