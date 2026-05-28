#!/bin/bash
# run_experiments_cluster.sh - Run all experiments directly on CCAD cluster
# Execute this script ON the cluster (mulatona)

set -e

EXP_DIR="$HOME/hyperquicksort"
SIZES=(100000 250000 750000 2000000 5000000)
SIZE_NAMES=("100k" "250k" "750k" "2M" "5M")
PROCS=(2 4 8 16 32)
RUNS=(1 2 3)

echo "=== QuickSort Performance Experiments ==="
echo "Running on cluster: $(hostname)"
echo "Sizes: ${SIZES[*]}"
echo "Processes: ${PROCS[*]}"
echo "Runs per configuration: ${#RUNS[@]}"
echo ""

# Create results directory
mkdir -p $EXP_DIR/experiments/results

# Function to create and submit sequential job
run_seq() {
    local size=$1
    local size_name=$2
    local run=$3

    cat > $EXP_DIR/experiments/slurm/tmp_seq.slurm << EOF
#!/bin/bash
#SBATCH --job-name=seq_${size_name}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=$EXP_DIR/experiments/results/seq_${size_name}_run${run}.out
#SBATCH --error=$EXP_DIR/experiments/results/seq_${size_name}_run${run}.err

. /etc/profile
cd $EXP_DIR
echo "Sequential Quicksort --generate $size players (run $run)"
./quicksort_seq --generate $size
EOF

    cd $EXP_DIR
    job_id=$(sbatch experiments/slurm/tmp_seq.slurm | grep -o '[0-9]*')
    echo "$job_id"
}

# Function to create and submit parallel job
run_par() {
    local size=$1
    local size_name=$2
    local procs=$3
    local run=$4

    cat > $EXP_DIR/experiments/slurm/tmp_par.slurm << EOF
#!/bin/bash
#SBATCH --job-name=par_${size_name}_p${procs}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=$procs
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=$EXP_DIR/experiments/results/par_${size_name}_p${procs}_run${run}.out
#SBATCH --error=$EXP_DIR/experiments/results/par_${size_name}_p${procs}_run${run}.err

. /etc/profile
cd $EXP_DIR/parallel
echo "Hyperquicksort --generate $size players with $procs processes (run $run)"
mpirun --oversubscribe -np $procs --bind-to none --map-by ppr:1:core ./hyperquicksort --generate $size
EOF

    cd $EXP_DIR
    job_id=$(sbatch experiments/slurm/tmp_par.slurm | grep -o '[0-9]*')
    echo "$job_id"
}

# Submit all jobs
JOB_IDS=()

echo "=== Submitting Sequential Jobs ==="
for i in "${!SIZES[@]}"; do
    SIZE=${SIZES[$i]}
    SIZE_NAME=${SIZE_NAMES[$i]}

    for run in "${RUNS[@]}"; do
        echo -n "  Sequential ${SIZE_NAME} (run $run): job "
        job_id=$(run_seq $SIZE $SIZE_NAME $run)
        echo "$job_id"
        JOB_IDS+=($job_id)
        sleep 0.5
    done
done

echo ""
echo "=== Submitting Parallel Jobs ==="
for i in "${!SIZES[@]}"; do
    SIZE=${SIZES[$i]}
    SIZE_NAME=${SIZE_NAMES[$i]}

    for procs in "${PROCS[@]}"; do
        for run in "${RUNS[@]}"; do
            echo -n "  Parallel ${SIZE_NAME} p${procs} (run $run): job "
            job_id=$(run_par $SIZE $SIZE_NAME $procs $run)
            echo "$job_id"
            JOB_IDS+=($job_id)
            sleep 0.5
        done
    done
done

echo ""
echo "=== Submitted ${#JOB_IDS[@]} jobs ==="
echo "Monitor with: squeue -u \$USER"
echo ""
echo "After all jobs complete, run:"
echo "  python3 $EXP_DIR/experiments/scripts/collect_results.py"
echo "  python3 $EXP_DIR/experiments/scripts/plot_results.py"
