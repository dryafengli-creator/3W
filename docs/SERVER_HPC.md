# 3W — 算力阵地：深圳高性能计算公共平台 (SYSU HPC)

> **创建**: 2026-06-25 · **状态**: ✅ 已接入（SSH 免密）
> **定位**: 本地 = 指挥中心（代码/git/设计/轻量仿真）；**本 HPC = 算力阵地**（大数据下载 + 重计算 + GPU）。
> **真实性原则 (P1)**: 本文所有规格均来自 2026-06-25 ssh 实测。

---

## 1. 接入方式

| 项 | 值 |
|---|---|
| SSH 别名 | `ssh sysu-hpc`（已配 `~/.ssh/config`，免密） |
| 登录 IP / 端口 | 172.25.20.103 : 22（**校园私网**，需校园网/VPN 内才可达） |
| 用户 | `fsby1lyf` |
| 认证 | 公钥 `id_ed25519`（已装入服务器 `~/.ssh/authorized_keys`） |
| Web 平台 | http://172.25.20.103:8081/login/ （账号同上） |
| 登录节点 | `manage2`（64 核 / 124 GB） |

⚠️ **安全**: 初始密码 `dah^%$21GB` 已在聊天明文出现 → **建议尽快在 Web 平台改密码**。免密登录已配好，日常不再需要密码。

---

## 2. 硬件 / 调度（Slurm）

Rocky Linux 8.6 · 调度器 **Slurm**（`sbatch`/`squeue`/`sinfo`）。
⚠️ **重计算必须经 `sbatch`/`salloc` 提交作业，不要在登录节点跑。** 账户有 **1000 元机时奖励**，需省用（CPU 分区便宜，GPU 贵）。

| 分区 | 节点 | 每节点核 | GPU | 用途 |
|---|---|---|---|---|
| `x86_64_2cpu`（默认） | 52 | 64 | — | **κ Phase 1 主力（线性代数，便宜）** |
| `x86_64_4cpu` | 10 | 96 | — | 大内存 CPU 作业 |
| `x86_64_8cpu` | 2 | 192 | — | 超大 CPU 作业 |
| `x86_64_gpu800` | 5 | 64 | A800×4（≈A100 80G） | 后期 reTissue / 训练 |
| `x86_64_gpu6000` | 2 | 32 | A6000×2 | 中等 GPU |

账户 `account1` · QOS `normal`。

---

## 3. 存储

| 路径 | 文件系统 | 容量 | 用途 |
|---|---|---|---|
| `/share/home/fsby1lyf` | Lustre `/share` | 5.3 P（19% 用） | home；3W 数据与环境放这里 |

计划项目根：`/share/home/fsby1lyf/3W/`（数据 `data/`、环境 `envs/`、结果 `results/`）。

---

## 4. 外网 / 软件

- **登录节点可直连外网**（实测 2026-06-25）：anaconda 200 / github 200 / pypi 200 ✅；cellxgene 裸 bucket 403（正常，具体数据集 URL + census API 可用）。无 proxy env。
  → **"服务器拉公共数据"策略成立**（CellxGene census / HCA / 公共空转）。
- **无预装 anaconda/cuda 模块**（`module avail` 仅基础）→ 需自行在 home 装 **miniconda** + 建 3W 环境（numpy/scipy/scanpy/anndata 等）。

---

## 5. 常用命令

```bash
ssh sysu-hpc                              # 免密登录
sinfo -o '%P %a %l %D %c %G'              # 看分区/GPU
squeue -u fsby1lyf                        # 看自己的作业
sbatch job.sh                             # 提交作业
salloc -p x86_64_2cpu -c 8 --time=2:00:00 # 申请交互式 CPU 资源
```

---

## 6. 待办（部署 3W）

- [ ] Web 平台改初始密码
- [ ] 装 miniconda 到 `/share/home/fsby1lyf/miniconda3`
- [ ] 建 conda 环境 `3w`（python + numpy/scipy/scikit-learn/scanpy/anndata）
- [ ] 建项目根 `/share/home/fsby1lyf/3W/` 并同步 `threew/` 代码
- [ ] 写 Slurm 作业模板（CPU 版，用于 κ 真数据实验）
- [ ] Phase 1 数据：从 CellxGene 拉 ≥3 个组织
