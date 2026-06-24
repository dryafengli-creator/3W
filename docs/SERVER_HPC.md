# 3W — 算力阵地：深圳高性能计算公共平台 (SYSU HPC)

> **创建**: 2026-06-25 · **状态**: ✅ 已接入 + **环境已配置** + Slurm 试跑通过
> **手册**: `高性能计算公共平台（深圳校区）用户使用手册2025_v2.pdf`
> **定位**: 本地 = 指挥中心（代码/git/设计）；**本 HPC = 算力阵地**（数据下载 + `sbatch` 重计算）。
> **真实性原则 (P1)**: 本文所有状态均来自 ssh 实测。

---

## 1. 接入方式

| 项 | 值 |
|---|---|
| SSH 别名 | `ssh sysu-hpc`（`~/.ssh/config`，免密） |
| 登录 IP / 端口 | 172.25.20.103 : 22（**校园私网**，需校园网/VPN） |
| 用户 | `fsby1lyf` |
| Web 平台 | http://172.25.20.103:8081/login/ （数据上传/下载、私有计费中心） |
| 登录节点 | `manage2`（**禁止跑重计算**） |
| 项目代码 | `~/3W`（`git clone https://github.com/dryafengli-creator/3W.git`） |

⚠️ **请尽快在 Web 平台修改初始密码**（聊天中曾明文出现）。日常用 SSH 免密即可。

---

## 2. 硬件 / Slurm（手册 §作业管理）

Rocky Linux 8.6 · **Slurm** · 5056 CPU 核 · 24 GPU · 6 PB 存储 · 200 Gb IB。

| 分区 | GPU | 用途 |
|---|---|---|
| `x86_64_2cpu`（**默认**） | — | **κ Phase 1 主力（便宜）** |
| `x86_64_4cpu` / `x86_64_8cpu` | — | 大内存 CPU |
| `x86_64_gpu800` | A800×4 | 后期 reTissue / 训练（`--gres=gpu:A800:N`） |
| `x86_64_gpu6000` | A6000×2 | 中等 GPU |

**规范（手册 §不规范操作）**：
- ⛔ **管理节点禁止高 CPU/高 IO 任务**（我们在登录节点跑仿真曾触发 OpenBLAS OOM）
- ✅ **所有重计算必须 `sbatch` 提交**
- ⛔ 谨慎使用 `--exclusive`（占满整节点，费机时）
- GPU 分区不要跑纯 CPU 任务

账户 `account1` · QOS `normal` · **新开 1000 元机时奖励** · 管理费 30 元/月 · 免费存储 5 TB。

---

## 3. 环境与目录（手册 §Conda，已配置 ✅）

按手册安装在 **个人目录**，不污染 base：

| 路径 | 内容 |
|---|---|
| `~/software/miniconda3` | Miniconda（手册推荐 `${HOME}/software/miniconda3`） |
| conda env **`3w`** | Python 3.11 + numpy/scipy/sklearn/pandas/h5py/scanpy/anndata |
| `~/3W/` | 项目根（git 仓库） |
| `~/3W/data/` | 数据（gitignore，服务器拉取） |
| `~/3W/results/` | 结果 audit |

**激活环境**：
```bash
source ~/.bashrc
conda activate 3w
```

**一键重装**（登录节点，轻量）：
```bash
bash ~/3W/scripts/hpc/setup_miniconda.sh
```

---

## 4. 作业提交（已试跑 ✅）

```bash
cd ~/3W
git pull
sbatch scripts/hpc/run_kappa_cpu.slurm
squeue -u fsby1lyf
sacct -j <JOBID> --format=JobID,State,ExitCode,Elapsed -n
```

**试跑记录（2026-06-25）**：
- Job `859653` · 分区 `x86_64_2cpu` · **COMPLETED** · 12s
- κ 仿真三论断与本地一致（FDR 0.021/0.083/0.188；U 捕获 0.864）

日志：`~/3W/<JOBID>.out` / `~/3W/<JOBID>.err`

---

## 5. 外网 / 数据

登录节点可直连：anaconda ✅ · github ✅ · pypi ✅ → CellxGene 公共数据可在服务器拉取。

大文件也可用 Web 平台「数据管理」上传/下载。

---

## 6. 常用命令

```bash
ssh sysu-hpc
sinfo -o '%P %a %l %D %c %G'
squeue -u fsby1lyf
scancel <JOBID>
conda env list
```

---

## 7. 待办

- [x] SSH 免密接入
- [x] Miniconda + env `3w`
- [x] 项目 `~/3W` git 同步
- [x] Slurm CPU 模板试跑
- [ ] Web 平台改密码
- [ ] Phase 1：CellxGene 拉 ≥3 组织 → κ 真数据阳性对照

---

## 8. 论文致谢（手册要求）

> 本研究工作得到中山大学高性能计算公共平台（深圳校区）支持。
> Supported by High-performance Computing Public Platform (Shenzhen Campus) of Sun Yat-sen University.
