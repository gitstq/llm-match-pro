"""推荐引擎测试"""

import pytest
from llm_match_pro.hardware.detector import HardwareInfo, GPUInfo
from llm_match_pro.models.database import ModelDatabase
from llm_match_pro.engine.recommender import Recommender
from llm_match_pro.engine.scorer import MatchScorer


class TestMatchScorer:
    """测试匹配评分器"""

    def test_score_basic(self):
        """测试基础评分"""
        hardware = HardwareInfo()
        hardware.gpus = [GPUInfo(vram_total_mb=24576, is_available=True)]

        db = ModelDatabase()
        model = db.get_model("Qwen/Qwen2.5-7B-Instruct")

        scorer = MatchScorer(hardware)
        score = scorer.score(model)

        assert score.overall_score > 0
        assert score.overall_score <= 100
        assert score.can_run

    def test_score_no_gpu(self):
        """测试无GPU评分"""
        hardware = HardwareInfo()
        hardware.memory_total_mb = 32768
        hardware.memory_available_mb = 16384

        db = ModelDatabase()
        model = db.get_model("Qwen/Qwen2.5-7B-Instruct")

        scorer = MatchScorer(hardware)
        score = scorer.score(model)

        assert not score.can_run or score.warnings  # 应该警告或不可运行


class TestRecommender:
    """测试推荐引擎"""

    def test_recommend_basic(self):
        """测试基础推荐"""
        hardware = HardwareInfo()
        hardware.gpus = [GPUInfo(vram_total_mb=24576, is_available=True)]

        db = ModelDatabase()
        recommender = Recommender(hardware, db)

        scores = recommender.recommend(top_k=5)
        assert len(scores) > 0
        assert len(scores) <= 5

    def test_recommend_chinese(self):
        """测试中文模型推荐"""
        hardware = HardwareInfo()
        hardware.gpus = [GPUInfo(vram_total_mb=24576, is_available=True)]

        db = ModelDatabase()
        recommender = Recommender(hardware, db)

        scores = recommender.recommend_chinese_models(top_k=5)
        assert len(scores) > 0
        for score in scores:
            assert score.model.language == "zh"

    def test_upgrade_path(self):
        """测试升级建议"""
        hardware = HardwareInfo()
        recommender = Recommender(hardware)

        suggestions = recommender.get_upgrade_path()
        assert len(suggestions) > 0  # 无GPU应该有建议
