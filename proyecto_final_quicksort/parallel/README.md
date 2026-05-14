# Parallel Hyperquicksort Implementation

Parallel implementation of quicksort using the Hyperquicksort algorithm with MPI for cluster computing.

## Files

- `hyperquicksort.cpp` - Parallel Hyperquicksort implementation using MPI
- `quicksort_seq.cpp` - Original sequential quicksort (for comparison)
- `benchmark_cluster.sh` - SLURM script for full benchmark (1-64 processors)
- `generate_graphs.py` - Python script to generate performance graphs
- `Makefile` - Build configuration with benchmark and graph targets
- `run_cluster.slurm` - Simple SLURM script for single test run

## Algorithm: Hyperquicksort

Hyperquicksort is a parallel sorting algorithm based on the hypercube communication pattern:

1. **Initial Distribution**: Data is distributed across processors using round-robin
2. **Local Sort**: Each processor sorts its local data independently
3. **Hypercube Communication**: For each dimension d = 0 to log₂(p)-1:
   - Processors are paired (each processor pairs with one that has bit d flipped)
   - A pivot is selected (average of medians)
   - Data is exchanged between paired processors
   - Each processor keeps elements that belong to its partition
4. **Final Gather**: Results are gathered on rank 0

## Building

### On a cluster with MPI:
```bash
module load openmpi  # or your cluster's MPI module
make
```

Or manually:
```bash
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp
g++ -O3 -std=c++17 -o quicksort_seq quicksort_seq.cpp
```

## Running

### Quick Test (Local)
```bash
# Sequential version
make run-seq

# Parallel version (4 processors)
make run

# Compare both
make compare
```

### Full Benchmark (Cluster)

**Using SLURM:**
```bash
# Submit the benchmark job (1-64 processors)
sbatch benchmark_cluster.sh

# Check job status
squeue -u $USER

# View output
cat results/benchmark_*.out
```

**Using Make (if MPI is available locally):**
```bash
make benchmark
```

**Manual execution:**
```bash
# Sequential
./quicksort_seq

# Parallel with N processors
mpiexec -np 4 ./hyperquicksort
mpiexec -np 8 ./hyperquicksort
mpiexec -np 16 ./hyperquicksort
```

## Output

### Console Output
- Top 20 sorted players
- Timing information (distribution, sort, total)

### Files Generated
- `results/benchmark.csv` - Timing data for all runs
- `results/sorted_players_seq.csv` - Sequential sort results
- `results/sorted_players_p{N}.csv` - Parallel sort results for N processors

## Generating Graphs

After running benchmarks, generate performance graphs:

```bash
make graphs
# or
python3 generate_graphs.py
```

This creates:
- `results/performance_graphs.png` - 4-panel analysis (sort time, speedup, efficiency, total time)
- `results/performance_table.png` - Summary table of all metrics
- `results/time_breakdown.png` - Bar chart showing sort vs communication time

## Requirements

- C++17 compatible compiler
- MPI library (OpenMPI, MPICH, etc.)
- Python 3 + matplotlib + pandas (for graphs)
- For cluster: SLURM scheduler (or modify script for your scheduler)

## Installing Python Dependencies

```bash
pip install matplotlib pandas numpy
```

## Performance Metrics

The benchmark measures:
- **Distribution Time**: Time to scatter data across processors
- **Sort Time**: Actual sorting time (parallel quicksort)
- **Total Time**: Complete execution including I/O

Metrics calculated:
- **Speedup**: T₁ / Tₚ (sequential time / parallel time)
- **Efficiency**: (Speedup / p) × 100%

## Expected Results

With ~50,000 chess players:
- Sequential: ~50-100ms
- 2 processors: ~30-60ms (1.5-2x speedup)
- 4 processors: ~20-40ms (2.5-4x speedup)
- 8+ processors: Communication overhead becomes significant

Note: Speedup depends on cluster interconnect and data size.
