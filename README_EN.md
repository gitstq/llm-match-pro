<div align="center">

# 🤖 LLM-Match-Pro

**Smart Local LLM Hardware Matching & Recommendation Engine**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-24%20passing-brightgreen)](tests/)
[![CLI](https://img.shields.io/badge/CLI-Typer-orange)](https://typer.tiangolo.com/)
[![WebUI](https://img.shields.io/badge/WebUI-Streamlit-red)](https://streamlit.io/)

[简体中文](README.md) | [繁體中文](README_ZH_TW.md)

</div>

---

## 🎉 Introduction

**LLM-Match-Pro** is an intelligent local Large Language Model (LLM) hardware matching and recommendation engine. It automatically detects your hardware configuration (GPU/CPU/Memory) and intelligently recommends the most suitable local LLM models from a pre-built database.

### Why LLM-Match-Pro?

- 🎯 **Chinese Models Priority** — 18+ built-in mainstream Chinese models (DeepSeek, Qwen, ChatGLM, Baichuan, Yi)
- 🇨🇳 **Domestic GPU Support** — Supports Ascend, Moore Threads, and other domestic GPUs
- 🧠 **Smart Quantization** — Automatically recommends optimal quantization based on your VRAM (Q2_K ~ FP16)
- 📊 **Visual Analytics** — Web UI with radar charts, bar charts for intuitive comparison
- 🚀 **One-click Launch** — Auto-generates llama.cpp / Ollama / vLLM / Docker launch commands

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Auto Hardware Detection** | Auto-detect NVIDIA / AMD / Ascend / Moore Threads GPUs |
| 📚 **Rich Model Library** | 18+ pre-built models, covering 6B ~ 72B parameters |
| 🎚️ **Smart Quantization** | 13 quantization options with auto-recommendation |
| 📈 **Performance Estimation** | Predict inference speed (tokens/s), VRAM usage |
| 💻 **CLI + Web** | Command-line tool + Streamlit Web UI dual mode |
| 🐳 **Docker Support** | One-click Docker deployment |
| 🧪 **Full Tests** | 24 unit tests with >90% coverage |

---

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/gitstq/llm-match-pro.git
cd llm-match-pro
pip install -e ".[dev]"
```

### CLI Usage

```bash
# Detect hardware
llm-match-pro detect

# Recommend models
llm-match-pro recommend

# List supported models
llm-match-pro models

# Get upgrade advice
llm-match-pro upgrade

# Generate launch command
llm-match-pro launch Qwen/Qwen2.5-7B-Instruct --quant Q4_K_M
```

### Web UI

```bash
# Launch Web UI
llm-match-web

# Or
streamlit run llm_match_pro/web.py
```

Then visit http://localhost:8501

### Docker

```bash
# Build image
docker build -t llm-match-pro .

# Run CLI
docker run -it --rm llm-match-pro detect

# Run Web UI
docker run -it --rm -p 8501:8501 llm-match-pro web
```

---

## 📖 Detailed Guide

### Hardware Detection

```bash
$ llm-match-pro detect

🔍 Detecting hardware...

┌─────┬─────────────────────────┬────────┬────────┬────────────────┐
│ No. │ Name                    │ Vendor │ VRAM   │ Driver         │
├─────┼─────────────────────────┼────────┼────────┼────────────────┤
│ 1   │ NVIDIA GeForce RTX 4090 │ NVIDIA │ 24 GB  │ 535.104.05     │
└─────┴─────────────────────────┴────────┴────────┴────────────────┘
```

### Model Recommendation

```bash
$ llm-match-pro recommend --top-k 5 --lang en

🤖 LLM-Match-Pro Smart Recommendation

┌─────┬────────────────────────┬────────┬────────┬────────┬──────────┬──────┬────────┐
│ Rank│ Model                  │ Params │ Quant  │ VRAM   │ Speed    │ Score│ Status │
├─────┼────────────────────────┼────────┼────────┼────────┼──────────┼──────┼────────┤
│ 1   │ Llama-3.1-8B-Instruct│ 8.0B   │ Q4_K_M │ 4.8 GB │ 40.2 t/s │ 91   │ ✓ OK   │
│ 2   │ Mistral-7B-Instruct  │ 7.3B   │ Q4_K_M │ 4.4 GB │ 38.5 t/s │ 89   │ ✓ OK   │
└─────┴────────────────────────┴────────┴────────┴────────┴──────────┴──────┴────────┘
```

---

## 💡 Design & Roadmap

### Architecture

```
llm_match_pro/
├── hardware/      # Hardware detection layer
├── models/        # Model database layer
├── engine/        # Recommendation engine layer
├── config/        # Configuration management
└── utils/         # Utility functions
```

### Scoring Algorithm

Overall Score = VRAM Fit (25%) + Performance (25%) + Quality (25%) + Compatibility (25%)

### Roadmap

- [x] v1.0.0 — Basic features: hardware detection, model recommendation, CLI, Web UI
- [ ] v1.1.0 — ModelScope API sync, online model search
- [ ] v1.2.0 — Auto benchmark data updates
- [ ] v1.3.0 — VS Code extension
- [ ] v2.0.0 — Distributed inference recommendations

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by gitstq**

If this project helps you, please give it a ⭐ Star!

</div>
