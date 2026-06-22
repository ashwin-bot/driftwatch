# main.py
import json
import logging
from fastapi import FastAPI, Request

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("driftwatch")

@app.post("/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    event = request.headers.get("X-GitHub-Event")
    logger.info(f"Received event: {event}")
    logger.info(json.dumps(json.loads(body), indent=2)[:500])
    return {"status": "received"}