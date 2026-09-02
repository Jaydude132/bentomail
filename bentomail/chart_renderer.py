# Author: Jason Marencic
# June 2, 2026

import io

import matplotlib

matplotlib.use(
    "Agg"
)  # Headless mode prevents display binding crashes on background workers
import matplotlib.pyplot as plt


def render_chart_to_png(chart, theme) -> bytes:
    """
    Renders a BaseChart subclass into clean binary PNG bytes,
    fully styled according to your active EmailTheme parameters.
    """
    from .components import BarChart, LineChart, PieChart

    # 1. Instantiate the figure using standard 850px dashboard width limits
    fig, ax = plt.subplots(figsize=(8, 2.7))

    # 2. Extract theme-specific styles
    bg_color = theme.section_bg
    text_color = theme.text_color
    border_color = theme.border_color
    accent_color = chart.color or theme.accent_color
    text_muted = theme.text_muted

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # 3. Handle data layout programmatically based on subclass typing
    if isinstance(chart, LineChart):
        ax.plot(
            chart.x,
            chart.y,
            color=accent_color,
            linewidth=2.5,
            marker="o",
            markersize=4,
        )
        ax.grid(True, color=border_color, linestyle="--", alpha=0.3)

    elif isinstance(chart, BarChart):
        bars = ax.bar(
            chart.categories,
            chart.values,
            color=accent_color,
            edgecolor=border_color,
            width=0.5,
        )
        # Display precise metric values above each column
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=text_color,
                fontsize=8,
            )
        ax.grid(True, color=border_color, linestyle="--", alpha=0.3, axis="y")

    elif isinstance(chart, PieChart):
        ax.axis("equal")
        slices = len(chart.sizes)

        # Color mapping: blending accent color down through standard theme colors
        colors = [accent_color]
        if slices > 1:
            theme_colors = [
                theme.accent_color,
                theme.info_color,
                theme.success_color,
                theme.warning_color,
                theme.important_color,
            ]
            colors = theme_colors[:slices]
            while len(colors) < slices:
                colors.append(theme.border_color)

        wedges, texts, autotexts = ax.pie(
            chart.sizes,
            labels=chart.labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            textprops={"color": text_color, "fontsize": 9},
        )
        for autotext in autotexts:
            autotext.set_color("#ffffff")  # High-contrast white percentage text
            autotext.set_weight("bold")

    # 4. Standard clean coordinate layout framing
    if not isinstance(chart, PieChart):
        ax.tick_params(colors=text_muted, labelsize=9)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        if chart.x_label:
            ax.set_xlabel(chart.x_label)
        if chart.y_label:
            ax.set_ylabel(chart.y_label)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(border_color)
        ax.spines["left"].set_color(border_color)

    plt.tight_layout()

    # 5. Extract raw binary PNG data without disk I/O bottlenecks
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    png_bytes = buf.getvalue()
    buf.close()

    plt.close(fig)  # Reclaim active memory allocation
    return png_bytes
