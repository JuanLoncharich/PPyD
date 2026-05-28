#!/usr/bin/env python3
"""
collect_results.py - Parse SLURM output files and extract timing metrics

This script reads all .out files from the results directory and extracts:
- Sequential: generation time, sort time, total time
- Parallel: distribution time, sort time, total time

Results are saved to CSV files for further analysis.
"""

import os
import re
import csv
from pathlib import Path
from typing import Dict, List

# Configuration
SIZES = [100000, 250000, 750000, 2000000, 5000000]
SIZE_NAMES = ["100k", "250k", "750k", "2M", "5M"]
PROCS = [1, 2, 4, 8, 16, 32]
RUNS = [1, 2, 3]

# Patterns to extract from output files
SEQ_PATTERNS = {
    'loaded': re.compile(r'Loaded (\d+) players in ([\d.]+) ms'),
    'sort': re.compile(r'Sorted in ([\d.]+) ms'),
    'total': re.compile(r'Total: ([\d.]+) ms'),
}

PAR_PATTERNS = {
    'loaded': re.compile(r'Loaded (\d+) players across (\d+) processors'),
    'dist': re.compile(r'Distribution time: ([\d.]+) ms'),
    'sort': re.compile(r'Sort time: ([\d.]+) ms'),
    'total': re.compile(r'Total time: ([\d.]+) ms'),
}


def parse_seq_file(filepath: Path) -> Dict:
    """Parse sequential output file."""
    content = filepath.read_text()

    match = SEQ_PATTERNS['loaded'].search(content)
    if not match:
        return None

    loaded = int(match.group(1))
    gen_time = float(match.group(2))

    match = SEQ_PATTERNS['sort'].search(content)
    sort_time = float(match.group(1)) if match else 0.0

    match = SEQ_PATTERNS['total'].search(content)
    total_time = float(match.group(1)) if match else 0.0

    return {
        'loaded': loaded,
        'gen_time_ms': gen_time,
        'sort_time_ms': sort_time,
        'total_time_ms': total_time,
    }


def parse_par_file(filepath: Path) -> Dict:
    """Parse parallel output file."""
    content = filepath.read_text()

    match = PAR_PATTERNS['loaded'].search(content)
    if not match:
        return None

    loaded = int(match.group(1))
    procs = int(match.group(2))

    match = PAR_PATTERNS['dist'].search(content)
    dist_time = float(match.group(1)) if match else 0.0

    match = PAR_PATTERNS['sort'].search(content)
    sort_time = float(match.group(1)) if match else 0.0

    match = PAR_PATTERNS['total'].search(content)
    total_time = float(match.group(1)) if match else 0.0

    return {
        'loaded': loaded,
        'procs': procs,
        'dist_time_ms': dist_time,
        'sort_time_ms': sort_time,
        'total_time_ms': total_time,
    }


def collect_results(results_dir: Path) -> Dict:
    """Collect all results from output files."""
    results = {
        'sequential': {},
        'parallel': {},
    }

    # Collect sequential results
    for size_name in SIZE_NAMES:
        results['sequential'][size_name] = {'sort_time_ms': [], 'total_time_ms': []}

        for run in RUNS:
            filepath = results_dir / f"seq_{size_name}_run{run}.out"
            if filepath.exists():
                data = parse_seq_file(filepath)
                if data:
                    results['sequential'][size_name]['sort_time_ms'].append(data['sort_time_ms'])
                    results['sequential'][size_name]['total_time_ms'].append(data['total_time_ms'])
                    print(f"  ✓ {filepath.name}: sort={data['sort_time_ms']:.2f}ms, total={data['total_time_ms']:.2f}ms")
                else:
                    print(f"  ✗ {filepath.name}: failed to parse")
            else:
                print(f"  - {filepath.name}: not found")

    # Collect parallel results
    for size_name in SIZE_NAMES:
        results['parallel'][size_name] = {}

        for procs in PROCS:
            results['parallel'][size_name][procs] = {
                'dist_time_ms': [],
                'sort_time_ms': [],
                'total_time_ms': [],
            }

            for run in RUNS:
                filepath = results_dir / f"par_{size_name}_p{procs}_run{run}.out"
                if filepath.exists():
                    data = parse_par_file(filepath)
                    if data:
                        results['parallel'][size_name][procs]['dist_time_ms'].append(data['dist_time_ms'])
                        results['parallel'][size_name][procs]['sort_time_ms'].append(data['sort_time_ms'])
                        results['parallel'][size_name][procs]['total_time_ms'].append(data['total_time_ms'])
                        print(f"  ✓ {filepath.name}: sort={data['sort_time_ms']:.2f}ms, total={data['total_time_ms']:.2f}ms")
                    else:
                        print(f"  ✗ {filepath.name}: failed to parse")
                else:
                    print(f"  - {filepath.name}: not found")

    return results


def calculate_statistics(results: Dict) -> Dict:
    """Calculate mean and std dev for each configuration."""
    import statistics

    stats = {
        'sequential': {},
        'parallel': {},
    }

    # Sequential statistics
    for size_name in SIZE_NAMES:
        if results['sequential'][size_name]['sort_time_ms']:
            stats['sequential'][size_name] = {
                'sort_time_ms': {
                    'mean': statistics.mean(results['sequential'][size_name]['sort_time_ms']),
                    'std': statistics.stdev(results['sequential'][size_name]['sort_time_ms']) if len(results['sequential'][size_name]['sort_time_ms']) > 1 else 0.0,
                },
                'total_time_ms': {
                    'mean': statistics.mean(results['sequential'][size_name]['total_time_ms']),
                    'std': statistics.stdev(results['sequential'][size_name]['total_time_ms']) if len(results['sequential'][size_name]['total_time_ms']) > 1 else 0.0,
                },
            }

    # Parallel statistics
    for size_name in SIZE_NAMES:
        stats['parallel'][size_name] = {}

        for procs in PROCS:
            if results['parallel'][size_name][procs]['sort_time_ms']:
                stats['parallel'][size_name][procs] = {
                    'dist_time_ms': {
                        'mean': statistics.mean(results['parallel'][size_name][procs]['dist_time_ms']),
                        'std': statistics.stdev(results['parallel'][size_name][procs]['dist_time_ms']) if len(results['parallel'][size_name][procs]['dist_time_ms']) > 1 else 0.0,
                    },
                    'sort_time_ms': {
                        'mean': statistics.mean(results['parallel'][size_name][procs]['sort_time_ms']),
                        'std': statistics.stdev(results['parallel'][size_name][procs]['sort_time_ms']) if len(results['parallel'][size_name][procs]['sort_time_ms']) > 1 else 0.0,
                    },
                    'total_time_ms': {
                        'mean': statistics.mean(results['parallel'][size_name][procs]['total_time_ms']),
                        'std': statistics.stdev(results['parallel'][size_name][procs]['total_time_ms']) if len(results['parallel'][size_name][procs]['total_time_ms']) > 1 else 0.0,
                    },
                }

    return stats


def save_csv_results(stats: Dict, output_dir: Path):
    """Save results to CSV files."""

    # Sequential results
    with open(output_dir / 'sequential_times.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['size', 'size_name', 'sort_time_ms_mean', 'sort_time_ms_std', 'total_time_ms_mean', 'total_time_ms_std'])

        for i, size_name in enumerate(SIZE_NAMES):
            if size_name in stats['sequential']:
                s = stats['sequential'][size_name]
                writer.writerow([
                    SIZES[i], size_name,
                    s['sort_time_ms']['mean'], s['sort_time_ms']['std'],
                    s['total_time_ms']['mean'], s['total_time_ms']['std'],
                ])

    # Parallel results
    with open(output_dir / 'parallel_times.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['size', 'size_name', 'procs', 'dist_time_ms_mean', 'dist_time_ms_std',
                        'sort_time_ms_mean', 'sort_time_ms_std', 'total_time_ms_mean', 'total_time_ms_std'])

        for i, size_name in enumerate(SIZE_NAMES):
            if size_name in stats['parallel']:
                for procs in PROCS:
                    if procs in stats['parallel'][size_name]:
                        p = stats['parallel'][size_name][procs]
                        writer.writerow([
                            SIZES[i], size_name, procs,
                            p['dist_time_ms']['mean'], p['dist_time_ms']['std'],
                            p['sort_time_ms']['mean'], p['sort_time_ms']['std'],
                            p['total_time_ms']['mean'], p['total_time_ms']['std'],
                        ])


def main():
    # Paths
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / 'results'
    output_dir = script_dir.parent

    print("=== Collecting Results ===")
    print(f"Results directory: {results_dir}")
    print()

    # Check if results directory exists
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run experiments first using run_experiments.sh")
        return

    # Collect results
    print("Parsing output files...")
    results = collect_results(results_dir)

    # Calculate statistics
    print()
    print("Calculating statistics...")
    stats = calculate_statistics(results)

    # Save to CSV
    print()
    print("Saving CSV files...")
    save_csv_results(stats, output_dir)

    print()
    print("=== Summary ===")
    print("Sequential times (sort only):")
    for i, size_name in enumerate(SIZE_NAMES):
        if size_name in stats['sequential']:
            s = stats['sequential'][size_name]
            print(f"  {size_name:>6}: {s['sort_time_ms']['mean']:>10.2f} ± {s['sort_time_ms']['std']:.2f} ms")

    print()
    print("Parallel times (sort only):")
    for i, size_name in enumerate(SIZE_NAMES):
        if size_name in stats['parallel']:
            print(f"  {size_name}:")
            for procs in [2, 4, 8, 16, 32]:
                if procs in stats['parallel'][size_name]:
                    p = stats['parallel'][size_name][procs]
                    print(f"    p{procs:>2}: {p['sort_time_ms']['mean']:>10.2f} ± {p['sort_time_ms']['std']:.2f} ms")

    print()
    print(f"CSV files saved to {output_dir}")
    print("Run 'python plot_results.py' to generate plots")


if __name__ == '__main__':
    main()
