import matplotlib.pyplot as plt
import json
import numpy as np
import argparse
from pathlib import Path


def calculate_stats(values):
    """Calculate mean and 95% confidence interval.

    Args:
        values: List of numeric values

    Returns:
        Tuple of (mean, error) where error is the 95% CI half-width
    """
    values = np.array(values)
    mean = np.mean(values)
    # 95% CI using t-distribution for small samples
    n = len(values)
    if n > 1:
        std_err = np.std(values, ddof=1) / np.sqrt(n)
        # For 95% CI with small samples, use t-value ~ 2 (conservative)
        # More precisely: scipy.stats.t.ppf(0.975, n-1) but we'll use 1.96 for normal approx
        t_value = 1.96 if n > 30 else 2.0
        error = t_value * std_err
    else:
        error = 0
    return mean, error


def load_and_analyze_results(json_path):
    """Load benchmark results from JSON and calculate statistics.

    Args:
        json_path: Path to the benchmark result JSON file

    Returns:
        Dictionary with statistics
    """
    with open(json_path, 'r') as f:
        results = json.load(f)

    # Extract metrics
    scores = []
    times = []
    tokens = []
    human_reasonable = []
    judge_reasonable = []

    for result in results:
        scores.append(result['lm_score_output'])
        times.append(result['lm_score_time_seconds'])
        tokens.append(result['lm_score_tokens'])
        human_reasonable.append(1 if result['human_evaluation']['reasonable'] else 0)

        # Parse judge judgment
        judgment = result['lm_judge_evaluation']['judgment'].lower()
        if 'reasonable' in judgment and 'unreasonable' not in judgment:
            judge_reasonable.append(1)
        else:
            judge_reasonable.append(0)

    # Calculate statistics
    score_mean, score_err = calculate_stats(scores)
    time_mean, time_err = calculate_stats(times)
    token_mean, token_err = calculate_stats(tokens)

    # For binary metrics (human/judge), calculate proportion
    human_accuracy = np.mean(human_reasonable) * 100  # as percentage
    judge_accuracy = np.mean(judge_reasonable) * 100  # as percentage

    # Calculate standard error for proportions
    n = len(human_reasonable)
    human_prop = np.mean(human_reasonable)
    judge_prop = np.mean(judge_reasonable)
    human_err = 1.96 * np.sqrt(human_prop * (1 - human_prop) / n) * 100
    judge_err = 1.96 * np.sqrt(judge_prop * (1 - judge_prop) / n) * 100

    return {
        'score': {'mean': score_mean, 'error': score_err, 'values': scores},
        'time': {'mean': time_mean, 'error': time_err, 'values': times},
        'tokens': {'mean': token_mean, 'error': token_err, 'values': tokens},
        'human_accuracy': {'mean': human_accuracy, 'error': human_err},
        'judge_accuracy': {'mean': judge_accuracy, 'error': judge_err},
        'n_samples': n
    }


# Legacy hardcoded results for comparison (optional)
legacy_results = {
    "Predict, one pass": {
        "time": 370.11,  # 6:10.11
        "score": 27/30,
        "tokens": 406.62
    },
    "Predict, suppress thinking, one pass": {
        "time": 68,  # 1:08
        "score": 19/30,
        "tokens": 78.50
    },
    "Predict, suppress thinking, 3 passes, majority vote": {
        "time": 230.38,  # 3:50:38
        "score": 23/30,
        "tokens": 237.97
    },
    "Predict, suppress thinking, 3 passes, average": {
        "time": 209.47,  # 3:29.47
        "score": 25/30,
        "tokens": 237.97
    }
}


def create_visualization(json_paths, output_path=None):
    """Create visualization from benchmark results JSON(s).

    Args:
        json_paths: Single path or list of paths to benchmark result JSON files
        output_path: Optional path to save the figure
    """
    # Handle single path or list of paths
    if isinstance(json_paths, str):
        json_paths = [json_paths]

    # Load and analyze all results
    all_stats = []
    method_names = []
    for json_path in json_paths:
        stats = load_and_analyze_results(json_path)
        all_stats.append(stats)
        method_name = Path(json_path).stem.replace('_benchmark_result', '')
        method_names.append(method_name)

    n_methods = len(all_stats)

    # Calculate global y-limits across all methods for aligned axes
    max_time = max(s['time']['mean'] + s['time']['error'] for s in all_stats)
    max_tokens = max(s['tokens']['mean'] + s['tokens']['error'] for s in all_stats)

    # Create figure with 4 rows and n_methods columns
    fig, axes = plt.subplots(4, n_methods, figsize=(5 * n_methods, 12))

    # Handle single method case (axes won't be 2D)
    if n_methods == 1:
        axes = axes.reshape(-1, 1)

    fig.suptitle('LM-Score Benchmark Comparison', fontsize=16, fontweight='bold')

    # Color scheme
    colors = ['forestgreen', 'royalblue', 'steelblue', 'coral']

    # Plot each method
    for col, (stats, method_name) in enumerate(zip(all_stats, method_names)):
        x_pos = [0]

        # Chart 1: LM-Judge Accuracy
        judge_mean = stats['judge_accuracy']['mean']
        judge_err = stats['judge_accuracy']['error']
        axes[0, col].bar(x_pos, [judge_mean], yerr=[judge_err], color=colors[0], alpha=0.7, capsize=10, width=0.4)
        axes[0, col].set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        axes[0, col].set_title(f'{method_name}\n{judge_mean:.1f}% ± {judge_err:.1f}% (n={stats["n_samples"]})',
                               fontsize=12, pad=10)
        axes[0, col].set_ylim(0, 110)  # Same scale for all
        axes[0, col].set_xticks([])
        axes[0, col].grid(axis='y', alpha=0.3)

        # Chart 2: Human Accuracy
        human_mean = stats['human_accuracy']['mean']
        human_err = stats['human_accuracy']['error']
        axes[1, col].bar(x_pos, [human_mean], yerr=[human_err], color=colors[1], alpha=0.7, capsize=10, width=0.4)
        axes[1, col].set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        axes[1, col].set_title(f'{human_mean:.1f}% ± {human_err:.1f}%', fontsize=12, pad=10)
        axes[1, col].set_ylim(0, 110)  # Same scale for all
        axes[1, col].set_xticks([])
        axes[1, col].grid(axis='y', alpha=0.3)

        # Chart 3: Time comparison
        time_mean = stats['time']['mean']
        time_err = stats['time']['error']
        axes[2, col].bar(x_pos, [time_mean], yerr=[time_err], color=colors[2], alpha=0.7, capsize=10, width=0.4)
        axes[2, col].set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
        axes[2, col].set_title(f'{time_mean:.2f}s ± {time_err:.2f}s', fontsize=12, pad=10)
        axes[2, col].set_ylim(0, max_time * 1.2)  # Aligned across all methods
        axes[2, col].set_xticks([])
        axes[2, col].grid(axis='y', alpha=0.3)

        # Chart 4: Token comparison
        token_mean = stats['tokens']['mean']
        token_err = stats['tokens']['error']
        axes[3, col].bar(x_pos, [token_mean], yerr=[token_err], color=colors[3], alpha=0.7, capsize=10, width=0.4)
        axes[3, col].set_ylabel('Tokens', fontsize=12, fontweight='bold')
        axes[3, col].set_title(f'{token_mean:.1f} ± {token_err:.1f}', fontsize=12, pad=10)
        axes[3, col].set_ylim(0, max_tokens * 1.2)  # Aligned across all methods
        axes[3, col].set_xticks([])
        axes[3, col].grid(axis='y', alpha=0.3)

    # Add row labels on the left
    row_labels = ['LM-Judge Evaluation:\n% Judged Reasonable', 'Human Evaluation:\n% Judged Reasonable',
                  'Average Execution Time', 'Average Token Usage']
    for row, label in enumerate(row_labels):
        axes[row, 0].set_ylabel(label, fontsize=13, fontweight='bold')

    # Adjust layout and save
    plt.tight_layout()

    if output_path is None:
        if n_methods == 1:
            output_path = str(Path(json_paths[0]).parent / f'{method_names[0]}_visualization.png')
        else:
            output_path = 'analysis/benchmark_comparison.png'

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_path}")

    # Create per-problem stacked bar chart if multiple methods
    if n_methods > 1:
        create_per_problem_visualization(json_paths, method_names, output_path)

    # Print summary statistics for all methods
    print(f"\n{'='*80}")
    print(f"Summary Statistics")
    print(f"{'='*80}")
    for stats, method_name in zip(all_stats, method_names):
        print(f"\n{method_name}:")
        print(f"  Sample Size: {stats['n_samples']}")
        print(f"  Average LM_SCORE Output: {stats['score']['mean']:.2f} ± {stats['score']['error']:.2f}")
        print(f"  Human Accuracy: {stats['human_accuracy']['mean']:.1f}% ± {stats['human_accuracy']['error']:.1f}%")
        print(f"  LM-Judge Accuracy: {stats['judge_accuracy']['mean']:.1f}% ± {stats['judge_accuracy']['error']:.1f}%")
        print(f"  Average Time: {stats['time']['mean']:.2f}s ± {stats['time']['error']:.2f}s")
        print(f"  Average Tokens: {stats['tokens']['mean']:.1f} ± {stats['tokens']['error']:.1f}")
    print(f"{'='*80}\n")

    plt.show()


def create_per_problem_visualization(json_paths, method_names, base_output_path):
    """Create stacked bar chart showing which methods solved each problem.

    Args:
        json_paths: List of paths to benchmark result JSON files
        method_names: List of method names
        base_output_path: Base path for output file
    """
    # Load all results
    all_results = []
    for json_path in json_paths:
        with open(json_path, 'r') as f:
            results = json.load(f)
        all_results.append(results)

    n_methods = len(method_names)
    n_problems = len(all_results[0])

    # Define color palette
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#8e44ad', '#f39c12', '#1abc9c', '#e67e22', '#34495e']
    method_colors = colors[:n_methods]

    # Create matrices: problems x methods (1 if solved, 0 if not)
    # One for LM-judge evaluation, one for human evaluation
    judge_matrix = np.zeros((n_problems, n_methods))
    human_matrix = np.zeros((n_problems, n_methods))

    for method_idx, results in enumerate(all_results):
        for problem_idx, result in enumerate(results):
            # Human evaluation
            if result['human_evaluation']['reasonable']:
                human_matrix[problem_idx, method_idx] = 1

            # LM-judge evaluation
            judgment = result['lm_judge_evaluation']['judgment'].lower()
            if 'reasonable' in judgment and 'unreasonable' not in judgment:
                judge_matrix[problem_idx, method_idx] = 1

    # Create figure with 2 subplots (2 rows, 1 column)
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle('Per-Problem Success: Which Methods Solved Each Problem',
                 fontsize=18, fontweight='bold', y=0.995)

    # Problem indices (x-axis)
    problem_indices = np.arange(n_problems)
    bar_width = 0.8

    # ============================================================================
    # SUBPLOT 1: LM-as-Judge Evaluation
    # ============================================================================
    ax1 = axes[0]
    bottom = np.zeros(n_problems)
    # Stack in reverse order (last method at bottom, first at top)
    for method_idx in reversed(range(n_methods)):
        ax1.bar(problem_indices, judge_matrix[:, method_idx], bar_width,
                bottom=bottom, label=method_names[method_idx],
                color=method_colors[method_idx], alpha=0.8)
        bottom += judge_matrix[:, method_idx]

    ax1.set_ylabel('Number of Methods\nthat Solved Problem', fontsize=12, fontweight='bold')
    ax1.set_title('Based on LM-as-Judge Evaluation', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xticks(problem_indices)
    ax1.set_xticklabels([])  # No x-labels on top plot
    ax1.set_ylim(0, n_methods + 0.5)
    ax1.set_yticks(range(n_methods + 1))

    # Keep legend in original order (reversed from stacking order)
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[::-1], labels[::-1], loc='upper right', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)

    # ============================================================================
    # SUBPLOT 2: Human Evaluation
    # ============================================================================
    ax2 = axes[1]
    bottom = np.zeros(n_problems)
    # Stack in reverse order (last method at bottom, first at top)
    for method_idx in reversed(range(n_methods)):
        ax2.bar(problem_indices, human_matrix[:, method_idx], bar_width,
                bottom=bottom, label=method_names[method_idx],
                color=method_colors[method_idx], alpha=0.8)
        bottom += human_matrix[:, method_idx]

    ax2.set_xlabel('Problem Index', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Methods\nthat Solved Problem', fontsize=12, fontweight='bold')
    ax2.set_title('Based on Human Evaluation', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xticks(problem_indices)
    ax2.set_xticklabels([f'{i}' for i in range(n_problems)], fontsize=8)
    ax2.set_ylim(0, n_methods + 0.5)
    ax2.set_yticks(range(n_methods + 1))

    # Keep legend in original order (reversed from stacking order)
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles[::-1], labels[::-1], loc='upper right', fontsize=11)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # Save with modified filename
    output_path = Path(base_output_path).parent / (Path(base_output_path).stem + '_per_problem.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Per-problem visualization saved to: {output_path}")

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize LM-Score benchmark results")
    parser.add_argument(
        "json_files",
        type=str,
        nargs='+',
        help="Path(s) to benchmark result JSON file(s) (e.g., 'out/test1_benchmark_result.json out/test2_benchmark_result.json')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for visualization (default: auto-generated based on input filename)"
    )

    args = parser.parse_args()

    # Check that all files exist
    for json_file in args.json_files:
        if not Path(json_file).exists():
            print(f"Error: File not found: {json_file}")
            exit(1)

    create_visualization(args.json_files, args.output)
