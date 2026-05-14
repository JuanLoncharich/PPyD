#!/usr/bin/env python3
"""
Generate performance graphs for Hyperquicksort benchmark results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Create results directory if it doesn't exist
os.makedirs('results', exist_ok=True)

# Read benchmark data
try:
    df = pd.read_csv('results/benchmark.csv')
except FileNotFoundError:
    print("Error: results/benchmark.csv not found. Run the benchmark first.")
    exit(1)

# Sort by number of processors
df = df.sort_values('processors')

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Hyperquicksort Performance Analysis', fontsize=16, fontweight='bold')

# 1. Sort Time vs Processors (log scale on x-axis)
ax1 = axes[0, 0]
ax1.plot(df['processors'], df['sort_time_ms'], 'o-', linewidth=2, markersize=8, color='#2E86AB')
ax1.set_xscale('log', base=2)
ax1.set_xlabel('Number of Processors', fontsize=11)
ax1.set_ylabel('Sort Time (ms)', fontsize=11)
ax1.set_title('Sort Time vs Processors (Log Scale)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(df['processors'])
ax1.set_xticklabels(df['processors'])

# 2. Speedup Analysis
ax2 = axes[0, 1]
seq_time = df[df['processors'] == 1]['sort_time_ms'].values[0]
speedup = seq_time / df['sort_time_ms']
ideal = df['processors']
ax2.plot(df['processors'], speedup, 'o-', linewidth=2, markersize=8, color='#A23B72', label='Actual Speedup')
ax2.plot(df['processors'], ideal, '--', linewidth=1.5, color='gray', label='Ideal Speedup')
ax2.set_xscale('log', base=2)
ax2.set_xlabel('Number of Processors', fontsize=11)
ax2.set_ylabel('Speedup', fontsize=11)
ax2.set_title('Speedup Analysis', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xticks(df['processors'])
ax2.set_xticklabels(df['processors'])

# 3. Efficiency
ax3 = axes[1, 0]
efficiency = (speedup / df['processors']) * 100
ax3.plot(df['processors'], efficiency, 's-', linewidth=2, markersize=8, color='#F18F01')
ax3.set_xscale('log', base=2)
ax3.set_xlabel('Number of Processors', fontsize=11)
ax3.set_ylabel('Efficiency (%)', fontsize=11)
ax3.set_title('Parallel Efficiency', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.set_xticks(df['processors'])
ax3.set_xticklabels(df['processors'])
ax3.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5)

# 4. Total Time Comparison
ax4 = axes[1, 1]
ax4.plot(df['processors'], df['total_time_ms'], 'o-', linewidth=2, markersize=8, color='#C73E1D')
ax4.set_xscale('log', base=2)
ax4.set_xlabel('Number of Processors', fontsize=11)
ax4.set_ylabel('Total Time (ms)', fontsize=11)
ax4.set_title('Total Execution Time (including distribution)', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.set_xticks(df['processors'])
ax4.set_xticklabels(df['processors'])

plt.tight_layout()
plt.savefig('results/performance_graphs.png', dpi=300, bbox_inches='tight')
print("Graphs saved to results/performance_graphs.png")

# Create a separate speedup/efficiency table
fig2, ax = plt.subplots(figsize=(10, 6))
ax.axis('tight')
ax.axis('off')

table_data = []
for _, row in df.iterrows():
    np_val = int(row['processors'])
    sp = seq_time / row['sort_time_ms']
    eff = (sp / np_val) * 100
    table_data.append([np_val,
                      f"{row['sort_time_ms']:.2f}",
                      f"{sp:.2f}",
                      f"{eff:.1f}%"])

table = ax.table(cellText=table_data,
                colLabels=['Processors', 'Sort Time (ms)', 'Speedup', 'Efficiency'],
                cellLoc='center',
                loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

# Style the header
for i in range(4):
    table[(0, i)].set_facecolor('#4472C4')
    table[(0, i)].set_text_props(weight='bold', color='white')

plt.title('Hyperquicksort Performance Summary', fontsize=14, fontweight='bold', pad=20)
plt.savefig('results/performance_table.png', dpi=300, bbox_inches='tight')
print("Table saved to results/performance_table.png")

# Create a combined comparison graph
fig3, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(df))
width = 0.35

bars1 = ax.bar(x - width/2, df['sort_time_ms'], width, label='Sort Time', color='#2E86AB')
bars2 = ax.bar(x + width/2, df['total_time_ms'] - df['distribution_time_ms'],
               width, label='Communication Overhead', color='#F18F01')

ax.set_xlabel('Number of Processors', fontsize=12)
ax.set_ylabel('Time (ms)', fontsize=12)
ax.set_title('Time Breakdown by Processor Count', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df['processors'])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=8)

for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=8)

plt.tight_layout()
plt.savefig('results/time_breakdown.png', dpi=300, bbox_inches='tight')
print("Time breakdown saved to results/time_breakdown.png")

print("\n========================================")
print("All graphs generated successfully!")
print("========================================")
print("Files created:")
print("  - results/performance_graphs.png")
print("  - results/performance_table.png")
print("  - results/time_breakdown.png")
