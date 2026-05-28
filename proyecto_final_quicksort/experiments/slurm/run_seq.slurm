#!/bin/bash
#SBATCH --job-name=seq_${SIZE_NAME}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=${EXP_DIR}/results/seq_${SIZE_NAME}_${RUN}.out
#SBATCH --error=${EXP_DIR}/results/seq_${SIZE_NAME}_${RUN}.err

. /etc/profile
cd ${EXP_DIR}/..
echo "Sequential Quicksort --generate ${SIZE} players"
./quicksort_seq --generate ${SIZE}
