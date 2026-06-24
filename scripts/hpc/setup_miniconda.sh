#!/usr/bin/env bash
# 3W — SYSU HPC environment bootstrap (follows platform manual 2025_v2 §Conda)
# Run on LOGIN NODE only (lightweight). Do NOT run heavy compute here.
set -euo pipefail

CONDA_ROOT="${HOME}/software/miniconda3"
ENV_NAME="3w"
PROJECT_ROOT="${HOME}/3W"

echo "=== [1/6] create directories ==="
mkdir -p "${HOME}/software" "${PROJECT_ROOT}"/{data,results,scripts,logs}

if [[ -x "${CONDA_ROOT}/bin/conda" ]]; then
  echo "miniconda already at ${CONDA_ROOT}; skip install"
else
  echo "=== [2/6] download + install miniconda -> ${CONDA_ROOT} ==="
  cd "${HOME}/software"
  if [[ ! -f Miniconda3-latest-Linux-x86_64.sh ]]; then
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  fi
  # target dir must NOT exist before -b install (manual)
  rm -rf "${CONDA_ROOT}"
  bash Miniconda3-latest-Linux-x86_64.sh -b -p "${CONDA_ROOT}"
  rm -f Miniconda3-latest-Linux-x86_64.sh
fi

echo "=== [3/6] wire ~/.bashrc (PATH + conda init) ==="
grep -q 'software/miniconda3/bin' ~/.bashrc || \
  echo 'export PATH="${HOME}/software/miniconda3/bin:$PATH"' >> ~/.bashrc
"${CONDA_ROOT}/bin/conda" init bash >/dev/null 2>&1 || true

# shellcheck disable=SC1091
source "${CONDA_ROOT}/etc/profile.d/conda.sh"

echo "=== [4/6] create conda env: ${ENV_NAME} (python 3.11) ==="
if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "env ${ENV_NAME} exists; skip create"
else
  conda create -n "${ENV_NAME}" python=3.11 -y
fi

conda activate "${ENV_NAME}"

echo "=== [5/6] install Phase-1 packages (kappa + scRNA I/O) ==="
# numpy/scipy/sklearn: kappa engine; scanpy/anndata: real data Phase 1
conda install -y -c conda-forge numpy scipy scikit-learn pandas h5py
pip install -q scanpy anndata

echo "=== [6/6] smoke test ==="
python - <<'PY'
import numpy, scipy, sklearn, pandas, h5py, scanpy, anndata
print("OK packages:", numpy.__version__, scipy.__version__, sklearn.__version__, scanpy.__version__)
PY

echo ""
echo "DONE. Next:"
echo "  source ~/.bashrc && conda activate ${ENV_NAME}"
echo "  project root: ${PROJECT_ROOT}"
echo "  submit jobs via: sbatch ${PROJECT_ROOT}/scripts/hpc/run_kappa_cpu.slurm"
