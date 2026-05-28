#!/bin/bash
#SBATCH --job-name=hyperqs
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --partition=short
#SBATCH --time=00:05:00
#SBATCH --output=hyper_%j.out

. /etc/profile
cd ~/hyperquicksort
srun ./hyperquicksort
