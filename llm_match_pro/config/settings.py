"""配置管理模块"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = Field(default="LLM-Match-Pro", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")

    # 数据源配置
    huggingface_api_url: str = Field(
        default="https://huggingface.co/api/models",
        description="HuggingFace API地址"
    )
    modelscope_api_url: str = Field(
        default="https://www.modelscope.cn/api/v1/dolphin/models",
        description="ModelScope API地址"
    )
    use_modelscope_mirror: bool = Field(
        default=True,
        description="是否优先使用ModelScope镜像"
    )

    # 模型数据库
    model_db_path: Path = Field(
        default=Path.home() / ".llm_match_pro" / "models_db.json",
        description="模型数据库路径"
    )
    cache_ttl_hours: int = Field(default=24, description="缓存过期时间(小时)")

    # 硬件检测
    enable_nvidia_gpu: bool = Field(default=True, description="启用NVIDIA GPU检测")
    enable_amd_gpu: bool = Field(default=True, description="启用AMD GPU检测")
    enable_ascend_gpu: bool = Field(default=True, description="启用昇腾GPU检测")
    enable_mthreads_gpu: bool = Field(default=True, description="启用摩尔线程GPU检测")

    # 推荐引擎
    default_quantization: str = Field(default="Q4_K_M", description="默认量化方案")
    vram_overhead_ratio: float = Field(default=1.15, description="VRAM预留比例")
    recommend_top_k: int = Field(default=10, description="推荐结果数量")

    # Web UI
    web_host: str = Field(default="0.0.0.0", description="Web服务主机")
    web_port: int = Field(default=8501, description="Web服务端口")

    class Config:
        env_prefix = "LLM_MATCH_"
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
