#!/bin/bash
#SBATCH --job-name=seq_sort
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=short
#SBATCH --time=00:05:00
#SBATCH --output=seq_%j.out

. /etc/profile
cd ~/hyperquicksort
echo 'Sequential Quicksort --generate 10000 players'
./quicksort_seq --generate 10000
