#!/bin/bash
#SBATCH --job-name=par_${SIZE_NAME}_p${PROCS}
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=${PROCS}
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=${EXP_DIR}/results/par_${SIZE_NAME}_p${PROCS}_${RUN}.out
#SBATCH --error=${EXP_DIR}/results/par_${SIZE_NAME}_p${PROCS}_${RUN}.err

. /etc/profile
cd ${EXP_DIR}/parallel
echo "Hyperquicksort --generate ${SIZE} players with ${PROCS} processes"
mpirun --oversubscribe -np ${PROCS} --bind-to none --map-by ppr:1:core ./hyperquicksort --generate ${SIZE}
