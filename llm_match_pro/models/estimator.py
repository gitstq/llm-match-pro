"""VRAM估算器"""

from ..utils.helpers import estimate_vram_requirement


class VRAMEstimator:
    """VRAM需求估算器"""

    def estimate(
        self,
        params_billion: float,
        quantization: str = "fp16",
        context_length: int = 4096,
        batch_size: int = 1,
    ) -> float:
        """
        估算VRAM需求

        Args:
            params_billion: 参数量（十亿）
            quantization: 量化方案
            context_length: 上下文长度
            batch_size: 批大小

        Returns:
            VRAM需求（MB）
        """
        return estimate_vram_requirement(params_billion, quantization, context_length, batch_size)

    def get_quantization_options(self) -> dict:
        """获取支持的量化选项"""
        return {
            "fp32": {"bits": 32, "description": "全精度FP32，最高质量", "speed_ratio": 0.5},
            "fp16": {"bits": 16, "description": "半精度FP16，推荐", "speed_ratio": 1.0},
            "bf16": {"bits": 16, "description": "Brain Float16", "speed_ratio": 1.0},
            "int8": {"bits": 8, "description": "INT8量化，速度提升", "speed_ratio": 1.5},
            "Q8_0": {"bits": 8, "description": "GGUF Q8_0，高质量量化", "speed_ratio": 1.4},
            "Q6_K": {"bits": 6, "description": "GGUF Q6_K", "speed_ratio": 1.6},
            "Q5_K_M": {"bits": 5, "description": "GGUF Q5_K_M，平衡方案", "speed_ratio": 1.8},
            "Q5_K_S": {"bits": 5, "description": "GGUF Q5_K_S", "speed_ratio": 1.9},
            "Q4_K_M": {"bits": 4, "description": "GGUF Q4_K_M，推荐量化", "speed_ratio": 2.0},
            "Q4_K_S": {"bits": 4, "description": "GGUF Q4_K_S", "speed_ratio": 2.1},
            "Q4_0": {"bits": 4, "description": "GGUF Q4_0，最小体积", "speed_ratio": 2.2},
            "Q3_K_M": {"bits": 3, "description": "GGUF Q3_K_M，低显存", "speed_ratio": 2.5},
            "Q3_K_S": {"bits": 3, "description": "GGUF Q3_K_S", "speed_ratio": 2.6},
            "Q2_K": {"bits": 2, "description": "GGUF Q2_K，极限压缩", "speed_ratio": 3.0},
            "awq": {"bits": 4, "description": "AWQ量化，GPU加速", "speed_ratio": 2.0},
            "gptq": {"bits": 4, "description": "GPTQ量化，广泛支持", "speed_ratio": 1.9},
        }

    def recommend_quantization(self, available_vram_mb: float, params_billion: float) -> str:
        """
        根据可用VRAM推荐量化方案

        Args:
            available_vram_mb: 可用VRAM（MB）
            params_billion: 参数量

        Returns:
            推荐的量化方案
        """
        quantizations = ["fp16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q4_0", "Q3_K_M", "Q2_K"]

        for quant in quantizations:
            vram_needed = self.estimate(params_billion, quant)
            # 预留15%余量
            if vram_needed * 1.15 <= available_vram_mb:
                return quant

        return "Q2_K"  # 最低量化
