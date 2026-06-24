#!/bin/bash
#SBATCH -J 3w-kappa
#SBATCH -p x86_64_2cpu
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -c 1
#SBATCH --time=02:00:00
#SBATCH -o %j.out
#SBATCH -e %j.err

# 3W Phase-1 CPU job template (kappa / conservation analysis)
# Manual: heavy compute MUST go through sbatch, not login node.

set -euo pipefail
source ~/.bashrc
conda activate 3w

PROJECT_ROOT="${HOME}/3W"
cd "${PROJECT_ROOT}"

echo "=== job start $(date -Is) ==="
echo "host=$(hostname) partition=${SLURM_JOB_PARTITION} cpus=${SLURM_CPUS_ON_NODE}"
python -V
python -m threew.conservation.sim_kappa_calibration

echo "=== job end $(date -Is) ==="
