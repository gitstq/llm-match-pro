<div align="center">

# 🤖 LLM-Match-Pro

**智能本地LLM硬體匹配與推薦引擎**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-24%20passing-brightgreen)](tests/)
[![CLI](https://img.shields.io/badge/CLI-Typer-orange)](https://typer.tiangolo.com/)
[![WebUI](https://img.shields.io/badge/WebUI-Streamlit-red)](https://streamlit.io/)

[简体中文](README.md) | [English](README_EN.md)

</div>

---

## 🎉 專案介紹

**LLM-Match-Pro** 是一款智能本地大語言模型（LLM）硬體匹配與推薦引擎。它能夠自動檢測你的硬體配置（GPU/CPU/記憶體），並從預置的模型資料庫中智能推薦最適合你設備運行的本地LLM模型。

### 為什麼選擇 LLM-Match-Pro？

- 🎯 **中文模型優先** — 內置18+主流中文模型（DeepSeek、Qwen、ChatGLM、Baichuan、Yi）
- 🇨🇳 **國產GPU支援** — 支援昇騰（Ascend）、摩爾線程（Moore Threads）等國產顯卡
- 🧠 **智能量化推薦** — 根據你的顯存自動推薦最佳量化方案（Q2_K ~ FP16）
- 📊 **可視化分析** — Web UI提供雷達圖、柱狀圖等直觀對比
- 🚀 **一鍵啟動命令** — 自動生成 llama.cpp / Ollama / vLLM / Docker 啟動命令

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **自動硬體檢測** | 自動識別 NVIDIA / AMD / 昇騰 / 摩爾線程 GPU |
| 📚 **豐富模型庫** | 18+ 預置模型，覆蓋 6B ~ 72B 參數規模 |
| 🎚️ **智能量化** | 支援 13 種量化方案，自動推薦最佳配置 |
| 📈 **性能預估** | 預估推理速度（tokens/s）、VRAM佔用 |
| 💻 **CLI + Web** | 命令行工具 + Streamlit Web 界面雙模式 |
| 🐳 **Docker支援** | 一鍵 Docker 部署，開箱即用 |
| 🧪 **完整測試** | 24 個單元測試，覆蓋率 >90% |

---

## 🚀 快速開始

### 安裝

```bash
# 從源碼安裝
git clone https://github.com/gitstq/llm-match-pro.git
cd llm-match-pro
pip install -e ".[dev]"
```

### CLI 使用

```bash
# 檢測硬體
llm-match-pro detect

# 推薦模型
llm-match-pro recommend

# 查看模型列表
llm-match-pro models

# 獲取升級建議
llm-match-pro upgrade

# 生成啟動命令
llm-match-pro launch Qwen/Qwen2.5-7B-Instruct --quant Q4_K_M
```

### Web UI 使用

```bash
# 啟動 Web 界面
llm-match-web

# 或
streamlit run llm_match_pro/web.py
```

然後訪問 http://localhost:8501

### Docker 使用

```bash
# 構建鏡像
docker build -t llm-match-pro .

# 運行 CLI
docker run -it --rm llm-match-pro detect

# 運行 Web UI
docker run -it --rm -p 8501:8501 llm-match-pro web
```

---

## 📖 詳細使用指南

### 硬體檢測

```bash
$ llm-match-pro detect

🔍 正在檢測硬體資訊...

┌─────────┬─────────────────────────────┬──────────┬─────────┬────────────────┐
│ 序號    │ 名稱                        │ 廠商     │ 顯存    │ 驅動           │
├─────────┼─────────────────────────────┼──────────┼─────────┼────────────────┤
│ 1       │ NVIDIA GeForce RTX 4090     │ NVIDIA   │ 24.0 GB │ 535.104.05     │
└─────────┴─────────────────────────────┴──────────┴─────────┴────────────────┘
```

### 模型推薦

```bash
$ llm-match-pro recommend --top-k 5 --lang zh

🤖 LLM-Match-Pro 智能推薦

┌──────┬────────────────────────┬──────────┬────────┬──────────┬──────────┬──────┬────────┐
│ 排名 │ 模型                   │ 參數量   │ 量化   │ VRAM     │ 速度     │ 評分 │ 狀態   │
├──────┼────────────────────────┼──────────┼────────┼──────────┼──────────┼──────┼────────┤
│ 1    │ Qwen2.5-7B-Instruct    │ 7.6B     │ Q4_K_M │ 4.5 GB   │ 35.2 t/s │ 92   │ ✓ 可   │
│ 2    │ DeepSeek-LLM-7B-Chat   │ 7.0B     │ Q4_K_M │ 4.2 GB   │ 38.5 t/s │ 90   │ ✓ 可   │
│ 3    │ ChatGLM3-6B            │ 6.0B     │ Q4_K_M │ 3.6 GB   │ 42.0 t/s │ 88   │ ✓ 可   │
└──────┴────────────────────────┴──────────┴────────┴──────────┴──────────┴──────┴────────┘
```

---

## 💡 設計思路與迭代規劃

### 架構設計

```
llm_match_pro/
├── hardware/      # 硬體檢測層
├── models/        # 模型資料庫層
├── engine/        # 推薦引擎層
├── config/        # 配置管理層
└── utils/         # 工具函數層
```

### 評分算法

綜合評分 = VRAM適配度(25%) + 性能評分(25%) + 質量評分(25%) + 兼容性評分(25%)

### 迭代規劃

- [x] v1.0.0 — 基礎功能：硬體檢測、模型推薦、CLI、Web UI
- [ ] v1.1.0 — ModelScope API 同步、線上模型搜索
- [ ] v1.2.0 — 基準測試數據自動更新
- [ ] v1.3.0 — VS Code 插件
- [ ] v2.0.0 — 分佈式推理推薦、多機多卡方案

---

## 🤝 貢獻指南

歡迎提交 Issue 和 PR！

1. Fork 本倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 創建 Pull Request

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<div align="center">

**Made with ❤️ by gitstq**

如果本專案對你有幫助，請給個 ⭐ Star！

</div>
