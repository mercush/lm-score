import matplotlib.pyplot as plt

results = {
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

# Extract data for plotting
methods = list(results.keys())
times = [results[m]["time"] for m in methods]
scores = [results[m]["score"] * 100 for m in methods]  # Convert to percentage
tokens = [results[m]["tokens"] for m in methods]

# Create figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(12, 10))
fig.suptitle('LM-Score Benchmark Comparison', fontsize=16, fontweight='bold')

# Shorten method names for better display
short_methods = [
    "Predict\n1 pass",
    "Predict\nSuppress\n1 pass",
    "Predict\nSuppress\n3 pass\nMajority",
    "Predict\nSuppress\n3 pass\nAverage"
]

# Chart 1: Time comparison
axes[0].bar(short_methods, times, color='steelblue', alpha=0.7)
axes[0].set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
axes[0].set_title('Execution Time', fontsize=14)
axes[0].grid(axis='y', alpha=0.3)
for i, (method, time) in enumerate(zip(short_methods, times)):
    axes[0].text(i, time + 10, f'{time:.1f}s', ha='center', va='bottom', fontsize=10)

# Chart 2: Score comparison
axes[1].bar(short_methods, scores, color='forestgreen', alpha=0.7)
axes[1].set_ylabel('Score (%)', fontsize=12, fontweight='bold')
axes[1].set_title('Accuracy Score', fontsize=14)
axes[1].set_ylim(0, 100)
axes[1].grid(axis='y', alpha=0.3)
axes[1].legend()
for i, (method, score) in enumerate(zip(short_methods, scores)):
    axes[1].text(i, score + 2, f'{score:.1f}%', ha='center', va='bottom', fontsize=10)

# Chart 3: Token comparison
axes[2].bar(short_methods, tokens, color='coral', alpha=0.7)
axes[2].set_ylabel('Tokens', fontsize=12, fontweight='bold')
axes[2].set_title('Token Usage', fontsize=14)
axes[2].grid(axis='y', alpha=0.3)
for i, (method, token) in enumerate(zip(short_methods, tokens)):
    axes[2].text(i, token + 5, f'{token:.1f}', ha='center', va='bottom', fontsize=10)

# Adjust layout and save
plt.tight_layout()
plt.savefig('analysis/benchmark_comparison.png', dpi=300, bbox_inches='tight')
print("Chart saved to analysis/benchmark_comparison.png")
plt.show()
