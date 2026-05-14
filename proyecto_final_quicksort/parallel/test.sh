#!/bin/bash

# Test script for Hyperquicksort
# This script compiles and runs both sequential and parallel versions

set -e

echo "=========================================="
echo "Hyperquicksort Test Script"
echo "=========================================="

# Check for MPI
if ! command -v mpicxx &> /dev/null; then
    echo "Error: mpicxx not found. Please install MPI."
    echo "  Ubuntu/Debian: sudo apt-get install mpich libmpich-dev"
    echo "  CentOS/RHEL: sudo yum install mpich-devel"
    exit 1
fi

# Compile
echo ""
echo "Compiling..."
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp
g++ -O3 -std=c++17 -o quicksort_seq quicksort_seq.cpp
echo "Compilation successful!"

# Check for data file
if [ ! -f "top_chess_players_aug_2020.csv" ]; then
    echo ""
    echo "Warning: top_chess_players_aug_2020.csv not found!"
    echo "Please ensure the data file is in the current directory."
    exit 1
fi

# Run tests with different processor counts
echo ""
echo "=========================================="
echo "Running Sequential Version"
echo "=========================================="
./quicksort_seq
echo ""

for np in 2 4 8; do
    echo "=========================================="
    echo "Running Parallel Version ($np processors)"
    echo "=========================================="
    mpiexec -np $np ./hyperquicksort
    echo ""
done

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
echo ""
echo "Output files:"
echo "  - sorted_players.csv (sequential)"
echo "  - sorted_players_parallel.csv (parallel)"
