"""推荐引擎"""

from typing import List, Optional

from ..hardware.detector import HardwareInfo
from ..models.database import ModelDatabase, ModelInfo
from .scorer import MatchScorer, MatchScore


class Recommender:
    """LLM推荐引擎"""

    def __init__(self, hardware: HardwareInfo, db: Optional[ModelDatabase] = None):
        self.hardware = hardware
        self.db = db or ModelDatabase()
        self.scorer = MatchScorer(hardware)

    def recommend(
        self,
        top_k: int = 10,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_params: Optional[float] = None,
        max_params: Optional[float] = None,
        only_runnable: bool = True,
        prefer_quantization: Optional[str] = None,
    ) -> List[MatchScore]:
        """
        推荐最适合的LLM模型

        Args:
            top_k: 返回前K个结果
            language: 语言筛选 (zh/en/multilingual)
            tags: 标签筛选
            min_params: 最小参数量
            max_params: 最大参数量
            only_runnable: 仅返回可运行的模型
            prefer_quantization: 优先量化方案

        Returns:
            排序后的匹配评分列表
        """
        # 获取候选模型
        candidates = self.db.list_models(
            tags=tags,
            language=language,
            min_params=min_params,
            max_params=max_params,
        )

        # 评分
        scores = []
        for model in candidates:
            score = self.scorer.score(model, quantization=prefer_quantization or "auto")
            scores.append(score)

        # 筛选可运行的
        if only_runnable:
            scores = [s for s in scores if s.can_run]

        # 按综合评分排序
        scores.sort(key=lambda s: s.overall_score, reverse=True)

        return scores[:top_k]

    def recommend_for_code(self, top_k: int = 5) -> List[MatchScore]:
        """推荐适合代码任务的模型"""
        return self.recommend(
            top_k=top_k,
            tags=["code"],
            only_runnable=True,
        )

    def recommend_for_chat(self, top_k: int = 5) -> List[MatchScore]:
        """推荐适合对话任务的模型"""
        return self.recommend(
            top_k=top_k,
            tags=["chat"],
            only_runnable=True,
        )

    def recommend_chinese_models(self, top_k: int = 5) -> List[MatchScore]:
        """推荐中文模型"""
        return self.recommend(
            top_k=top_k,
            language="zh",
            only_runnable=True,
        )

    def get_upgrade_path(self) -> List[dict]:
        """
        获取硬件升级建议

        Returns:
            升级建议列表
        """
        suggestions = []

        if not self.hardware.has_gpu:
            suggestions.append({
                "priority": "high",
                "type": "add_gpu",
                "title": "添加独立GPU",
                "description": "当前无GPU，推理速度极慢。建议添加NVIDIA RTX 3060 12GB或更高",
                "estimated_cost": "￥2000-4000",
                "benefit": "速度提升20-50倍",
            })
        else:
            total_vram = self.hardware.total_vram_mb
            if total_vram < 8000:
                suggestions.append({
                    "priority": "high",
                    "type": "upgrade_gpu",
                    "title": "升级GPU显存",
                    "description": f"当前显存{total_vram/1024:.1f}GB，建议升级至12GB以上",
                    "recommended": "RTX 3060 12GB / RTX 4070 12GB",
                    "estimated_cost": "￥2500-4500",
                    "benefit": "可运行7B模型Q4量化",
                })
            elif total_vram < 16000:
                suggestions.append({
                    "priority": "medium",
                    "type": "upgrade_gpu",
                    "title": "升级GPU显存",
                    "description": f"当前显存{total_vram/1024:.1f}GB，升级后可运行更大模型",
                    "recommended": "RTX 3090 24GB / RTX 4090 24GB",
                    "estimated_cost": "￥8000-15000",
                    "benefit": "可运行14B-32B模型",
                })

        # 内存建议
        if self.hardware.memory_total_mb < 16000:
            suggestions.append({
                "priority": "medium",
                "type": "upgrade_ram",
                "title": "增加内存",
                "description": f"当前内存{self.hardware.memory_total_mb/1024:.1f}GB，建议升级至32GB",
                "estimated_cost": "￥500-1000",
                "benefit": "支持更大模型CPU推理",
            })

        return suggestions
