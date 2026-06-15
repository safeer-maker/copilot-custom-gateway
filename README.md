Here is your complete, comprehensive `README.md` file for the project root, updated to reflect the dynamic model discovery architecture we just designed.

--

# Copilot Custom Gateway (`copilot-custom-gateway`)

An enterprise-grade, low-latency API proxy built with **Python FastAPI** and **LangChain**. This middleware translates standard GitHub Copilot Chat and Agent requests into compatible orchestrations for privately hosted custom Large Language Models (LLMs), bypassing public cloud infrastructure entirely.

Instead of relying on static, hardcoded configuration files, this gateway implements an open-ended **Dynamic Model Discovery Engine** (`/v1/models`). When Visual Studio Code initializes, it dynamically polls this proxy, automatically populating the Copilot model selection dropdown on the fly.

---

## Project Architecture

This repository establishes a Bring Your Own Key (BYOK) compliant local endpoint. It wraps your private models within an OpenAI-compatible API layer, allowing VS Code Chat and autonomous Copilot Agents to interact directly with your air-gapped system.

```
┌─────────────────┐             ┌────────────────────────┐             ┌─────────────────────┐
│  VS Code Chat   │  HTTP GET   │ Copilot Custom Gateway │  LangChain  │   Privately Hosted  │
│  & Agent Views  ├────────────►│   (FastAPI Proxy)      ├────────────►│   Inference Model   │
└─────────────────┘  /v1/...    └────────────────────────┘  Protocols  └─────────────────────┘

```

## Key Features

* **Dynamic Model Discovery:** Exposes a native `/v1/models` endpoint, allowing VS Code to auto-load your entire private model catalog dynamically.
* **OpenAI Compatibility Layer:** Emulates `/v1/chat/completions` supporting real-time Server-Sent Events (SSE) token streaming.
* **Agent Tool-Calling Enabled:** Forwards structural payload signatures (`toolCalling: true`) to ensure Copilot Agent views can execute multi-step workspace tasks seamlessly.
* **LangChain Orchestration:** Easily swap underlying inference backends (HuggingFace, vLLM, local Ollama nodes, or proprietary clusters) based on the incoming model parameter.
* **Stateless & High-Performance:** Engineered over FastAPI's async event loop for sub-millisecond translation overhead.

---

## Quick Start

### 1. Prerequisites

* Python 3.10 or higher
* VS Code (with GitHub Copilot and Copilot Chat extensions active)

### 2. Installation

Clone the repository and install dependencies:

```bash
cd copilot-custom-gateway
pip install -r requirements.txt

```

### 3. Running the Gateway

Launch the Uvicorn high-performance ASGI server:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

```

The gateway will initialize and listen natively on `[http://127.0.0.1:8080](http://127.0.0.1:8080)`.

---

## Client Configurations

To connect your VS Code environment to this private infrastructure, you must register the endpoint within your user profile's language model registry.

### Step 1: Open the Custom Registry

1. Launch VS Code.
2. Open the **Command Palette** using `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS).
3. Type and execute: **Chat: Manage Language Models**.
4. Select **Add Models** and choose **Custom Endpoint** from the dropdown option list.

This action instructs VS Code to automatically create and open your user profile's hidden `chatLanguageModels.json` configuration file.

### Step 2: Inject the Dynamic Model Definition Block

Replace or append the content within your `chatLanguageModels.json` file with the following technical schema declaration:

```json
[
  {
    "name": "Local Gateway (Dynamic)",
    "vendor": "openai", 
    "apiType": "chat-completions",
    "apiKey": "ccg_live_7efda921bc4d390a8f8e0d1b3c5a6f7e80123456789abcdef",
    "url": "http://127.0.0.1:8080/v1"
  }
]

```
    
#### Critical Configuration Details:

* `vendor: "openai"`: Setting this vendor type signals to VS Code that it shouldn't look for a static list. Instead, it instructs the IDE to run a background handshake request directly to your `url/models` route.
* `url`: Explicitly points to your running FastAPI server base path.
* `apiKey`: The private, secure access token mapped to your custom gateway environment logic.

### Step 3: Verify Integration

1. Restart or reload your VS Code window (`Developer: Reload Window` via the Command Palette).
2. Open the **Copilot Chat Panel** (`Ctrl+Alt+I` or `Cmd+Ctrl+I`) or the **Agent View**.
3. Click on the model selection dropdown header (located next to the chat input area).
4. You will see your local model catalog auto-populated dynamically straight from your server! Select your desired model, and your threads will now route 100% locally through your gateway proxy.