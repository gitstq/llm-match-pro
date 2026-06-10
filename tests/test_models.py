"""模型数据库测试"""

import pytest
from llm_match_pro.models.database import ModelDatabase, ModelInfo
from llm_match_pro.models.estimator import VRAMEstimator


class TestModelDatabase:
    """测试模型数据库"""

    def test_initialization(self):
        """测试初始化"""
        db = ModelDatabase()
        assert len(db.models) > 0

    def test_get_model(self):
        """测试获取模型"""
        db = ModelDatabase()
        model = db.get_model("Qwen/Qwen2.5-7B-Instruct")
        assert model is not None
        assert model.name == "Qwen2.5-7B-Instruct"

    def test_list_models(self):
        """测试列出模型"""
        db = ModelDatabase()
        models = db.list_models()
        assert len(models) > 0

    def test_list_by_language(self):
        """测试按语言筛选"""
        db = ModelDatabase()
        models = db.list_models(language="zh")
        assert len(models) > 0
        for m in models:
            assert m.language == "zh"

    def test_list_by_tags(self):
        """测试按标签筛选"""
        db = ModelDatabase()
        models = db.list_models(tags=["chat"])
        assert len(models) > 0

    def test_quantized_variants(self):
        """测试量化变体"""
        db = ModelDatabase()
        variants = db.get_quantized_variants("Qwen/Qwen2.5-7B-Instruct")
        assert len(variants) > 0


class TestVRAMEstimator:
    """测试VRAM估算器"""

    def test_estimate_fp16(self):
        """测试FP16估算"""
        estimator = VRAMEstimator()
        vram = estimator.estimate(7.0, "fp16")
        assert vram > 0
        assert vram < 50000  # 应该小于50GB

    def test_estimate_q4(self):
        """测试Q4量化估算"""
        estimator = VRAMEstimator()
        vram_fp16 = estimator.estimate(7.0, "fp16")
        vram_q4 = estimator.estimate(7.0, "Q4_K_M")
        assert vram_q4 < vram_fp16

    def test_recommend_quantization(self):
        """测试量化推荐"""
        estimator = VRAMEstimator()
        quant = estimator.recommend_quantization(8192, 7.0)  # 8GB显存
        assert quant in ["fp16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q4_0", "Q3_K_M", "Q2_K"]

    def test_quantization_options(self):
        """测试量化选项"""
        estimator = VRAMEstimator()
        options = estimator.get_quantization_options()
        assert "fp16" in options
        assert "Q4_K_M" in options
