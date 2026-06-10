"""通用工具函数"""

import platform
import sys
from typing import Dict, Any


def format_bytes(bytes_val: int) -> str:
    """将字节数格式化为人类可读字符串"""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 ** 2:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 ** 3:
        return f"{bytes_val / (1024 ** 2):.1f} MB"
    elif bytes_val < 1024 ** 4:
        return f"{bytes_val / (1024 ** 3):.1f} GB"
    else:
        return f"{bytes_val / (1024 ** 4):.1f} TB"


def format_vram(vram_mb: float) -> str:
    """格式化显存大小"""
    if vram_mb < 1024:
        return f"{vram_mb:.0f} MB"
    else:
        return f"{vram_mb / 1024:.1f} GB"


def get_platform_info() -> Dict[str, Any]:
    """获取平台信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
    }


def estimate_vram_requirement(
    params_billion: float,
    quantization: str = "fp16",
    context_length: int = 4096,
    batch_size: int = 1,
) -> float:
    """
    估算模型VRAM需求（MB）

    Args:
        params_billion: 模型参数量（十亿）
        quantization: 量化方案
        context_length: 上下文长度
        batch_size: 批大小

    Returns:
        预估VRAM需求（MB）
    """
    # 基础参数内存（每参数字节数）
    bytes_per_param = {
        "fp32": 4.0,
        "fp16": 2.0,
        "bf16": 2.0,
        "int8": 1.0,
        "Q8_0": 1.0,
        "Q6_K": 0.75,
        "Q5_K_M": 0.65,
        "Q5_K_S": 0.62,
        "Q4_K_M": 0.58,
        "Q4_K_S": 0.55,
        "Q4_0": 0.50,
        "Q3_K_M": 0.45,
        "Q3_K_S": 0.42,
        "Q2_K": 0.35,
        "awq": 0.45,
        "gptq": 0.45,
        "gguf_Q4": 0.58,
        "gguf_Q5": 0.65,
        "gguf_Q8": 1.0,
    }

    quant_lower = quantization.lower()
    # 支持小写查询
    bytes_per_param_lower = {k.lower(): v for k, v in bytes_per_param.items()}
    bpp = bytes_per_param_lower.get(quant_lower, 2.0)

    # 基础权重内存
    base_vram = params_billion * 1e9 * bpp / (1024 ** 2)

    # KV Cache估算 (每token约0.5-1MB per billion params)
    kv_cache_per_token = params_billion * 0.001  # MB per token
    kv_cache_total = kv_cache_per_token * context_length * batch_size

    # 激活值和开销
    activation_overhead = base_vram * 0.1

    # 总VRAM需求
    total_vram = base_vram + kv_cache_total + activation_overhead

    return total_vram
