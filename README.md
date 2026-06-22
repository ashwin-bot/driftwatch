# DriftWatch

Autonomous GitHub bot that detects documentation drift in merged PRs.
Watches merged pull requests, matches changed code to the doc sections
that reference it using embeddings, and posts a PR comment flagging
outdated sections with an LLM-drafted suggested update.

## Status
🚧 In development — webhook receiver working end-to-end (GitHub → ngrok → FastAPI).
Next: signature verification, event filtering, GitHub App auth.

## Architecture
1. PR merged → GitHub webhook fires
2. FastAPI service extracts the diff (function-level chunks via tree-sitter)
3. Diff is embedded and matched against a pre-indexed doc corpus (pgvector)
4. Flagged sections get an LLM-drafted update
5. Result posted back as a PR comment

## Stack
- FastAPI (webhook + orchestration)
- GitHub App (auth + API access)
- pgvector / PostgreSQL (embeddings + metadata)
- tree-sitter (code chunking)
- Claude / OpenAI API (drafting)

## Local setup
\`\`\`
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

Create a `.env` with:
\`\`\`
GITHUB_APP_ID=
GITHUB_WEBHOOK_SECRET=
GITHUB_PRIVATE_KEY_PATH=
GITHUB_INSTALLATION_ID=
\`\`\`