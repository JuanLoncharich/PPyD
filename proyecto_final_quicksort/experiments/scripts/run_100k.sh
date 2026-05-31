#!/bin/bash
# run_100k.sh - Run experiments for 100k size
# Execute this script ON the cluster (mulatona)

cd "$(dirname "$0")"
./run_experiments_cluster.sh 100k
