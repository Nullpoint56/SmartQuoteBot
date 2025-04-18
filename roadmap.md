# 🛣️ Project Roadmap

## Python code roadmap

### Current Version: 1.0

#### ✅ Features Implemented:
- Semantic similarity-based quote matching using MiniLM (via `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- FAISS-based cosine similarity index for real-time quote retrieval
- Lightweight in-memory quote metadata system
- JSON + FAISS index export pipeline
- Discord bot integration

---

### 📌 Version 1.1 — Custom Classifier (Next)

#### 🎯 Goals:
- Build and train a **custom text classification model** for Hungarian inputs
- Labels: `alcohol`, `suffering`, `none`
- Collect and annotate example sentences from real and synthetic sources
- Evaluate model performance (accuracy, precision, recall)
- Deploy classifier as a **prefilter** before semantic search to reduce unnecessary embedding runs

#### 💡 Benefits:
- Lower average latency for irrelevant messages
- Allows for targeted semantic search only when needed
- Opens path to custom moderation or tone-sensitive bots

---

### 📌 Version 1.2 — RKNN NPU Inference

#### 🎯 Goals:
- Optimize the MiniLM embedding model to run on the **RK3566 NPU** using **RKNN Toolkit 2**
- Convert MiniLM from ONNX to RKNN format (without quantization initially)
- Evaluate NPU inference performance (latency, consistency)
- Integrate RKNN runtime into the bot's inference pipeline
- Fall back to CPU if RKNN not available

#### 💡 Benefits:
- Dramatically faster inference (sub-50ms per message)
- Offloads CPU for other tasks
- Enables real-time responsiveness in busier environments

---

## CI/CD roadmap

### OrangePi
- NVME SSD upgrade
- RKNN OS support: https://www.xda-developers.com/how-i-used-the-npu-on-my-orange-pi-5-pro-to-run-llms/
