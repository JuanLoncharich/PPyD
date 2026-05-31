#!/bin/bash
# run_2M.sh - Run experiments for 2M size
# Execute this script ON the cluster (mulatona)

cd "$(dirname "$0")"
./run_experiments_cluster.sh 2M
