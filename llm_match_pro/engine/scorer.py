"""匹配评分引擎"""

from dataclasses import dataclass
from typing import List, Dict, Any

from ..hardware.detector import HardwareInfo
from ..models.database import ModelInfo
from ..models.estimator import VRAMEstimator


@dataclass
class MatchScore:
    """匹配评分结果"""
    model: ModelInfo
    overall_score: float  # 0-100
    vram_fit_score: float  # VRAM适配度
    performance_score: float  # 性能评分
    quality_score: float  # 质量评分
    compatibility_score: float  # 兼容性评分
    can_run: bool  # 是否可以运行
    recommended_quantization: str
    estimated_vram_mb: float
    estimated_tokens_per_sec: float
    warnings: List[str]


class MatchScorer:
    """硬件-模型匹配评分器"""

    def __init__(self, hardware: HardwareInfo):
        self.hardware = hardware
        self.estimator = VRAMEstimator()

    def score(self, model: ModelInfo, quantization: str = "auto") -> MatchScore:
        """
        对单个模型进行匹配评分

        Args:
            model: 模型信息
            quantization: 量化方案，auto则自动推荐

        Returns:
            匹配评分结果
        """
        warnings = []

        # 自动推荐量化方案
        if quantization == "auto":
            if self.hardware.has_gpu:
                available_vram = self.hardware.total_vram_mb
            else:
                available_vram = self.hardware.memory_available_mb * 0.7
            quantization = self.estimator.recommend_quantization(
                available_vram, model.params_billion
            )

        # 估算VRAM需求
        estimated_vram = self.estimator.estimate(
            model.params_billion, quantization, model.context_length
        )

        # 检查VRAM适配度
        if self.hardware.has_gpu:
            available_vram = self.hardware.total_vram_mb
            vram_source = "GPU"
        else:
            available_vram = self.hardware.memory_available_mb * 0.7
            vram_source = "CPU RAM"
            warnings.append("未检测到GPU，将使用CPU推理，速度较慢")

        # VRAM适配度评分 (0-25)
        vram_ratio = estimated_vram / available_vram if available_vram > 0 else 1.0
        if vram_ratio <= 0.5:
            vram_fit_score = 25.0
        elif vram_ratio <= 0.7:
            vram_fit_score = 22.0
        elif vram_ratio <= 0.85:
            vram_fit_score = 18.0
        elif vram_ratio <= 1.0:
            vram_fit_score = 15.0
            warnings.append(f"VRAM使用率高 ({vram_ratio*100:.0f}%)，建议降低量化精度")
        else:
            vram_fit_score = max(0, 15.0 - (vram_ratio - 1.0) * 10)
            warnings.append(f"VRAM不足！需要{estimated_vram:.0f}MB，可用{available_vram:.0f}MB")

        can_run = vram_ratio <= 1.1  # 允许10%超配

        # 性能评分 (0-25)
        performance_score = self._calc_performance_score(model, quantization)

        # 质量评分 (0-25)
        quality_score = self._calc_quality_score(model, quantization)

        # 兼容性评分 (0-25)
        compatibility_score = self._calc_compatibility_score(model, quantization)

        # 综合评分
        overall_score = vram_fit_score + performance_score + quality_score + compatibility_score

        # 估算推理速度
        estimated_tps = self._estimate_tokens_per_sec(model, quantization)

        return MatchScore(
            model=model,
            overall_score=overall_score,
            vram_fit_score=vram_fit_score,
            performance_score=performance_score,
            quality_score=quality_score,
            compatibility_score=compatibility_score,
            can_run=can_run,
            recommended_quantization=quantization,
            estimated_vram_mb=estimated_vram,
            estimated_tokens_per_sec=estimated_tps,
            warnings=warnings,
        )

    def _calc_performance_score(self, model: ModelInfo, quantization: str) -> float:
        """计算性能评分"""
        score = 15.0  # 基础分

        # 参数量越小性能越好
        if model.params_billion <= 7:
            score += 5
        elif model.params_billion <= 14:
            score += 3
        elif model.params_billion <= 32:
            score += 1

        # 量化方案影响性能
        quant_options = self.estimator.get_quantization_options()
        quant_info = quant_options.get(quantization, {"speed_ratio": 1.0})
        speed_ratio = quant_info["speed_ratio"]

        if speed_ratio >= 2.0:
            score += 5
        elif speed_ratio >= 1.5:
            score += 3
        elif speed_ratio >= 1.0:
            score += 1

        return min(25.0, score)

    def _calc_quality_score(self, model: ModelInfo, quantization: str) -> float:
        """计算质量评分"""
        score = 10.0  # 基础分

        # 基准测试分数
        avg_benchmark = 0.0
        if model.benchmarks:
            avg_benchmark = sum(model.benchmarks.values()) / len(model.benchmarks)

        if avg_benchmark >= 80:
            score += 8
        elif avg_benchmark >= 70:
            score += 6
        elif avg_benchmark >= 60:
            score += 4
        elif avg_benchmark >= 50:
            score += 2

        # 参数量越大质量越好
        if model.params_billion >= 70:
            score += 4
        elif model.params_billion >= 32:
            score += 3
        elif model.params_billion >= 14:
            score += 2
        elif model.params_billion >= 7:
            score += 1

        # 量化精度影响质量
        quant_options = self.estimator.get_quantization_options()
        quant_info = quant_options.get(quantization, {"bits": 16})
        bits = quant_info["bits"]

        if bits >= 16:
            score += 3
        elif bits >= 8:
            score += 2
        elif bits >= 5:
            score += 1
        else:
            score -= 1

        return min(25.0, max(0, score))

    def _calc_compatibility_score(self, model: ModelInfo, quantization: str) -> float:
        """计算兼容性评分"""
        score = 15.0  # 基础分

        # 检查GPU兼容性
        if self.hardware.has_nvidia:
            score += 5  # NVIDIA兼容性最好
        elif self.hardware.has_amd:
            score += 3
        elif self.hardware.has_ascend:
            if "llama" in model.architecture.lower() or "qwen" in model.tags:
                score += 3
            else:
                score += 1
        elif self.hardware.has_mthreads:
            score += 2
        else:
            score += 2  # CPU运行

        # 中文模型在国内环境兼容性更好
        if model.language == "zh":
            score += 3
        elif model.language == "multilingual":
            score += 2

        # 开源协议
        if model.license in ["apache-2.0", "mit", "bsd"]:
            score += 2

        return min(25.0, score)

    def _estimate_tokens_per_sec(self, model: ModelInfo, quantization: str) -> float:
        """估算每秒生成token数"""
        # 基础速度（假设RTX 4090 @ fp16）
        base_tps = 50.0

        # 根据参数量调整
        if model.params_billion <= 3:
            base_tps *= 3.0
        elif model.params_billion <= 7:
            base_tps *= 2.0
        elif model.params_billion <= 14:
            base_tps *= 1.0
        elif model.params_billion <= 32:
            base_tps *= 0.5
        elif model.params_billion <= 70:
            base_tps *= 0.25
        else:
            base_tps *= 0.15

        # 根据量化方案调整
        quant_options = self.estimator.get_quantization_options()
        quant_info = quant_options.get(quantization, {"speed_ratio": 1.0})
        base_tps *= quant_info["speed_ratio"]

        # 根据硬件调整
        if not self.hardware.has_gpu:
            base_tps *= 0.05  # CPU慢20倍
        elif self.hardware.has_nvidia:
            # 根据显存大小估算GPU性能
            total_vram = self.hardware.total_vram_mb
            if total_vram >= 48000:  # RTX 4090 / A6000
                base_tps *= 1.2
            elif total_vram >= 24000:  # RTX 3090/4090 24GB
                base_tps *= 1.0
            elif total_vram >= 16000:  # RTX 4080 / 4070 Ti
                base_tps *= 0.7
            elif total_vram >= 12000:  # RTX 3060 / 4070
                base_tps *= 0.5
            elif total_vram >= 8000:  # RTX 3070 / 4060
                base_tps *= 0.35
            else:
                base_tps *= 0.2
        elif self.hardware.has_amd:
            base_tps *= 0.7
        elif self.hardware.has_ascend:
            base_tps *= 0.6
        elif self.hardware.has_mthreads:
            base_tps *= 0.4

        return round(base_tps, 1)
