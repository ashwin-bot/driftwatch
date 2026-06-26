# main.py
import hmac
import hashlib
import json
import logging
import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("driftwatch")

WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]

def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    if not signature_header:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)

@app.post("/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    event = request.headers.get("X-GitHub-Event")
    logger.info(f"Received event: {event}")
    logger.info(json.dumps(json.loads(body), indent=2)[:500])
    return {"status": "received"}