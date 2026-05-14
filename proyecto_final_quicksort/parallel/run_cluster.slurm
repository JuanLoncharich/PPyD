#!/bin/bash
#SBATCH --job-name=hyperquicksort
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=hyperquicksort_%j.out
#SBATCH --error=hyperquicksort_%j.err

# Load required modules (adjust for your cluster)
# module load openmpi

echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Tasks: $SLURM_NTASKS"
echo "=========================================="

# Compile
echo "Compiling..."
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp

# Run
echo "Running Hyperquicksort with $SLURM_NTASKS processors..."
echo "----------------------------------------"
mpiexec -np $SLURM_NTASKS ./hyperquicksort

echo "----------------------------------------"
echo "Job completed at: $(date)"
