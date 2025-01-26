from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from dotenv import load_dotenv
from .slack_bot import SlackWordCountBot

# Load environment variables
load_dotenv()

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Slack bot with tokens based on mode
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_app_token = os.getenv("SLACK_APP_TOKEN")  # Optional for socket mode

if not slack_bot_token:
    raise ValueError("Missing required SLACK_BOT_TOKEN in .env file")

# Initialize bot with both tokens if running in socket mode, otherwise just bot token
slack_bot = SlackWordCountBot(slack_bot_token, slack_app_token if os.getenv("USE_SOCKET_MODE") else None)

@app.on_event("startup")
async def startup_event():
    """Start the Slack bot when the FastAPI app starts."""
    slack_bot.start()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
