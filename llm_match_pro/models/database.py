"""模型数据库模块"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class ModelInfo:
    """模型信息"""
    id: str
    name: str
    description: str = ""
    params_billion: float = 0.0
    context_length: int = 4096
    quantization: str = "fp16"
    vram_required_mb: float = 0.0
    tags: List[str] = field(default_factory=list)
    source: str = "huggingface"  # huggingface / modelscope
    source_url: str = ""
    license: str = ""
    language: str = "en"  # en / zh / multilingual
    architecture: str = ""
    is_chat_model: bool = True
    benchmarks: Dict[str, float] = field(default_factory=dict)
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        return cls(**data)


class ModelDatabase:
    """模型数据库"""

    # 预置模型数据（中文模型优先）
    DEFAULT_MODELS = [
        # DeepSeek系列
        ModelInfo(
            id="deepseek-ai/deepseek-llm-7b-chat",
            name="DeepSeek-LLM-7B-Chat",
            description="DeepSeek 7B对话模型，中文表现优秀",
            params_billion=7.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=14000,
            tags=["deepseek", "chat", "chinese", "7b"],
            source="huggingface",
            source_url="https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat",
            license="deepseek-license",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 68.9, "cmmlu": 71.5, "mmlu": 63.8},
        ),
        ModelInfo(
            id="deepseek-ai/deepseek-llm-67b-chat",
            name="DeepSeek-LLM-67B-Chat",
            description="DeepSeek 67B大模型，中文推理能力强",
            params_billion=67.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=134000,
            tags=["deepseek", "chat", "chinese", "67b"],
            source="huggingface",
            source_url="https://huggingface.co/deepseek-ai/deepseek-llm-67b-chat",
            license="deepseek-license",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 71.1, "cmmlu": 75.0, "mmlu": 71.1},
        ),
        # Qwen系列
        ModelInfo(
            id="Qwen/Qwen2.5-7B-Instruct",
            name="Qwen2.5-7B-Instruct",
            description="阿里通义千问2.5 7B指令模型",
            params_billion=7.6,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=16000,
            tags=["qwen", "chat", "chinese", "7b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
            license="apache-2.0",
            language="zh",
            architecture="qwen2",
            is_chat_model=True,
            benchmarks={"ceval": 83.5, "cmmlu": 86.0, "mmlu": 74.2},
        ),
        ModelInfo(
            id="Qwen/Qwen2.5-14B-Instruct",
            name="Qwen2.5-14B-Instruct",
            description="阿里通义千问2.5 14B指令模型",
            params_billion=14.7,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=30000,
            tags=["qwen", "chat", "chinese", "14b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen2.5-14B-Instruct",
            license="apache-2.0",
            language="zh",
            architecture="qwen2",
            is_chat_model=True,
            benchmarks={"ceval": 86.1, "cmmlu": 88.5, "mmlu": 79.5},
        ),
        ModelInfo(
            id="Qwen/Qwen2.5-32B-Instruct",
            name="Qwen2.5-32B-Instruct",
            description="阿里通义千问2.5 32B指令模型",
            params_billion=32.5,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=66000,
            tags=["qwen", "chat", "chinese", "32b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen2.5-32B-Instruct",
            license="apache-2.0",
            language="zh",
            architecture="qwen2",
            is_chat_model=True,
            benchmarks={"ceval": 88.3, "cmmlu": 90.1, "mmlu": 83.5},
        ),
        ModelInfo(
            id="Qwen/Qwen2.5-72B-Instruct",
            name="Qwen2.5-72B-Instruct",
            description="阿里通义千问2.5 72B指令模型",
            params_billion=72.7,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=147000,
            tags=["qwen", "chat", "chinese", "72b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen2.5-72B-Instruct",
            license="apache-2.0",
            language="zh",
            architecture="qwen2",
            is_chat_model=True,
            benchmarks={"ceval": 89.5, "cmmlu": 91.2, "mmlu": 85.3},
        ),
        # ChatGLM系列
        ModelInfo(
            id="THUDM/chatglm3-6b",
            name="ChatGLM3-6B",
            description="清华ChatGLM3 6B对话模型",
            params_billion=6.0,
            context_length=8192,
            quantization="fp16",
            vram_required_mb=13000,
            tags=["chatglm", "chat", "chinese", "6b"],
            source="huggingface",
            source_url="https://huggingface.co/THUDM/chatglm3-6b",
            license="chatglm-license",
            language="zh",
            architecture="glm",
            is_chat_model=True,
            benchmarks={"ceval": 69.0, "cmmlu": 71.0, "mmlu": 66.1},
        ),
        ModelInfo(
            id="THUDM/glm-4-9b-chat",
            name="GLM-4-9B-Chat",
            description="清华GLM-4 9B对话模型，新一代架构",
            params_billion=9.0,
            context_length=131072,
            quantization="fp16",
            vram_required_mb=19000,
            tags=["glm", "chat", "chinese", "9b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/THUDM/glm-4-9b-chat",
            license="chatglm-license",
            language="zh",
            architecture="glm-4",
            is_chat_model=True,
            benchmarks={"ceval": 74.7, "cmmlu": 77.1, "mmlu": 72.4},
        ),
        # Baichuan系列
        ModelInfo(
            id="baichuan-inc/Baichuan2-7B-Chat",
            name="Baichuan2-7B-Chat",
            description="百川智能Baichuan2 7B对话模型",
            params_billion=7.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=14000,
            tags=["baichuan", "chat", "chinese", "7b"],
            source="huggingface",
            source_url="https://huggingface.co/baichuan-inc/Baichuan2-7B-Chat",
            license="baichuan-license",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 67.3, "cmmlu": 69.8, "mmlu": 62.0},
        ),
        ModelInfo(
            id="baichuan-inc/Baichuan2-13B-Chat",
            name="Baichuan2-13B-Chat",
            description="百川智能Baichuan2 13B对话模型",
            params_billion=13.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=27000,
            tags=["baichuan", "chat", "chinese", "13b"],
            source="huggingface",
            source_url="https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat",
            license="baichuan-license",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 71.8, "cmmlu": 73.5, "mmlu": 67.5},
        ),
        # Yi系列
        ModelInfo(
            id="01-ai/Yi-1.5-6B-Chat",
            name="Yi-1.5-6B-Chat",
            description="零一万物Yi-1.5 6B对话模型",
            params_billion=6.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=12000,
            tags=["yi", "chat", "chinese", "6b"],
            source="huggingface",
            source_url="https://huggingface.co/01-ai/Yi-1.5-6B-Chat",
            license="apache-2.0",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 71.5, "cmmlu": 73.2, "mmlu": 65.8},
        ),
        ModelInfo(
            id="01-ai/Yi-1.5-34B-Chat",
            name="Yi-1.5-34B-Chat",
            description="零一万物Yi-1.5 34B对话模型",
            params_billion=34.0,
            context_length=4096,
            quantization="fp16",
            vram_required_mb=69000,
            tags=["yi", "chat", "chinese", "34b"],
            source="huggingface",
            source_url="https://huggingface.co/01-ai/Yi-1.5-34B-Chat",
            license="apache-2.0",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"ceval": 82.2, "cmmlu": 84.5, "mmlu": 76.8},
        ),
        # Llama系列（国际主流）
        ModelInfo(
            id="meta-llama/Meta-Llama-3.1-8B-Instruct",
            name="Llama-3.1-8B-Instruct",
            description="Meta Llama 3.1 8B指令模型",
            params_billion=8.0,
            context_length=128000,
            quantization="fp16",
            vram_required_mb=16000,
            tags=["llama", "chat", "english", "8b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct",
            license="llama3.1",
            language="en",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"mmlu": 73.0, "hellaswag": 79.3, "arc_challenge": 62.5},
        ),
        ModelInfo(
            id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            name="Llama-3.1-70B-Instruct",
            description="Meta Llama 3.1 70B指令模型",
            params_billion=70.0,
            context_length=128000,
            quantization="fp16",
            vram_required_mb=141000,
            tags=["llama", "chat", "english", "70b", "long-context"],
            source="huggingface",
            source_url="https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct",
            license="llama3.1",
            language="en",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"mmlu": 86.0, "hellaswag": 88.0, "arc_challenge": 71.5},
        ),
        # Mistral系列
        ModelInfo(
            id="mistralai/Mistral-7B-Instruct-v0.3",
            name="Mistral-7B-Instruct-v0.3",
            description="Mistral 7B指令模型v0.3",
            params_billion=7.3,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=15000,
            tags=["mistral", "chat", "english", "7b"],
            source="huggingface",
            source_url="https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3",
            license="apache-2.0",
            language="en",
            architecture="mistral",
            is_chat_model=True,
            benchmarks={"mmlu": 62.5, "hellaswag": 83.5, "arc_challenge": 60.5},
        ),
        ModelInfo(
            id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            name="Mixtral-8x7B-Instruct",
            description="Mistral Mixtral 8x7B MoE指令模型",
            params_billion=46.7,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=96000,
            tags=["mistral", "chat", "english", "moe", "47b"],
            source="huggingface",
            source_url="https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1",
            license="apache-2.0",
            language="en",
            architecture="mixtral",
            is_chat_model=True,
            benchmarks={"mmlu": 70.6, "hellaswag": 87.5, "arc_challenge": 64.5},
        ),
        # Code模型
        ModelInfo(
            id="deepseek-ai/deepseek-coder-6.7b-instruct",
            name="DeepSeek-Coder-6.7B-Instruct",
            description="DeepSeek代码模型6.7B",
            params_billion=6.7,
            context_length=16384,
            quantization="fp16",
            vram_required_mb=14000,
            tags=["deepseek", "code", "chinese", "6.7b"],
            source="huggingface",
            source_url="https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct",
            license="deepseek-license",
            language="zh",
            architecture="llama",
            is_chat_model=True,
            benchmarks={"humaneval": 47.0, "mbpp": 58.0},
        ),
        ModelInfo(
            id="Qwen/Qwen2.5-Coder-7B-Instruct",
            name="Qwen2.5-Coder-7B-Instruct",
            description="阿里通义千问代码模型7B",
            params_billion=7.6,
            context_length=32768,
            quantization="fp16",
            vram_required_mb=16000,
            tags=["qwen", "code", "chinese", "7b"],
            source="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct",
            license="apache-2.0",
            language="zh",
            architecture="qwen2",
            is_chat_model=True,
            benchmarks={"humaneval": 54.3, "mbpp": 65.2},
        ),
    ]

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".llm_match_pro" / "models_db.json"
        self.models: Dict[str, ModelInfo] = {}
        self._load()

    def _load(self) -> None:
        """加载模型数据库"""
        self.models = {}

        # 加载预置模型
        for model in self.DEFAULT_MODELS:
            self.models[model.id] = model

        # 加载用户自定义模型
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for model_id, model_data in data.items():
                        if model_id not in self.models:
                            self.models[model_id] = ModelInfo.from_dict(model_data)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

    def save(self) -> None:
        """保存模型数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        data = {model_id: model.to_dict() for model_id, model in self.models.items()}
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        return self.models.get(model_id)

    def list_models(
        self,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None,
        min_params: Optional[float] = None,
        max_params: Optional[float] = None,
    ) -> List[ModelInfo]:
        """列出模型"""
        result = list(self.models.values())

        if tags:
            result = [m for m in result if any(t in m.tags for t in tags)]

        if language:
            result = [m for m in result if m.language == language]

        if min_params is not None:
            result = [m for m in result if m.params_billion >= min_params]

        if max_params is not None:
            result = [m for m in result if m.params_billion <= max_params]

        return result

    def add_model(self, model: ModelInfo) -> None:
        """添加模型"""
        self.models[model.id] = model
        self.save()

    def remove_model(self, model_id: str) -> bool:
        """移除模型"""
        if model_id in self.models:
            del self.models[model_id]
            self.save()
            return True
        return False

    def get_quantized_variants(self, model_id: str) -> List[ModelInfo]:
        """获取模型的量化变体"""
        base_model = self.get_model(model_id)
        if not base_model:
            return []

        quantizations = ["Q4_K_M", "Q5_K_M", "Q8_0", "Q4_0", "Q6_K"]
        variants = []

        for quant in quantizations:
            from .estimator import VRAMEstimator
            estimator = VRAMEstimator()
            vram = estimator.estimate(base_model.params_billion, quant, base_model.context_length)

            variant = ModelInfo(
                id=f"{model_id}-{quant.lower()}",
                name=f"{base_model.name}-{quant}",
                description=f"{base_model.description} ({quant}量化)",
                params_billion=base_model.params_billion,
                context_length=base_model.context_length,
                quantization=quant,
                vram_required_mb=vram,
                tags=base_model.tags + [quant.lower(), "quantized"],
                source=base_model.source,
                source_url=base_model.source_url,
                license=base_model.license,
                language=base_model.language,
                architecture=base_model.architecture,
                is_chat_model=base_model.is_chat_model,
                benchmarks=base_model.benchmarks,
            )
            variants.append(variant)

        return variants
