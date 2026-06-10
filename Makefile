.PHONY: install install-dev test lint format clean build docker-build docker-run web

# 安装
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# 测试
test:
	pytest tests/ -v --cov=llm_match_pro --cov-report=term-missing

test-html:
	pytest tests/ -v --cov=llm_match_pro --cov-report=html

# 代码质量
lint:
	ruff check llm_match_pro/ tests/
	mypy llm_match_pro/

format:
	black llm_match_pro/ tests/
	ruff check --fix llm_match_pro/ tests/

# 清理
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# 构建
build: clean
	python -m build

# PyInstaller打包
build-exe:
	pyinstaller --onefile --name llm-match-pro \
		--add-data "llm_match_pro:llm_match_pro" \
		--hidden-import llm_match_pro.cli \
		llm_match_pro/cli.py

# Docker
docker-build:
	docker build -t llm-match-pro:latest .

docker-run:
	docker run -it --rm llm-match-pro:latest

docker-web:
	docker run -it --rm -p 8501:8501 llm-match-pro:latest web

# Web UI
web:
	streamlit run llm_match_pro/web.py

# CLI命令
cli-detect:
	python -m llm_match_pro.cli detect

cli-recommend:
	python -m llm_match_pro.cli recommend

cli-models:
	python -m llm_match_pro.cli models

# 帮助
help:
	@echo "LLM-Match-Pro Makefile 命令列表"
	@echo ""
	@echo "  install      - 安装项目"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理构建文件"
	@echo "  build        - 构建Python包"
	@echo "  build-exe    - 构建可执行文件"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run   - 运行Docker容器"
	@echo "  web          - 启动Web UI"
	@echo "  cli-detect   - 检测硬件"
	@echo "  cli-recommend- 推荐模型"
