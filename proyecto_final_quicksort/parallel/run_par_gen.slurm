#!/bin/bash
#SBATCH --job-name=par_sort
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --partition=short
#SBATCH --time=00:05:00
#SBATCH --output=par_%j.out

. /etc/profile
cd ~/hyperquicksort
echo 'Hyperquicksort --generate 100000 players'
srun ./hyperquicksort --generate 100000
