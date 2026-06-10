<div align="center">

# 🤖 LLM-Match-Pro

**智能本地LLM硬件匹配与推荐引擎**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-24%20passing-brightgreen)](tests/)
[![CLI](https://img.shields.io/badge/CLI-Typer-orange)](https://typer.tiangolo.com/)
[![WebUI](https://img.shields.io/badge/WebUI-Streamlit-red)](https://streamlit.io/)

[English](README_EN.md) | [繁體中文](README_ZH_TW.md)

</div>

---

## 🎉 项目介绍

**LLM-Match-Pro** 是一款智能本地大语言模型（LLM）硬件匹配与推荐引擎。它能够自动检测你的硬件配置（GPU/CPU/内存），并从预置的模型数据库中智能推荐最适合你设备运行的本地LLM模型。

### 为什么选择 LLM-Match-Pro？

- 🎯 **中文模型优先** — 内置18+主流中文模型（DeepSeek、Qwen、ChatGLM、Baichuan、Yi）
- 🇨🇳 **国产GPU支持** — 支持昇腾（Ascend）、摩尔线程（Moore Threads）等国产显卡
- 🧠 **智能量化推荐** — 根据你的显存自动推荐最佳量化方案（Q2_K ~ FP16）
- 📊 **可视化分析** — Web UI提供雷达图、柱状图等直观对比
- 🚀 **一键启动命令** — 自动生成 llama.cpp / Ollama / vLLM / Docker 启动命令

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **自动硬件检测** | 自动识别 NVIDIA / AMD / 昇腾 / 摩尔线程 GPU |
| 📚 **丰富模型库** | 18+ 预置模型，覆盖 6B ~ 72B 参数规模 |
| 🎚️ **智能量化** | 支持 13 种量化方案，自动推荐最佳配置 |
| 📈 **性能预估** | 预估推理速度（tokens/s）、VRAM占用 |
| 💻 **CLI + Web** | 命令行工具 + Streamlit Web 界面双模式 |
| 🐳 **Docker支持** | 一键 Docker 部署，开箱即用 |
| 🧪 **完整测试** | 24 个单元测试，覆盖率 >90% |

---

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装（即将发布）
pip install llm-match-pro

# 或从源码安装
git clone https://github.com/gitstq/llm-match-pro.git
cd llm-match-pro
pip install -e ".[dev]"
```

### CLI 使用

```bash
# 检测硬件
llm-match-pro detect

# 推荐模型
llm-match-pro recommend

# 查看模型列表
llm-match-pro models

# 获取升级建议
llm-match-pro upgrade

# 生成启动命令
llm-match-pro launch Qwen/Qwen2.5-7B-Instruct --quant Q4_K_M
```

### Web UI 使用

```bash
# 启动 Web 界面
llm-match-web

# 或
streamlit run llm_match_pro/web.py
```

然后访问 http://localhost:8501

### Docker 使用

```bash
# 构建镜像
docker build -t llm-match-pro .

# 运行 CLI
docker run -it --rm llm-match-pro detect

# 运行 Web UI
docker run -it --rm -p 8501:8501 llm-match-pro web
```

---

## 📖 详细使用指南

### 硬件检测

```bash
$ llm-match-pro detect

🔍 正在检测硬件信息...

┌─────────┬─────────────────────────────┬──────────┬─────────┬────────────────┐
│ 序号    │ 名称                        │ 厂商     │ 显存    │ 驱动           │
├─────────┼─────────────────────────────┼──────────┼─────────┼────────────────┤
│ 1       │ NVIDIA GeForce RTX 4090     │ NVIDIA   │ 24.0 GB │ 535.104.05     │
└─────────┴─────────────────────────────┴──────────┴─────────┴────────────────┘
```

### 模型推荐

```bash
$ llm-match-pro recommend --top-k 5 --lang zh

🤖 LLM-Match-Pro 智能推荐

┌──────┬────────────────────────┬──────────┬────────┬──────────┬──────────┬──────┬────────┐
│ 排名 │ 模型                   │ 参数量   │ 量化   │ VRAM     │ 速度     │ 评分 │ 状态   │
├──────┼────────────────────────┼──────────┼────────┼──────────┼──────────┼──────┼────────┤
│ 1    │ Qwen2.5-7B-Instruct    │ 7.6B     │ Q4_K_M │ 4.5 GB   │ 35.2 t/s │ 92   │ ✓ 可   │
│ 2    │ DeepSeek-LLM-7B-Chat   │ 7.0B     │ Q4_K_M │ 4.2 GB   │ 38.5 t/s │ 90   │ ✓ 可   │
│ 3    │ ChatGLM3-6B            │ 6.0B     │ Q4_K_M │ 3.6 GB   │ 42.0 t/s │ 88   │ ✓ 可   │
└──────┴────────────────────────┴──────────┴────────┴──────────┴──────────┴──────┴────────┘
```

### 支持的模型

| 系列 | 模型 | 参数量 | 上下文 | 语言 |
|------|------|--------|--------|------|
| DeepSeek | DeepSeek-LLM-7B/67B-Chat | 7B/67B | 4K | 中文 |
| Qwen | Qwen2.5-7B/14B/32B/72B-Instruct | 7.6B~72.7B | 32K | 中文 |
| ChatGLM | ChatGLM3-6B / GLM-4-9B-Chat | 6B/9B | 8K~128K | 中文 |
| Baichuan | Baichuan2-7B/13B-Chat | 7B/13B | 4K | 中文 |
| Yi | Yi-1.5-6B/34B-Chat | 6B/34B | 4K | 中文 |
| Llama | Llama-3.1-8B/70B-Instruct | 8B/70B | 128K | 英文 |
| Mistral | Mistral-7B / Mixtral-8x7B | 7B/47B | 32K | 英文 |

---

## 💡 设计思路与迭代规划

### 架构设计

```
llm_match_pro/
├── hardware/      # 硬件检测层
├── models/        # 模型数据库层
├── engine/        # 推荐引擎层
├── config/        # 配置管理层
└── utils/         # 工具函数层
```

### 评分算法

综合评分 = VRAM适配度(25%) + 性能评分(25%) + 质量评分(25%) + 兼容性评分(25%)

### 迭代规划

- [x] v1.0.0 — 基础功能：硬件检测、模型推荐、CLI、Web UI
- [ ] v1.1.0 — ModelScope API 同步、在线模型搜索
- [ ] v1.2.0 — 基准测试数据自动更新
- [ ] v1.3.0 — VS Code 插件
- [ ] v2.0.0 — 分布式推理推荐、多机多卡方案

---

## 📦 打包与部署指南

### 构建 Python 包

```bash
make build
```

### 构建可执行文件

```bash
make build-exe
```

### Docker 部署

```bash
make docker-build
make docker-run
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境

```bash
make install-dev
make test
make lint
make format
```

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

**Made with ❤️ by gitstq**

如果本项目对你有帮助，请给个 ⭐ Star！

</div>
