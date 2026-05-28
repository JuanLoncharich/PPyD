#!/bin/bash
# run_experiments.sh - Run all performance experiments on CCAD cluster
# This script submits SLURM jobs for all configurations

set -e

# Experiment configurations
SIZES=(100000 1000000 2500000)
SIZE_NAMES=("100k" "1M" "2.5M")
PROCS=(1 2 4 8 16 32)
RUNS=(1 2 3)

EXP_DIR="$HOME/hyperquicksort"

echo "=== QuickSort Performance Experiments ==="
echo "Sizes: ${SIZES[*]}"
echo "Processes: ${PROCS[*]}"
echo "Runs per configuration: ${#RUNS[@]}"
echo ""

# Create results directory
ssh mulatona.ccad.unc.edu.ar "mkdir -p $EXP_DIR/experiments/results"

# Function to submit sequential job
submit_seq() {
    local size=$1
    local size_name=$2
    local run=$3

    cat > /tmp/run_seq.slurm << EOF
#!/bin/bash
#SBATCH --job-name=seq_${size_name}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=$EXP_DIR/experiments/results/seq_${size_name}_run${run}.out

. /etc/profile
cd $EXP_DIR
echo "Sequential Quicksort --generate $size players (run $run)"
./quicksort_seq --generate $size
EOF

    scp -q /tmp/run_seq.slurm mulatona.ccad.unc.edu.ar:$EXP_DIR/experiments/slurm/
    ssh mulatona.ccad.unc.edu.ar "cd $EXP_DIR && sbatch experiments/slurm/run_seq.slurm" | grep -o '[0-9]*'
}

# Function to submit parallel job
submit_par() {
    local size=$1
    local size_name=$2
    local procs=$3
    local run=$4

    cat > /tmp/run_par.slurm << EOF
#!/bin/bash
#SBATCH --job-name=par_${size_name}_p${procs}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=$procs
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=$EXP_DIR/experiments/results/par_${size_name}_p${procs}_run${run}.out

. /etc/profile
cd $EXP_DIR/parallel
echo "Hyperquicksort --generate $size players with $procs processes (run $run)"
mpirun --oversubscribe -np $procs --bind-to none --map-by ppr:1:core ./hyperquicksort --generate $size
EOF

    scp -q /tmp/run_par.slurm mulatona.ccad.unc.edu.ar:$EXP_DIR/experiments/slurm/
    ssh mulatona.ccad.unc.edu.ar "cd $EXP_DIR && sbatch experiments/slurm/run_par.slurm" | grep -o '[0-9]*'
}

# Submit all jobs
JOB_IDS=()

echo "=== Submitting Sequential Jobs ==="
for i in "${!SIZES[@]}"; do
    SIZE=${SIZES[$i]}
    SIZE_NAME=${SIZE_NAMES[$i]}

    for run in "${RUNS[@]}"; do
        echo -n "  Sequential ${SIZE_NAME} (run $run): job "
        job_id=$(submit_seq $SIZE $SIZE_NAME $run)
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
            job_id=$(submit_par $SIZE $SIZE_NAME $procs $run)
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
echo "After all jobs complete, run collect_results.py to parse the outputs"
