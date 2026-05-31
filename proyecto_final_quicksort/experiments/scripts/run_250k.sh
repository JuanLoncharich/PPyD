#!/bin/bash
# run_250k.sh - Run experiments for 250k size
# Execute this script ON the cluster (mulatona)

cd "$(dirname "$0")"
./run_experiments_cluster.sh 250k
