"""CLI入口模块"""

import sys
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from .hardware.detector import HardwareDetector
from .models.database import ModelDatabase
from .engine.recommender import Recommender
from .utils.helpers import format_vram, format_bytes

app = typer.Typer(
    name="llm-match-pro",
    help="智能本地LLM硬件匹配与推荐引擎",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """版本回调"""
    if value:
        console.print("[bold cyan]LLM-Match-Pro[/bold cyan] v1.0.0")
        console.print("智能本地LLM硬件匹配与推荐引擎")
        console.print("License: MIT")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="显示版本信息", callback=version_callback
    ),
) -> None:
    """LLM-Match-Pro CLI"""
    pass


@app.command(name="detect")
def detect_hardware() -> None:
    """检测当前硬件信息"""
    console.print("\n[bold cyan]🔍 正在检测硬件信息...[/bold cyan]\n")

    detector = HardwareDetector()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("检测中...", total=None)
        info = detector.detect_all()
        progress.update(task, completed=True)

    # 显示CPU信息
    cpu_table = Table(title="CPU信息", box=box.ROUNDED)
    cpu_table.add_column("项目", style="cyan")
    cpu_table.add_column("值", style="green")
    cpu_table.add_row("核心数", str(info.cpu_count))
    cpu_table.add_row("频率", f"{info.cpu_freq_mhz:.0f} MHz")
    console.print(cpu_table)

    # 显示内存信息
    mem_table = Table(title="内存信息", box=box.ROUNDED)
    mem_table.add_column("项目", style="cyan")
    mem_table.add_column("值", style="green")
    mem_table.add_row("总内存", info.memory_total_formatted)
    mem_table.add_row("可用内存", format_vram(info.memory_available_mb))
    console.print(mem_table)

    # 显示GPU信息
    if info.gpus:
        gpu_table = Table(title="GPU信息", box=box.ROUNDED)
        gpu_table.add_column("序号", style="cyan")
        gpu_table.add_column("名称", style="green")
        gpu_table.add_column("厂商", style="yellow")
        gpu_table.add_column("显存", style="magenta")
        gpu_table.add_column("驱动", style="blue")

        for i, gpu in enumerate(info.gpus):
            gpu_table.add_row(
                str(i + 1),
                gpu.name,
                gpu.vendor,
                format_vram(gpu.vram_total_mb),
                gpu.driver_version,
            )
        console.print(gpu_table)
    else:
        console.print("[yellow]⚠️ 未检测到GPU[/yellow]")

    # 显示平台信息
    platform_table = Table(title="平台信息", box=box.ROUNDED)
    platform_table.add_column("项目", style="cyan")
    platform_table.add_column("值", style="green")
    platform_table.add_row("系统", info.platform)
    platform_table.add_row("版本", info.platform_version)
    platform_table.add_row("架构", info.architecture)
    console.print(platform_table)

    # 显示磁盘信息
    disk_table = Table(title="磁盘信息", box=box.ROUNDED)
    disk_table.add_column("项目", style="cyan")
    disk_table.add_column("值", style="green")
    disk_table.add_row("总容量", f"{info.disk_total_gb:.1f} GB")
    disk_table.add_row("可用空间", f"{info.disk_free_gb:.1f} GB")
    console.print(disk_table)


@app.command(name="recommend")
def recommend_models(
    top_k: int = typer.Option(10, "--top-k", "-k", help="推荐数量"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="语言筛选 (zh/en)"),
    only_runnable: bool = typer.Option(True, "--runnable/--all", help="仅显示可运行"),
    quantization: Optional[str] = typer.Option(None, "--quant", "-q", help="量化方案"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="标签筛选"),
) -> None:
    """推荐适合的LLM模型"""
    console.print("\n[bold cyan]🤖 LLM-Match-Pro 智能推荐[/bold cyan]\n")

    # 检测硬件
    console.print("[dim]正在检测硬件...[/dim]")
    detector = HardwareDetector()
    hardware = detector.detect_all()

    console.print(f"[green]✓[/green] 检测到 {len(hardware.gpus)} 个GPU")
    if hardware.has_gpu:
        console.print(f"[green]✓[/green] 总显存: {hardware.total_vram_formatted}")
    else:
        console.print("[yellow]⚠[/yellow] 未检测到GPU，将使用CPU推理")

    # 创建推荐器
    db = ModelDatabase()
    recommender = Recommender(hardware, db)

    console.print("[dim]正在分析模型匹配度...[/dim]\n")

    # 获取推荐
    scores = recommender.recommend(
        top_k=top_k,
        language=language,
        tags=tags,
        only_runnable=only_runnable,
        prefer_quantization=quantization,
    )

    if not scores:
        console.print("[yellow]⚠️ 未找到符合条件的模型[/yellow]")
        console.print("建议：")
        console.print("  1. 使用 --all 参数查看所有模型")
        console.print("  2. 使用 --quant 指定更低量化精度")
        return

    # 显示推荐结果
    table = Table(
        title=f"推荐模型 (Top {len(scores)})",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("排名", style="bold", width=4, justify="center")
    table.add_column("模型", style="green", min_width=25)
    table.add_column("参数量", style="yellow", width=8)
    table.add_column("量化", style="magenta", width=8)
    table.add_column("VRAM", style="red", width=10)
    table.add_column("速度", style="blue", width=10)
    table.add_column("评分", style="bold cyan", width=6)
    table.add_column("状态", width=8)

    for i, score in enumerate(scores):
        model = score.model
        status = "[green]✓ 可运行[/green]" if score.can_run else "[red]✗ 不可[/red]"

        table.add_row(
            str(i + 1),
            model.name,
            f"{model.params_billion:.1f}B",
            score.recommended_quantization,
            format_vram(score.estimated_vram_mb),
            f"{score.estimated_tokens_per_sec:.1f} t/s",
            f"{score.overall_score:.0f}",
            status,
        )

    console.print(table)

    # 显示详细信息
    console.print("\n[bold cyan]📋 详细推荐信息[/bold cyan]\n")
    for i, score in enumerate(scores[:5]):
        model = score.model

        details = Text()
        details.append(f"{i+1}. ", style="bold")
        details.append(f"{model.name}\n", style="bold green")
        details.append(f"   描述: {model.description}\n", style="dim")
        details.append(f"   推荐量化: ", style="cyan")
        details.append(f"{score.recommended_quantization}\n", style="magenta")
        details.append(f"   预估VRAM: ", style="cyan")
        details.append(f"{format_vram(score.estimated_vram_mb)}\n", style="red")
        details.append(f"   预估速度: ", style="cyan")
        details.append(f"{score.estimated_tokens_per_sec:.1f} tokens/s\n", style="blue")
        details.append(f"   综合评分: ", style="cyan")
        details.append(f"{score.overall_score:.0f}/100 ", style="bold yellow")
        details.append(f"(VRAM:{score.vram_fit_score:.0f} 性能:{score.performance_score:.0f} "
                       f"质量:{score.quality_score:.0f} 兼容:{score.compatibility_score:.0f})\n")

        if score.warnings:
            details.append("   ⚠️ 注意: ", style="yellow")
            details.append(f"{'; '.join(score.warnings)}\n", style="yellow")

        console.print(Panel(details, border_style="blue"))


@app.command(name="upgrade")
def upgrade_advice() -> None:
    """获取硬件升级建议"""
    console.print("\n[bold cyan]💡 硬件升级建议[/bold cyan]\n")

    detector = HardwareDetector()
    hardware = detector.detect_all()
    recommender = Recommender(hardware)

    suggestions = recommender.get_upgrade_path()

    if not suggestions:
        console.print("[green]✓ 当前硬件配置良好，无需升级[/green]")
        return

    for suggestion in suggestions:
        priority_color = {"high": "red", "medium": "yellow", "low": "green"}.get(
            suggestion["priority"], "white"
        )

        content = Text()
        content.append(f"[{suggestion['priority'].upper()}] ", style=f"bold {priority_color}")
        content.append(f"{suggestion['title']}\n", style="bold")
        content.append(f"{suggestion['description']}\n", style="dim")

        if "recommended" in suggestion:
            content.append(f"推荐: ", style="cyan")
            content.append(f"{suggestion['recommended']}\n", style="green")

        if "estimated_cost" in suggestion:
            content.append(f"预估成本: ", style="cyan")
            content.append(f"{suggestion['estimated_cost']}\n", style="yellow")

        content.append(f"收益: ", style="cyan")
        content.append(f"{suggestion['benefit']}", style="bold green")

        console.print(Panel(content, border_style=priority_color))


@app.command(name="models")
def list_models(
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="语言筛选"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="标签筛选"),
) -> None:
    """列出支持的模型"""
    console.print("\n[bold cyan]📚 支持的模型列表[/bold cyan]\n")

    db = ModelDatabase()
    tags = [tag] if tag else None
    models = db.list_models(language=language, tags=tags)

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("模型", style="green", min_width=25)
    table.add_column("参数量", style="yellow", width=8)
    table.add_column("语言", style="magenta", width=8)
    table.add_column("上下文", style="blue", width=8)
    table.add_column("标签", style="dim")

    for model in models:
        table.add_row(
            model.name,
            f"{model.params_billion:.1f}B",
            model.language,
            str(model.context_length),
            ", ".join(model.tags[:3]),
        )

    console.print(table)
    console.print(f"\n共 {len(models)} 个模型")


@app.command(name="quant")
def list_quantizations() -> None:
    """列出支持的量化方案"""
    console.print("\n[bold cyan]🔢 支持的量化方案[/bold cyan]\n")

    from .models.estimator import VRAMEstimator
    estimator = VRAMEstimator()
    options = estimator.get_quantization_options()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("方案", style="green", width=10)
    table.add_column("位数", style="yellow", width=6)
    table.add_column("描述", style="cyan")
    table.add_column("速度比", style="magenta", width=8)

    for name, info in options.items():
        table.add_row(
            name,
            str(info["bits"]),
            info["description"],
            f"{info['speed_ratio']:.1f}x",
        )

    console.print(table)


@app.command(name="launch")
def generate_launch_command(
    model_id: str = typer.Argument(..., help="模型ID"),
    quantization: str = typer.Option("Q4_K_M", "--quant", "-q", help="量化方案"),
    backend: str = typer.Option("llama.cpp", "--backend", "-b", help="推理后端"),
) -> None:
    """生成模型启动命令"""
    console.print(f"\n[bold cyan]🚀 生成启动命令: {model_id}[/bold cyan]\n")

    db = ModelDatabase()
    model = db.get_model(model_id)

    if not model:
        console.print(f"[red]✗ 未找到模型: {model_id}[/red]")
        console.print("使用 'llm-match-pro models' 查看可用模型")
        return

    commands = {
        "llama.cpp": f"./main -m {model_id}-{quantization.lower()}.gguf -n 512 --temp 0.7",
        "ollama": f"ollama run {model_id.split('/')[-1].lower()}",
        "vllm": f"python -m vllm.entrypoints.openai.api_server --model {model_id} --quantization {quantization}",
        "transformers": f"python -c \"from transformers import AutoModel; model = AutoModel.from_pretrained('{model_id}')\"",
        "text-generation-webui": f"python server.py --model {model_id.split('/')[-1]} --loader transformers",
    }

    cmd = commands.get(backend, commands["llama.cpp"])

    console.print(Panel(
        f"[bold]{backend}[/bold]\n\n"
        f"[cyan]{cmd}[/cyan]",
        title="启动命令",
        border_style="green",
    ))

    # Docker命令
    docker_cmd = f"""docker run --gpus all -it \\
  -v ~/.cache/huggingface:/root/.cache/huggingface \\
  -p 8000:8000 \\
  vllm/vllm-openai:latest \\
  --model {model_id} \\
  --quantization {quantization}"""

    console.print(Panel(
        f"[cyan]{docker_cmd}[/cyan]",
        title="Docker启动",
        border_style="blue",
    ))


def main() -> None:
    """CLI入口"""
    app()


if __name__ == "__main__":
    main()
