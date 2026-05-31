#!/bin/bash
# run_5M.sh - Run experiments for 5M size
# Execute this script ON the cluster (mulatona)

cd "$(dirname "$0")"
./run_experiments_cluster.sh 5M
