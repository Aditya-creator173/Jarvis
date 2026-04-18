<div align="center">
  <h1>JARVIS</h1>
  <p><strong>Offline-First Personal AI Operator — Actually Useful</strong></p>

  [![Offline First](https://img.shields.io/badge/Feature-Offline_First-00e5c8.svg)](#)
  [![Qwen2.5-Coder](https://img.shields.io/badge/Model-Qwen2.5__Coder-blue)](#)
  [![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange)](#)
  [![Whisper STT](https://img.shields.io/badge/STT-Whisper-green)](#)
  [![Kokoro TTS](https://img.shields.io/badge/TTS-Kokoro-blueviolet)](#)
  [![SQLite Memory](https://img.shields.io/badge/Memory-SQLite-lightgrey)](#)
  [![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](#)
</div>

<br>

> **⚠️ Brutal Truth**
>
> *"Most Jarvis projects fail because they stop at voice input + LLM response. Execution is the hard part. This project is built around that reality — every design decision prioritizes actual task completion over impressive demos."*

---

## 01 — Overview: An agent that acts, not just talks.

Jarvis is a locally-running AI operator that accepts voice or CLI commands, uses a Qwen language model to plan actions, and executes those actions against your real filesystem, shell, and codebase — all offline, all on your machine, with no data leaving your device unless you explicitly ask for it.

It maintains persistent memory across sessions (episodic + semantic), learns your preferences, and becomes more useful the more you use it. Think of it as a terminal that understands English and takes initiative.

---

## 02 — Architecture: Five layers. Zero cloud dependencies.

Jarvis is composed of five clean layers. Each has a single responsibility and can be replaced or upgraded independently.

| Layer | Component | Description | Under the Hood |
| :--- | :--- | :--- | :--- |
| **01** | **Input Layer** | Captures user intent from voice or CLI text. Normalizes input before passing to the brain. | `faster-whisper`, `sounddevice`, `argparse` |
| **02** | **Brain Layer** | Qwen2.5-Coder via Ollama reasons about intent and produces structured tool calls through a state machine. | `ollama`, `langgraph`, `langchain-ollama` |
| **03** | **Execution Layer** | 8 tool modules that run real operations: file I/O, shell commands, code execution, web fetch. | `subprocess`, `pathlib`, `httpx` |
| **04** | **Memory Layer** | SQLite stores episodic history. Top-k memories inject into every prompt. | `sqlite3`, `sentence-transformers`, `numpy` |
| **05** | **Output Layer** | Kokoro TTS converts responses to natural speech. Rich renders beautiful CLI output. | `kokoro`, `sounddevice`, `rich` |

---

## 03 — Agent Loop: A state machine, not a black box.

Unlike free-form ReAct loops that hallucinate their way through tasks, Jarvis uses a deterministic LangGraph state graph. Every transition is inspectable and testable.

* 🦻 **HEAR (listen):** Captures audio via Whisper or reads CLI input. Returns a clean utterance string.
* 🧠 **PLAN (plan):** Sends the utterance + memory context + tool list to Qwen. Extracts a structured JSON tool call or direct response.
* ⚡ **RUN (execute):** Routes the tool call to the correct module. Runs it. Flags destructive operations for confirmation.
* 🔄 **LOOP (reflect):** Is the task done? If yes → respond. If not → plan again. Auto-retries failures up to 3 times.
* 💬 **TALK (respond):** Formats the final response. CLI gets a Rich panel. Voice mode routes to Kokoro TTS.

---

## 04 — Technology Stack: Every decision is intentional.

| Layer | Technology | Version | Why This Choice |
| :--- | :--- | :--- | :--- |
| **LLM Runtime** | Ollama | Latest | One-command local model management. REST API works like the cloud. |
| **Primary Model** | Qwen2.5-Coder 7B | Q4_K_M | Best-in-class code + reasoning at 7B. Fits 8GB RAM. |
| **Agent Framework** | LangGraph | 0.2.x | Deterministic state graph. Inspectable, testable, async-safe. |
| **Speech-to-Text** | faster-whisper | 1.x | CTranslate2 backend. 4–5× faster than openai-whisper. |
| **Text-to-Speech** | Kokoro-82M | Latest | 82M param model. Natural prosody. Runs fully on CPU. |
| **Memory DB** | SQLite | Built-in | Zero dependency. ACID. File-portable. |
| **Embeddings** | sentence-transformers | 3.x | all-MiniLM-L6-v2: Fast, accurate enough for local retrieval. |
| **CLI UI** | Rich | 13.x | Tables, panels, spinners. Makes the terminal feel alive. |
| **Config** | TOML (tomllib) | Built-in | Typed, readable, no external dep. No YAML ambiguity. |
| **Packaging** | uv | Latest | 10–100× faster than pip. Lockfile-based environments. |

---

## 05 — Tool Modules: Real actions. No faking it.

Every tool is a Python module inheriting from `BaseTool`. New tools can be added without touching core code.

* 📁 **fs_tool:** Read, write, list, copy, move, delete files. Destructive ops require confirmation. *(Offline)*
* 💻 **shell_tool:** Execute bash commands. Captures stdout+stderr. Enforced allowlist. *(Offline)*
* 📝 **code_tool:** Scaffold files, run Python scripts, lint with ruff, format code. *(Offline)*
* 🧠 **memory_tool:** Store facts semantically. Recall by natural language query. *(Offline)*
* ✅ **task_tool:** Full CRUD task management in SQLite. Plain SQL — no ORM. *(Offline)*
* 🔍 **search_tool:** Semantic search over memories or full-text grep across files. *(Offline)*
* 🌐 **web_tool:** Fetch a URL or search DuckDuckGo. Escalation-only. *(Online Only)*

---

## 06 — Quick Start: Zero to running in 5 commands.

```bash
# 1. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Ollama and pull the model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b

# 3. Clone and install dependencies
git clone https://github.com/you/jarvis && cd jarvis
uv sync

# 4. Run CLI mode
uv run python -m jarvis --mode cli

# 5. Or voice mode (requires microphone)
uv run python -m jarvis --mode voice
```

---

## 07 — Known Risks: We know what can go wrong.

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Structured JSON output from Qwen drifts** | High | High | Regex fallback parser + Ollama JSON mode + adversarial tests. |
| **Voice latency too high on CPU-only machines** | Med | High | Profile early, int8 Whisper quant, `--no-voice` fallback available. |
| **Shell tool executes destructive command** | Med | Critical | Allowlist, `confirm=True` gate, `--safe-mode` flag. |
| **Kokoro TTS not available cross-platform** | Med | Med | `speak()` falls back silently to `print()` — voice failure never crashes agent. |
| **LangGraph API breaks between minor versions** | Low | Med | Version pinned in `pyproject.toml`. |

<br>
<div align="center">
  <p><i>Built for Iris OS Vision &bull; No cloud. No excuses.</i></p>
</div>
