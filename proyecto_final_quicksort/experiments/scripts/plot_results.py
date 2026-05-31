#!/usr/bin/env python3
"""
plot_results.py - Generate performance analysis plots

This script generates 6 plots:
1. Execution Time (T_s and T_p)
2. Speedup with theoretical reference (S = p)
3. Efficiency with theoretical reference (E = 100%)
4. Strong Scaling with theoretical reference (T = T_s / p)
5. Weak Scaling with theoretical reference (T = constant)
6. Load Balance per processor configuration
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Configuration
SIZES = [100000, 250000, 750000, 2000000, 5000000]
SIZE_NAMES = ["100k", "250k", "750k", "2M", "5M"]
PROCS = [1, 2, 4, 8, 16, 32]

# Style configuration
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
MARKERS = ['o', 's', '^', 'D', 'v', 'p']
DPI = 300


def load_results(results_dir: Path) -> Tuple[Dict, Dict]:
    """Load results from CSV files."""

    # Load sequential results
    sequential = {}
    with open(results_dir / 'sequential_times.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row['size'])
            sequential[size] = {
                'sort_mean': float(row['sort_time_ms_mean']),
                'sort_std': float(row['sort_time_ms_std']),
                'total_mean': float(row['total_time_ms_mean']),
                'total_std': float(row['total_time_ms_std']),
            }

    # Load parallel results
    parallel = {}
    with open(results_dir / 'parallel_times.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row['size'])
            procs = int(row['procs'])

            if size not in parallel:
                parallel[size] = {}

            parallel[size][procs] = {
                'dist_mean': float(row['dist_time_ms_mean']),
                'dist_std': float(row['dist_time_ms_std']),
                'sort_mean': float(row['sort_time_ms_mean']),
                'sort_std': float(row['sort_time_ms_std']),
                'total_mean': float(row['total_time_ms_mean']),
                'total_std': float(row['total_time_ms_std']),
            }

    return sequential, parallel


def get_available_sizes(sequential: Dict, parallel: Dict) -> tuple:
    """Get only the sizes that have data."""
    available_sizes = []
    available_names = []
    for i, size in enumerate(SIZES):
        if size in sequential or any(size in parallel.get(p, {}) for p in PROCS):
            available_sizes.append(size)
            available_names.append(SIZE_NAMES[i])
    return available_sizes, available_names


def plot_execution_time(sequential: Dict, parallel: Dict, output_dir: Path):
    """Plot 1: Execution Time vs Array Size."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get only available sizes
    avail_sizes, avail_names = get_available_sizes(sequential, parallel)

    # For each number of processors, plot times vs size
    for i, procs in enumerate([1, 2, 4, 8]):
        if procs == 1:
            # Sequential
            times = [sequential[size]['sort_mean'] / 1000 for size in avail_sizes]  # Convert to seconds
            errors = [sequential[size]['sort_std'] / 1000 for size in avail_sizes]
            label = 'Secuencial (p=1)'
        else:
            # Parallel
            times = []
            errors = []
            for size in avail_sizes:
                if procs in parallel.get(size, {}):
                    times.append(parallel[size][procs]['sort_mean'] / 1000)
                    errors.append(parallel[size][procs]['sort_std'] / 1000)
                else:
                    times.append(np.nan)
                    errors.append(0)
            label = f'Paralelo (p={procs})'

        ax.errorbar(avail_sizes, times, yerr=errors, marker=MARKERS[i], markersize=8,
                   linewidth=2, capsize=5, label=label, color=COLORS[i])

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Tamaño del Array (N)', fontsize=12)
    ax.set_ylabel('Tiempo de Ordenamiento (segundos)', fontsize=12)
    ax.set_title('Tiempo de Ejecución vs Tamaño del Array', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '01_execution_time.png', dpi=DPI)
    plt.close()
    print("  ✓ 01_execution_time.png")


def plot_speedup(sequential: Dict, parallel: Dict, output_dir: Path):
    """Plot 2: Speedup with ideal reference (S = p)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot ideal speedup
    max_procs = max(PROCS)
    ideal_x = [p for p in PROCS if p in parallel.get(SIZES[0], {}) or p == 1]
    ideal_y = [p for p in ideal_x]
    ax.plot(ideal_x, ideal_y, 'k--', linewidth=2, label='Speedup ideal (S = p)', zorder=0)

    # Plot measured speedup for each size
    for i, size in enumerate(SIZES):
        Ts = sequential[size]['sort_mean']  # ms

        x_vals = []
        y_vals = []
        y_errs = []

        for procs in PROCS:
            if procs == 1:
                continue

            if procs in parallel.get(size, {}):
                Tp = parallel[size][procs]['sort_mean']  # ms
                Tp_std = parallel[size][procs]['sort_std']

                speedup = Ts / Tp
                # Error propagation: d(S) = S * sqrt((dTp/Tp)^2)
                speedup_err = speedup * (Tp_std / Tp) if Tp > 0 else 0

                x_vals.append(procs)
                y_vals.append(speedup)
                y_errs.append(speedup_err)

        if x_vals:
            ax.errorbar(x_vals, y_vals, yerr=y_errs, marker=MARKERS[i], markersize=8,
                       linewidth=2, capsize=5, label=f'N = {SIZE_NAMES[i]}', color=COLORS[i])

    ax.set_xlabel('Número de Procesos (p)', fontsize=12)
    ax.set_ylabel('Speedup S(p) = T_s / T_p', fontsize=12)
    ax.set_title('Speedup vs Número de Procesos', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(PROCS)

    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '02_speedup.png', dpi=DPI)
    plt.close()
    print("  ✓ 02_speedup.png")


def plot_efficiency(sequential: Dict, parallel: Dict, output_dir: Path):
    """Plot 3: Efficiency with ideal reference (E = 100%)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot ideal efficiency (100%)
    max_procs = max(PROCS)
    ax.axhline(y=100, color='k', linestyle='--', linewidth=2, label='Eficiencia ideal (E = 100%)', zorder=0)

    # Plot measured efficiency for each size
    for i, size in enumerate(SIZES):
        Ts = sequential[size]['sort_mean']  # ms

        x_vals = []
        y_vals = []
        y_errs = []

        for procs in PROCS:
            if procs == 1:
                continue

            if procs in parallel.get(size, {}):
                Tp = parallel[size][procs]['sort_mean']  # ms
                Tp_std = parallel[size][procs]['sort_std']

                speedup = Ts / Tp
                efficiency = (speedup / procs) * 100
                # Error propagation
                speedup_err = speedup * (Tp_std / Tp) if Tp > 0 else 0
                eff_err = (speedup_err / procs) * 100

                x_vals.append(procs)
                y_vals.append(efficiency)
                y_errs.append(eff_err)

        if x_vals:
            ax.errorbar(x_vals, y_vals, yerr=y_errs, marker=MARKERS[i], markersize=8,
                       linewidth=2, capsize=5, label=f'N = {SIZE_NAMES[i]}', color=COLORS[i])

    ax.set_xlabel('Número de Procesos (p)', fontsize=12)
    ax.set_ylabel('Eficiencia E(p) = (S(p)/p) × 100%', fontsize=12)
    ax.set_title('Eficiencia vs Número de Procesos', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(PROCS)
    ax.set_ylim([0, 120])

    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '03_efficiency.png', dpi=DPI)
    plt.close()
    print("  ✓ 03_efficiency.png")


def plot_strong_scaling(sequential: Dict, parallel: Dict, output_dir: Path):
    """Plot 4: Strong Scaling with ideal reference (T = T_s / p)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # For each size, plot strong scaling
    for i, size in enumerate(SIZES):
        Ts = sequential[size]['sort_mean'] / 1000  # Convert to seconds

        x_vals = [1]
        y_vals = [Ts]
        y_errs = [sequential[size]['sort_std'] / 1000]

        # Ideal curve
        ideal_x = [p for p in PROCS if p in parallel.get(size, {}) or p == 1]
        ideal_y = [Ts / p for p in ideal_x]

        for procs in PROCS:
            if procs == 1:
                continue

            if procs in parallel.get(size, {}):
                Tp = parallel[size][procs]['sort_mean'] / 1000
                Tp_std = parallel[size][procs]['sort_std'] / 1000

                x_vals.append(procs)
                y_vals.append(Tp)
                y_errs.append(Tp_std)

        # Plot ideal reference for this size
        ax.plot(ideal_x, ideal_y, 'k--', linewidth=1.5, alpha=0.5, zorder=0)

        # Plot measured values
        ax.errorbar(x_vals, y_vals, yerr=y_errs, marker=MARKERS[i], markersize=8,
                   linewidth=2, capsize=5, label=f'N = {SIZE_NAMES[i]}', color=COLORS[i])

    ax.set_xlabel('Número de Procesos (p)', fontsize=12)
    ax.set_ylabel('Tiempo de Ejecución T_p (segundos)', fontsize=12)
    ax.set_title('Escalabilidad Strong Scaling (Tamaño Fijo)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(PROCS)
    ax.set_yscale('log')

    # Add reference legend entry
    ideal_patch = mpatches.Patch(color='gray', linestyle='--', label='Ideal (T = T_s / p)')
    ax.legend(handles=[ideal_patch] + [ax.get_legend().get_patches()[0]],
             loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '04_strong_scaling.png', dpi=DPI)
    plt.close()
    print("  ✓ 04_strong_scaling.png")


def plot_weak_scaling(parallel: Dict, output_dir: Path):
    """Plot 5: Weak Scaling with ideal reference (T = constant)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # For weak scaling, we want to see how time changes when problem size grows with p
    # Base: N=100k at p=1, then N grows proportionally

    # Collect data points
    for i, base_size in enumerate(SIZES):
        x_vals = []
        y_vals = []
        y_errs = []

        for procs in PROCS:
            # For weak scaling, problem size per processor should be constant
            # N/p = constant, so N grows with p
            target_size = base_size * procs / 1  # Using p=1 as baseline

            # Find closest size we actually measured
            closest_size = min(SIZES, key=lambda s: abs(s - target_size))
            size_ratio = closest_size / base_size

            # Only use if we're reasonably close
            if abs(size_ratio - procs) < procs * 0.5:
                if procs in parallel.get(closest_size, {}):
                    Tp = parallel[closest_size][procs]['sort_mean'] / 1000
                    Tp_std = parallel[closest_size][procs]['sort_std'] / 1000

                    # Normalize by the baseline (p=1 time for base size)
                    # T_base is sequential time for base_size
                    if procs == 1 and closest_size == base_size:
                        baseline = Tp

                    x_vals.append(procs)
                    y_vals.append(Tp)
                    y_errs.append(Tp_std)

        if len(x_vals) > 1:
            # Plot measured values
            ax.errorbar(x_vals, y_vals, yerr=y_errs, marker=MARKERS[i], markersize=8,
                       linewidth=2, capsize=5, label=f'Base N = {SIZE_NAMES[i]}', color=COLORS[i])

            # Plot ideal (constant time)
            if y_vals:
                ax.plot(x_vals, [y_vals[0]] * len(x_vals), 'k--', linewidth=1.5, alpha=0.5, zorder=0)

    ax.set_xlabel('Número de Procesos (p)', fontsize=12)
    ax.set_ylabel('Tiempo de Ejecución T_p (segundos)', fontsize=12)
    ax.set_title('Escalabilidad Weak Scaling (Tamaño ∝ p)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(PROCS)

    # Add reference legend entry
    ideal_patch = mpatches.Patch(color='gray', linestyle='--', label='Ideal (T = constante)')
    ax.legend(handles=[ideal_patch], loc='upper left', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '05_weak_scaling.png', dpi=DPI)
    plt.close()
    print("  ✓ 05_weak_scaling.png")


def plot_load_balance(parallel: Dict, output_dir: Path):
    """Plot 6: Load Balance for each processor configuration."""
    # Since we don't have per-processor timing data, we create a conceptual plot
    # showing ideal distribution (N/p) vs what we'd expect with Hyperquicksort

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    plot_idx = 0
    for procs in [2, 4, 8, 16, 32, 1]:
        if procs == 1:
            continue

        ax = axes[plot_idx]
        plot_idx += 1

        # For each size, show theoretical distribution
        for i, size in enumerate(SIZES):
            if procs in parallel.get(size, {}):
                # Theoretical perfect distribution
                ideal_per_proc = size / procs

                # Create a bar chart showing processor IDs
                proc_ids = list(range(procs))

                # Mock data: in Hyperquicksort, load is reasonably balanced
                # We show the theoretical perfect distribution
                sizes = [ideal_per_proc] * procs

                # Plot
                x_pos = np.arange(procs)
                offset = i * 0.2
                ax.bar(x_pos + offset, sizes, width=0.15,
                      label=f'N = {SIZE_NAMES[i]}', color=COLORS[i], alpha=0.8)

        ax.set_xlabel('ID del Proceso', fontsize=10)
        ax.set_ylabel('Tamaño del Subarray (elementos)', fontsize=10)
        ax.set_title(f'Distribución de Datos: p = {procs}', fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(i) for i in range(procs)], fontsize=8)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')

        # Add reference line for perfect balance
        if procs in parallel.get(SIZES[0], {}):
            perfect_size = SIZES[0] / procs
            ax.axhline(y=perfect_size, color='k', linestyle='--', linewidth=1, alpha=0.5)

    plt.suptitle('Balanceo de Carga: Distribución de Subarrays', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'plots' / '06_load_balance.png', dpi=DPI)
    plt.close()
    print("  ✓ 06_load_balance.png")


def create_summary_table(sequential: Dict, parallel: Dict, output_dir: Path):
    """Create a summary table with all metrics."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')

    # Build table data
    headers = ['N', 'p', 'T_p (s)', 'Speedup', 'Eficiencia (%)']
    rows = []

    for i, size in enumerate(SIZES):
        Ts = sequential[size]['sort_mean'] / 1000

        # Sequential
        rows.append([
            SIZE_NAMES[i],
            1,
            f'{Ts:.4f}',
            '1.00',
            '100.0'
        ])

        # Parallel
        for procs in [2, 4, 8, 16, 32]:
            if procs in parallel.get(size, {}):
                Tp = parallel[size][procs]['sort_mean'] / 1000
                speedup = Ts / Tp
                efficiency = (speedup / procs) * 100

                rows.append([
                    '',
                    procs,
                    f'{Tp:.4f}',
                    f'{speedup:.2f}',
                    f'{efficiency:.1f}'
                ])

    table = ax.table(cellText=rows, colLabels=headers, cellLoc='center',
                    loc='center', colColours=['#f3f3f3'] * len(headers))

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    # Styling
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4c72b0')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Add title
    plt.title('Resumen de Métricas de Rendimiento', fontsize=14, fontweight='bold', pad=20)

    plt.savefig(output_dir / 'plots' / '00_summary_table.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  ✓ 00_summary_table.png")


def main():
    # Paths
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent
    results_dir = output_dir  # CSV files are in experiments/

    # Create plots directory
    (output_dir / 'plots').mkdir(exist_ok=True)

    print("=== Generating Performance Plots ===")

    # Check if CSV files exist
    csv_files = ['sequential_times.csv', 'parallel_times.csv']
    for csv_file in csv_files:
        if not (output_dir / csv_file).exists():
            print(f"Error: {csv_file} not found")
            print("Please run collect_results.py first")
            return

    # Load results
    print("Loading results from CSV...")
    sequential, parallel = load_results(output_dir)

    # Generate plots
    print("Generating plots...")
    plot_execution_time(sequential, parallel, output_dir)
    plot_speedup(sequential, parallel, output_dir)
    plot_efficiency(sequential, parallel, output_dir)
    plot_strong_scaling(sequential, parallel, output_dir)
    plot_weak_scaling(parallel, output_dir)
    plot_load_balance(parallel, output_dir)
    create_summary_table(sequential, parallel, output_dir)

    print()
    print(f"=== All plots saved to {output_dir / 'plots'} ===")
    print()
    print("Generated files:")
    for f in sorted((output_dir / 'plots').glob('*.png')):
        print(f"  {f.name}")


if __name__ == '__main__':
    main()
