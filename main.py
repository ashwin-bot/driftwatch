# main.py
import hmac
import hashlib
import json
import logging
import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from github_auth import get_installation_token
from diff_extractor import extract_changed_chunks

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("driftwatch")

WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]
GITHUB_APP_ID = os.environ["GITHUB_APP_ID"]
GITHUB_PRIVATE_KEY_PATH = os.environ["GITHUB_PRIVATE_KEY_PATH"]
GITHUB_INSTALLATION_ID = os.environ["GITHUB_INSTALLATION_ID"]

def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    if not signature_header:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)

@app.post("/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(body, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    payload = json.loads(body)

    if event == "pull_request" and payload.get("action") == "closed" and payload["pull_request"].get("merged"):
        pr = payload["pull_request"]
        owner = payload["repository"]["owner"]["login"]
        repo = payload["repository"]["name"]
        logger.info(f"Merged PR #{pr['number']} in {payload['repository']['full_name']}: {pr['title']}")

        try:
            token = get_installation_token(GITHUB_APP_ID, GITHUB_PRIVATE_KEY_PATH, GITHUB_INSTALLATION_ID)
            chunks = extract_changed_chunks(owner, repo, pr["number"], token)
            for c in chunks:
                logger.info(f"Changed {c['type']} '{c['name']}' in {c['file']} (lines {c['start_line']}-{c['end_line']})")
        except Exception:
            logger.exception(f"Failed to extract chunks for PR #{pr['number']}")
    else:
        logger.info(f"Ignored event: {event} / action: {payload.get('action')}")

    return {"status": "received"}