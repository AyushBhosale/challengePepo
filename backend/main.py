from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import time
import os
from dotenv import load_dotenv
import tempfile
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Load env vars
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "sora")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "preview")

headers = {
    "api-key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}

class VideoPrompt(BaseModel):
    prompt: str
    width: int = 480
    height: int = 480
    n_seconds: int = 5

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Generation API using Azure OpenAI!"}


@app.post("/generate-video")
def generate_video(data: VideoPrompt, background_tasks: BackgroundTasks):
    # Step 1: Create job
    create_url = f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs?api-version={OPENAI_API_VERSION}"
    body = {
        "prompt": data.prompt,
        "width": data.width,
        "height": data.height,
        "n_seconds": data.n_seconds,
        "model": AZURE_OPENAI_DEPLOYMENT_NAME
    }
    try:
        response = requests.post(create_url, headers=headers, json=body)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create video job: {str(e)}")

    job_id = response.json().get("id")
    if not job_id:
        raise HTTPException(status_code=500, detail="No job ID returned from Azure.")

    # Step 2: Poll job status
    status_url = f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/jobs/{job_id}?api-version={OPENAI_API_VERSION}"
    status = None
    while status not in ("succeeded", "failed", "cancelled"):
        time.sleep(5)
        status_response = requests.get(status_url, headers=headers).json()
        status = status_response.get("status")

    if status != "succeeded":
        raise HTTPException(status_code=500, detail=f"Video generation failed. Status: {status}")

    # Step 3: Download video
    generations = status_response.get("generations", [])
    if not generations:
        raise HTTPException(status_code=500, detail="No video generations found.")

    generation_id = generations[0].get("id")
    video_url = f"{AZURE_OPENAI_ENDPOINT}/openai/v1/video/generations/{generation_id}/content/video?api-version={OPENAI_API_VERSION}"
    video_response = requests.get(video_url, headers=headers)

    if not video_response.ok:
        raise HTTPException(status_code=500, detail="Failed to download video.")

    # Step 4: Create a temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_file.write(video_response.content)
    tmp_file.close()

    # Schedule deletion after response is sent
    background_tasks.add_task(os.remove, tmp_file.name)

    # Step 5: Return video file
    return FileResponse(tmp_file.name, media_type="video/mp4", filename="output.mp4")
