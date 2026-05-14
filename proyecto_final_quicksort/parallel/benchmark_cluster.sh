#!/bin/bash

#SBATCH --job-name=hyperqsort
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=results/benchmark_%j.out
#SBATCH --error=results/benchmark_%j.err

# Load required modules (adjust for your cluster)
module load openmpi

echo "=========================================="
echo "Hyperquicksort Benchmark"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Total tasks: $SLURM_NTASKS"
echo "=========================================="

# Create results directory
mkdir -p results

# Compile
echo "Compiling..."
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp
g++ -O3 -std=c++17 -o quicksort_seq quicksort_seq.cpp

# Clear previous benchmark results
> results/benchmark.csv

echo "=========================================="
echo "Running Sequential Version (3 runs for average)"
echo "=========================================="
for run in {1..3}; do
    echo "Run $run:"
    ./quicksort_seq
    echo ""
done

echo "=========================================="
echo "Running Parallel Versions (1 to 64 processors)"
echo "=========================================="

# Powers of 2 from 1 to 64
PROCESSORS=(1 2 4 8 16 32 64)

for np in "${PROCESSORS[@]}"; do
    echo "=========================================="
    echo "Running with $np processors"
    echo "=========================================="
    mpiexec -np $np ./hyperquicksort
    echo ""
done

echo "=========================================="
echo "Benchmark completed at: $(date)"
echo "Results saved in results/benchmark.csv"
echo "=========================================="
