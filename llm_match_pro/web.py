"""Web UI入口模块"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from .hardware.detector import HardwareDetector
from .models.database import ModelDatabase
from .engine.recommender import Recommender
from .utils.helpers import format_vram


def main() -> None:
    """Web UI主函数"""
    st.set_page_config(
        page_title="LLM-Match-Pro",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 自定义CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .model-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .score-high { color: #28a745; font-weight: bold; }
    .score-medium { color: #ffc107; font-weight: bold; }
    .score-low { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # 标题
    st.markdown('<div class="main-header">🤖 LLM-Match-Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">智能本地LLM硬件匹配与推荐引擎</div>', unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置")

        # 硬件检测按钮
        if st.button("🔍 检测硬件", type="primary", use_container_width=True):
            st.session_state.hardware_detected = True

        st.divider()

        # 推荐配置
        st.subheader("推荐设置")
        top_k = st.slider("推荐数量", 1, 20, 10)
        language_filter = st.selectbox(
            "语言偏好",
            ["全部", "中文", "英文"],
            index=0,
        )
        only_runnable = st.toggle("仅显示可运行", value=True)

        st.divider()

        # 量化方案
        st.subheader("量化方案")
        quant_preference = st.selectbox(
            "优先量化",
            ["自动推荐", "fp16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q4_0", "Q3_K_M"],
            index=0,
        )

        st.divider()

        # 关于
        st.markdown("""
        **LLM-Match-Pro v1.0.0**

        智能本地LLM硬件匹配与推荐引擎

        - 中文模型优先
        - 国产GPU支持
        - 智能量化推荐
        """)

    # 主内容区
    if not st.session_state.get("hardware_detected", False):
        st.info("👈 请点击侧边栏的「检测硬件」按钮开始分析")
        return

    # 检测硬件
    with st.spinner("正在检测硬件信息..."):
        detector = HardwareDetector()
        hardware = detector.detect_all()

    # 显示硬件信息
    st.header("💻 硬件信息")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("CPU核心", f"{hardware.cpu_count}核")
    with col2:
        st.metric("内存", hardware.memory_total_formatted)
    with col3:
        gpu_count = len(hardware.gpus)
        st.metric("GPU数量", f"{gpu_count}个")
    with col4:
        st.metric("总显存", hardware.total_vram_formatted if hardware.has_gpu else "无")

    # GPU详情
    if hardware.gpus:
        st.subheader("🎮 GPU详情")
        gpu_data = []
        for gpu in hardware.gpus:
            gpu_data.append({
                "名称": gpu.name,
                "厂商": gpu.vendor,
                "显存": format_vram(gpu.vram_total_mb),
                "驱动": gpu.driver_version,
            })
        st.dataframe(gpu_data, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 未检测到GPU，将使用CPU推理（速度较慢）")

    st.divider()

    # 模型推荐
    st.header("🎯 模型推荐")

    with st.spinner("正在分析最佳匹配..."):
        db = ModelDatabase()
        recommender = Recommender(hardware, db)

        lang_map = {"全部": None, "中文": "zh", "英文": "en"}
        lang = lang_map.get(language_filter)

        quant_map = {
            "自动推荐": "auto",
            "fp16": "fp16",
            "Q8_0": "Q8_0",
            "Q6_K": "Q6_K",
            "Q5_K_M": "Q5_K_M",
            "Q4_K_M": "Q4_K_M",
            "Q4_0": "Q4_0",
            "Q3_K_M": "Q3_K_M",
        }
        quant = quant_map.get(quant_preference, "auto")

        scores = recommender.recommend(
            top_k=top_k,
            language=lang,
            only_runnable=only_runnable,
            prefer_quantization=quant,
        )

    if not scores:
        st.warning("未找到符合条件的模型，请调整筛选条件")
        return

    # 推荐结果可视化
    chart_data = []
    for score in scores:
        chart_data.append({
            "模型": score.model.name,
            "综合评分": score.overall_score,
            "VRAM适配": score.vram_fit_score,
            "性能": score.performance_score,
            "质量": score.quality_score,
            "兼容性": score.compatibility_score,
            "预估速度(t/s)": score.estimated_tokens_per_sec,
            "VRAM需求(GB)": score.estimated_vram_mb / 1024,
        })

    df = pd.DataFrame(chart_data)

    # 综合评分柱状图
    fig = px.bar(
        df,
        x="模型",
        y="综合评分",
        color="综合评分",
        color_continuous_scale="RdYlGn",
        title="模型综合评分对比",
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # 雷达图对比（前3个）
    if len(scores) >= 2:
        fig_radar = go.Figure()
        categories = ["VRAM适配", "性能", "质量", "兼容性"]

        for i, score in enumerate(scores[:3]):
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    score.vram_fit_score,
                    score.performance_score,
                    score.quality_score,
                    score.compatibility_score,
                ],
                theta=categories,
                fill="toself",
                name=score.model.name,
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 25])),
            showlegend=True,
            title="Top 3 模型能力雷达图",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 详细推荐列表
    st.subheader("📋 详细推荐")

    for i, score in enumerate(scores):
        model = score.model

        score_class = "score-high" if score.overall_score >= 70 else \
                      "score-medium" if score.overall_score >= 50 else "score-low"

        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"**#{i+1} {model.name}**")
                st.caption(model.description)
                st.markdown(f"标签: {', '.join(model.tags[:3])}")

            with col2:
                st.markdown(f"参数量: **{model.params_billion:.1f}B**")
                st.markdown(f"推荐量化: **{score.recommended_quantization}**")
                st.markdown(f"预估VRAM: **{format_vram(score.estimated_vram_mb)}**")

            with col3:
                st.markdown(f"综合评分: <span class='{score_class}'>{score.overall_score:.0f}/100</span>",
                           unsafe_allow_html=True)
                st.markdown(f"预估速度: **{score.estimated_tokens_per_sec:.1f} t/s**")
                status = "✅ 可运行" if score.can_run else "❌ 不可运行"
                st.markdown(f"状态: **{status}**")

            if score.warnings:
                for warning in score.warnings:
                    st.warning(warning)

            # 启动命令
            with st.expander("查看启动命令"):
                st.code(f"""
# llama.cpp
./main -m {model.id}-{score.recommended_quantization.lower()}.gguf -n 512

# Ollama
ollama run {model.id.split('/')[-1].lower()}

# Docker (vLLM)
docker run --gpus all -p 8000:8000 vllm/vllm-openai:latest \\
  --model {model.id} --quantization {score.recommended_quantization}
                """.strip(), language="bash")

            st.divider()

    # 升级建议
    st.header("💡 硬件升级建议")
    suggestions = recommender.get_upgrade_path()

    if suggestions:
        for suggestion in suggestions:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                suggestion["priority"], "⚪"
            )
            with st.expander(f"{priority_emoji} {suggestion['title']}"):
                st.write(suggestion["description"])
                if "recommended" in suggestion:
                    st.write(f"**推荐:** {suggestion['recommended']}")
                if "estimated_cost" in suggestion:
                    st.write(f"**预估成本:** {suggestion['estimated_cost']}")
                st.write(f"**收益:** {suggestion['benefit']}")
    else:
        st.success("✅ 当前硬件配置良好，无需升级")


if __name__ == "__main__":
    main()
