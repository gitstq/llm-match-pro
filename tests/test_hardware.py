"""硬件检测测试"""

import pytest
from llm_match_pro.hardware.detector import HardwareDetector, HardwareInfo, GPUInfo


class TestHardwareDetector:
    """测试硬件检测器"""

    def test_detector_initialization(self):
        """测试检测器初始化"""
        detector = HardwareDetector()
        assert detector.info is not None

    def test_detect_all(self):
        """测试完整检测"""
        detector = HardwareDetector()
        info = detector.detect_all()
        assert isinstance(info, HardwareInfo)
        assert info.cpu_count > 0
        assert info.memory_total_mb > 0

    def test_cpu_detection(self):
        """测试CPU检测"""
        detector = HardwareDetector()
        detector._detect_cpu()
        assert detector.info.cpu_count > 0

    def test_memory_detection(self):
        """测试内存检测"""
        detector = HardwareDetector()
        detector._detect_memory()
        assert detector.info.memory_total_mb > 0
        assert detector.info.memory_available_mb > 0

    def test_platform_detection(self):
        """测试平台检测"""
        detector = HardwareDetector()
        detector._detect_platform()
        assert detector.info.platform != ""
        assert detector.info.architecture != ""

    def test_summary(self):
        """测试摘要生成"""
        detector = HardwareDetector()
        detector.detect_all()
        summary = detector.get_summary()
        assert "cpu" in summary
        assert "memory" in summary
        assert "gpus" in summary
        assert "platform" in summary


class TestGPUInfo:
    """测试GPU信息"""

    def test_gpu_creation(self):
        """测试GPU创建"""
        gpu = GPUInfo(
            name="RTX 4090",
            vendor="NVIDIA",
            vram_total_mb=24576,
            is_available=True,
        )
        assert gpu.name == "RTX 4090"
        assert gpu.vendor == "NVIDIA"


class TestHardwareInfo:
    """测试硬件信息"""

    def test_total_vram(self):
        """测试总显存计算"""
        info = HardwareInfo()
        info.gpus = [
            GPUInfo(vram_total_mb=8192),
            GPUInfo(vram_total_mb=4096),
        ]
        assert info.total_vram_mb == 12288

    def test_has_gpu(self):
        """测试GPU检测"""
        info = HardwareInfo()
        assert not info.has_gpu

        info.gpus = [GPUInfo(is_available=True)]
        assert info.has_gpu
