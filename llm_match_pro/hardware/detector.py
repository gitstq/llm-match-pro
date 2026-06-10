"""硬件检测模块"""

import psutil
import platform
import subprocess
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.helpers import format_bytes, format_vram


@dataclass
class GPUInfo:
    """GPU信息"""
    name: str = "Unknown"
    vendor: str = "Unknown"
    vram_total_mb: float = 0.0
    vram_free_mb: float = 0.0
    driver_version: str = "Unknown"
    compute_capability: str = ""
    pci_bus_id: str = ""
    is_available: bool = False


@dataclass
class HardwareInfo:
    """完整硬件信息"""
    cpu_count: int = 0
    cpu_freq_mhz: float = 0.0
    memory_total_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    gpus: List[GPUInfo] = field(default_factory=list)
    platform: str = ""
    platform_version: str = ""
    architecture: str = ""

    @property
    def total_vram_mb(self) -> float:
        """总显存"""
        return sum(gpu.vram_total_mb for gpu in self.gpus)

    @property
    def total_vram_formatted(self) -> str:
        """格式化总显存"""
        return format_vram(self.total_vram_mb)

    @property
    def memory_total_formatted(self) -> str:
        """格式化总内存"""
        return format_bytes(int(self.memory_total_mb * 1024 * 1024))

    @property
    def has_gpu(self) -> bool:
        """是否有可用GPU"""
        return len(self.gpus) > 0 and any(gpu.is_available for gpu in self.gpus)

    @property
    def has_nvidia(self) -> bool:
        """是否有NVIDIA GPU"""
        return any(gpu.vendor == "NVIDIA" for gpu in self.gpus)

    @property
    def has_amd(self) -> bool:
        """是否有AMD GPU"""
        return any(gpu.vendor == "AMD" for gpu in self.gpus)

    @property
    def has_ascend(self) -> bool:
        """是否有昇腾GPU"""
        return any(gpu.vendor == "Huawei Ascend" for gpu in self.gpus)

    @property
    def has_mthreads(self) -> bool:
        """是否有摩尔线程GPU"""
        return any(gpu.vendor == "Moore Threads" for gpu in self.gpus)


class HardwareDetector:
    """硬件检测器"""

    def __init__(self):
        self.info = HardwareInfo()

    def detect_all(self) -> HardwareInfo:
        """检测所有硬件信息"""
        self._detect_cpu()
        self._detect_memory()
        self._detect_disk()
        self._detect_platform()
        self._detect_gpus()
        return self.info

    def _detect_cpu(self) -> None:
        """检测CPU信息"""
        self.info.cpu_count = psutil.cpu_count(logical=True)
        try:
            freq = psutil.cpu_freq()
            if freq:
                self.info.cpu_freq_mhz = freq.max or freq.current
        except Exception:
            pass

    def _detect_memory(self) -> None:
        """检测内存信息"""
        mem = psutil.virtual_memory()
        self.info.memory_total_mb = mem.total / (1024 * 1024)
        self.info.memory_available_mb = mem.available / (1024 * 1024)

    def _detect_disk(self) -> None:
        """检测磁盘信息"""
        disk = psutil.disk_usage("/")
        self.info.disk_total_gb = disk.total / (1024 ** 3)
        self.info.disk_free_gb = disk.free / (1024 ** 3)

    def _detect_platform(self) -> None:
        """检测平台信息"""
        self.info.platform = platform.system()
        self.info.platform_version = platform.release()
        self.info.architecture = platform.machine()

    def _detect_gpus(self) -> None:
        """检测所有GPU"""
        self.info.gpus = []

        # 尝试检测NVIDIA GPU
        self._detect_nvidia()

        # 尝试检测AMD GPU
        self._detect_amd()

        # 尝试检测昇腾GPU
        self._detect_ascend()

        # 尝试检测摩尔线程GPU
        self._detect_mthreads()

        # 尝试通过lspci检测其他GPU
        self._detect_via_lspci()

    def _detect_nvidia(self) -> None:
        """检测NVIDIA GPU"""
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram_total = mem_info.total / (1024 * 1024)
                vram_free = mem_info.free / (1024 * 1024)

                try:
                    driver = pynvml.nvmlSystemGetDriverVersion()
                    if isinstance(driver, bytes):
                        driver = driver.decode("utf-8")
                except Exception:
                    driver = "Unknown"

                try:
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    compute_cap = f"{major}.{minor}"
                except Exception:
                    compute_cap = ""

                gpu = GPUInfo(
                    name=name,
                    vendor="NVIDIA",
                    vram_total_mb=vram_total,
                    vram_free_mb=vram_free,
                    driver_version=driver,
                    compute_capability=compute_cap,
                    is_available=True,
                )
                self.info.gpus.append(gpu)

        except ImportError:
            pass
        except Exception:
            pass

    def _detect_amd(self) -> None:
        """检测AMD GPU"""
        try:
            # 尝试通过rocm-smi检测
            result = subprocess.run(
                ["rocm-smi", "--showproductname", "--showmeminfo", "vram", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for gpu_id, gpu_data in data.items():
                    name = gpu_data.get("Card series", "AMD GPU")
                    vram_str = gpu_data.get("vram", "0")
                    vram_mb = self._parse_vram_string(vram_str)

                    gpu = GPUInfo(
                        name=name,
                        vendor="AMD",
                        vram_total_mb=vram_mb,
                        is_available=True,
                    )
                    self.info.gpus.append(gpu)
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        except Exception:
            pass

    def _detect_ascend(self) -> None:
        """检测华为昇腾GPU"""
        try:
            result = subprocess.run(
                ["npu-smi", "info", "-t", "board"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "NPU" in line or "Ascend" in line:
                        gpu = GPUInfo(
                            name="Huawei Ascend NPU",
                            vendor="Huawei Ascend",
                            vram_total_mb=32768,  # 典型值32GB
                            is_available=True,
                        )
                        self.info.gpus.append(gpu)
                        break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        except Exception:
            pass

    def _detect_mthreads(self) -> None:
        """检测摩尔线程GPU"""
        try:
            result = subprocess.run(
                ["mthreads-gmi"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                output = result.stdout
                if "MTT" in output or "Moore Threads" in output:
                    # 解析显存信息
                    vram_mb = 16384  # 默认16GB
                    if "S80" in output:
                        vram_mb = 16384
                    elif "S70" in output:
                        vram_mb = 16384
                    elif "S3000" in output:
                        vram_mb = 32768

                    gpu = GPUInfo(
                        name="Moore Threads GPU",
                        vendor="Moore Threads",
                        vram_total_mb=vram_mb,
                        is_available=True,
                    )
                    self.info.gpus.append(gpu)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        except Exception:
            pass

    def _detect_via_lspci(self) -> None:
        """通过lspci检测GPU"""
        if self.info.gpus:
            return

        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line or "3D controller" in line:
                        if "NVIDIA" in line:
                            continue  # 已由nvml检测
                        elif "AMD" in line or "ATI" in line:
                            continue  # 已由rocm-smi检测
                        else:
                            # 未知GPU，添加基本信息
                            gpu = GPUInfo(
                                name=line.split(":")[-1].strip(),
                                vendor="Unknown",
                                is_available=False,
                            )
                            self.info.gpus.append(gpu)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        except Exception:
            pass

    @staticmethod
    def _parse_vram_string(vram_str: str) -> float:
        """解析显存字符串"""
        try:
            vram_str = vram_str.strip().upper()
            if "GB" in vram_str:
                return float(vram_str.replace("GB", "").strip()) * 1024
            elif "MB" in vram_str:
                return float(vram_str.replace("MB", "").strip())
            else:
                return float(vram_str)
        except (ValueError, AttributeError):
            return 0.0

    def get_summary(self) -> Dict[str, Any]:
        """获取硬件摘要信息"""
        return {
            "cpu": {
                "cores": self.info.cpu_count,
                "frequency_mhz": self.info.cpu_freq_mhz,
            },
            "memory": {
                "total": self.info.memory_total_formatted,
                "available_mb": self.info.memory_available_mb,
            },
            "disk": {
                "total_gb": round(self.info.disk_total_gb, 1),
                "free_gb": round(self.info.disk_free_gb, 1),
            },
            "gpus": [
                {
                    "name": gpu.name,
                    "vendor": gpu.vendor,
                    "vram": format_vram(gpu.vram_total_mb),
                    "driver": gpu.driver_version,
                }
                for gpu in self.info.gpus
            ],
            "platform": {
                "system": self.info.platform,
                "version": self.info.platform_version,
                "architecture": self.info.architecture,
            },
        }
