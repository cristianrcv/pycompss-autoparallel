#!/bin/bash
#
#SBATCH --job-name=COMPSs-gemm-seq
#SBATCH --exclusive
#SBATCH -t00:30:00
#SBATCH --workdir=/home/bsc19/bsc19533/autoparallel/gemm_seq/results/mn/
#SBATCH -o compss-%J.out
#SBATCH -e compss-%J.err
#SBATCH -N1
#SBATCH -n1

echo "STARTING JOB"

SRC_DIR=$(pwd)/../../sequential/

MSIZES=(8 16 32 64 128 256 1024 2048 4096)
for i in "${!MSIZES[@]}"; do
  msize=${MSIZES[$i]}

  echo "- LAUNCHING EXECUTION WITH MSIZE=$msize"
  python -O "${SRC_DIR}"/gemm.py "$msize"
done

echo "ENDING JOB"

