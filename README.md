# Copilot Gateway

A FastAPI + LangChain service that lets you use **GitHub Copilot Chat and Agent mode in VSCode for free**, backed by Google Gemini (or any OpenAI-compatible LLM). It exposes an OpenAI-compatible API that VSCode's BYOK (Bring Your Own Key) system connects to directly.

```
VSCode Copilot Chat / Agent
        │  OpenAI-compatible HTTP
        ▼
┌──────────────────────┐
│   copilot-gateway    │   GET  /v1/models
│   FastAPI + LangChain│   POST /v1/chat/completions
└──────────┬───────────┘
           │ LangChain
           ▼
     Google Gemini API
     (free tier — 1,500 req/day)
```

---

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (used for package management)
- VSCode with the **GitHub Copilot** and **GitHub Copilot Chat** extensions
- A free Google Gemini API key — get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (no credit card required)

---

## Setup

**1. Clone and install dependencies:**

```bash
git clone <repo-url>
cd copilot-gateway
uv pip install -r requirements.txt
```

**2. Create your `.env` file:**

```bash
cp .env.example .env
```

Edit `.env` and paste your Gemini API key:

```
GOOGLE_API_KEY=your_key_here
```

**3. Start the gateway:**

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

The server runs at `http://127.0.0.1:8080`.

---

## Verify the gateway is working

Before connecting VSCode, confirm the two endpoints respond correctly:

**Model discovery:**
```bash
curl http://127.0.0.1:8080/v1/models
```
Expected output:
```json
{"object": "list", "data": [{"id": "gemini-2.5-flash", ...}]}
```

**Chat ping:**
```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.5-flash","messages":[{"role":"user","content":"say hello"}],"stream":false}'
```
Expected: a JSON response with Gemini's answer in `choices[0].message.content`.

---

## Connect to VSCode Copilot

**Option A — UI (recommended):**

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run **"Chat: Manage Language Models"**
3. Click **Add Models** → **Custom Endpoint**
4. Fill in:
   - **Base URL:** `http://127.0.0.1:8080/v1`
   - **API type:** Chat Completions
   - **API key:** any string (e.g. `dummy`)
5. `gemini-2.5-flash` should appear in the model picker automatically.

**Option B — settings.json (fallback if Option A doesn't show the model):**

Add this to your VSCode `settings.json`:

```json
"github.copilot.chat.customOAIModels": {
  "gemini-2.5-flash": {
    "name": "Gemini 2.5 Flash (Gateway)",
    "url": "http://127.0.0.1:8080/v1/chat/completions",
    "toolCalling": true,
    "maxInputTokens": 128000,
    "maxOutputTokens": 8000
  }
}
```

---

## Using it

1. Make sure the gateway server is running (`uv run uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload`)
2. Open Copilot Chat in VSCode (`Ctrl+Alt+I`)
3. Select **gemini-2.5-flash** from the model picker
4. Ask a question about your code — the answer comes through your gateway from Gemini

Agent mode works the same way — select the model and switch to Agent mode in the chat panel.

---

## Project structure

```
app/
├── main.py                          # FastAPI service (GET /v1/models, POST /v1/chat/completions)
└── scripts/
    └── dynamic-vendor-selection.py  # Original prototype (reference only)
requirements.txt                     # Python dependencies
.env.example                         # API key template
```

---

## Roadmap

- [ ] Multi-vendor fallback (Groq → Cerebras → OpenRouter → Gemini)
- [ ] Agent-mode tool-calling round-trip polish
- [ ] API key authentication on the gateway
- [ ] Docker / systemd service for auto-start
