#!/bin/bash
# run_750k.sh - Run experiments for 750k size
# Execute this script ON the cluster (mulatona)

cd "$(dirname "$0")"
./run_experiments_cluster.sh 750k
