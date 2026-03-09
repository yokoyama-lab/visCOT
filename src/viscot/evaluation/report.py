"""Report generation — LaTeX tables and comparison plots."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt

from .benchmark import BenchmarkResult, run_benchmark
from .comparison import ComparisonResult


def generate_latex_table(results: list[BenchmarkResult], output_path: Path) -> None:
    """Generate a LaTeX table summarizing benchmark results.

    Args:
        results: List of benchmark results.
        output_path: Path to write the .tex file.
    """
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Readability metrics for benchmark expressions}",
        r"\label{tab:benchmark}",
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Category & Expression & Crossings & $d_{cv}$ & Jerk & Score \\",
        r"\midrule",
    ]

    for r in results:
        expr_escaped = r.expression.replace("_", r"\_")
        if len(expr_escaped) > 30:
            expr_escaped = expr_escaped[:27] + "..."
        lines.append(
            f"  {r.category} & \\texttt{{{expr_escaped}}} & "
            f"{r.score.overlap.crossing_count} & "
            f"{r.score.spacing.d_cv:.3f} & "
            f"{r.score.smoothness.jerk:.3f} & "
            f"{r.score.score:.2f} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_comparison_plots(
    comparison: ComparisonResult,
    output_dir: Path,
) -> None:
    """Generate before/after comparison plots.

    Creates:
    - Box plot of d_cv before vs after
    - Scatter plot of composite score vs tree depth

    Args:
        comparison: ComparisonResult from compare_before_after.
        output_dir: Directory to write plot images.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Box plot: d_cv before vs after
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [comparison.d_cv_before, comparison.d_cv_after]
    bp = ax.boxplot(data, tick_labels=["Before", "After"], patch_artist=True)
    bp["boxes"][0].set_facecolor("#ff9999")
    bp["boxes"][1].set_facecolor("#99ccff")
    ax.set_ylabel("$d_{cv}$ (spacing coefficient of variation)")
    ax.set_title("Spacing Uniformity: Before vs After")
    ax.text(
        0.02, 0.98,
        f"Wilcoxon p={comparison.wilcoxon_pvalue:.4f}\n"
        f"Cohen's d={comparison.cohens_d:.3f}",
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    plt.tight_layout()
    fig.savefig(output_dir / "d_cv_comparison.pdf")
    fig.savefig(output_dir / "d_cv_comparison.png", dpi=150)
    plt.close(fig)

    # Scatter: composite score before vs after
    fig, ax = plt.subplots(figsize=(6, 4))
    n = len(comparison.scores_before)
    ax.scatter(range(n), comparison.scores_before, label="Before", marker="x", color="red")
    ax.scatter(range(n), comparison.scores_after, label="After", marker="o", color="blue")
    ax.set_xlabel("Expression index")
    ax.set_ylabel("Composite Score")
    ax.set_title("Composite Readability Score: Before vs After")
    ax.legend()
    plt.tight_layout()
    fig.savefig(output_dir / "score_comparison.pdf")
    fig.savefig(output_dir / "score_comparison.png", dpi=150)
    plt.close(fig)


def generate_full_report(output_dir: Path) -> None:
    """Run benchmarks, generate tables and plots.

    Args:
        output_dir: Directory for all output files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run benchmark
    results = run_benchmark()
    generate_latex_table(results, output_dir / "benchmark_table.tex")

    print(f"Generated benchmark table with {len(results)} expressions")
    for r in results:
        print(
            f"  [{r.category}] {r.expression[:40]:40s} "
            f"score={r.score.score:.2f} "
            f"crossings={r.score.overlap.crossing_count} "
            f"d_cv={r.score.spacing.d_cv:.3f}"
        )
