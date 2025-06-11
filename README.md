# SmartQuoteBot

SmartQuoteBot is a lightweight, intelligent Discord bot that listens for user messages, detects certain topics, and responds with a relevant quote from a curated database.  
Built for **efficiency**, **on-device AI inference**, and **minimal hosting costs**, it is designed to run smoothly even on low-power devices like the **Orange Pi 3B**.

---

## ✨ Features

- 🌟 **Lightweight AI detection**: Filters messages using a fast, on-device text classifier.
- 🔎 **Semantic quote matching**: Finds quotes similar to the message meaning when a topic match is detected.
- ⚡ **Low resource usage**: Optimized for ARM64 systems with optional RKNN NPU acceleration support.
- 🛠️ **Easy deployment**: Docker-based setup with multi-architecture builds (`linux/amd64` and `linux/arm64`).

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Nullpoint56/SmartQuoteBot.git
cd SmartQuoteBot
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and set your bot's token and settings:

```env
DISCORD_TOKEN=your-bot-token-here
BOT_PREFIX=!
```

### 3. Build and Run with Docker

```bash
docker build -t smartquotebot .
docker run --env-file .env smartquotebot
```

Or pull the prebuilt image from [Docker Hub](https://hub.docker.com/r/thomas934/rodof-bot).

---

## 🧹 Architecture Overview

| Component        | Description |
|------------------|-------------|
| **Classifier**    | Filters messages that may relate to specific topics such as "alcohol" or "suffering". |
| **Semantic Search** | Selects the most contextually relevant quote from a pre-tagged quote dataset. |
| **Discord Bot**   | Listens for messages, applies the classifier, and sends back appropriate responses. |
| **Docker Support** | Multi-platform builds for both x86 and ARM64 architectures. |

---

## 🧑‍💻 Local Development with `uv`

[`uv`](https://github.com/astral-sh/uv) is a fast Python package manager that replaces pip and pip-tools. This project uses `uv` exclusively to manage dependencies.

### 1. Install `uv`

#### 🖥️ Windows (via winget)

```bash
winget install --id=astral-sh.uv -e
```

#### 🌍 macOS / Linux / Other Platforms

Follow the official standalone installer instructions:
[https://docs.astral.sh/uv/getting-started/installation/#standalone-installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

### 2. Install project dependencies

```bash
uv pip install
```

> This reads directly from `pyproject.toml` and `uv.lock` to create a reproducible environment.

### 3. Run the development container with your current Git branch tag

Use the provided script to build and run the dev container based on the current Git branch:

```bash
uv run python scripts/dev_up.py
```

This will:

* Ask for your current branch name (e.g. `feature/login`)
* Sanitize the given Git branch name (e.g., `feature/login` → `feature-login`)
* Use it as the image tag (e.g., `thomas934/smart-quote-bot:feature-login`)
* Inject that tag into `docker-compose.override.yml`
* Start the container with live code mounting and logs

> 💡 **Note**: If you're not on the `master` or `dev` branch, the image will be tagged using your current branch name.

---

## 📦 Building for ARM64 (Orange Pi, Raspberry Pi)

The `Dockerfile` and GitHub Actions workflow support **multi-architecture builds**.

To manually build for ARM64:

```bash
docker buildx build --platform linux/arm64 -t smartquotebot-arm64 .
```

Alternatively, use the provided GitHub Actions workflow to auto-publish multi-architecture images.

---

## 📚 TODO / Roadmap

- [ ] Implement a custom classifier for improved detection
- [ ] Add support for slash commands (`/quote`)
- [ ] Enable customizable quote sets

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## ❤️ Acknowledgements

- [discord.py](https://github.com/Rapptz/discord.py) — Discord API library
- [scikit-learn](https://scikit-learn.org/) — Lightweight machine learning toolkit
- [sentence-transformers](https://www.sbert.net/) — Semantic similarity search

