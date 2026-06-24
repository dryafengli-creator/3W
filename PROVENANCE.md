# 3W — 继承与边界说明 (PROVENANCE)

> **创建**: 2026-06-25
> **用途**: 明确 3W 从 paper3 (CRM-VC / CKM) **继承了什么、刻意不继承什么**，避免历史包袱与上下文污染。
> **真实性原则 (P1)**: 凡未在 3W 内重新验证的，一律视为"待验证"，不得直接当 3W 结论引用。

---

## 1. 继承（迁入 3W）

| 资产 | 来源 (paper3) | 在 3W 的位置 | 性质 |
|---|---|---|---|
| 愿景 / 思维实录 | `audit/3W_VISION_AND_DIALOGUE_2026-06-23.md` | `docs/3W_VISION.md` | 概念骨架 |
| κ 技术设计 | `audit/METHOD_DESIGN_kappa_conservation_2026-06-23.md` | `docs/METHOD_DESIGN_kappa.md` | 数学/零模型/conjecture |
| κ 仿真代码 | `99_scripts/M_method_conservation/sim_kappa_calibration.py` | `threew/conservation/sim_kappa_calibration.py` | 已跑通（线性高斯） |

**只继承"方法资产"（代码 + 设计 + 思路），不继承数据与基础设施。**

---

## 2. 刻意不继承（留在 paper3，3W 不依赖）

| 不继承项 | 原因 |
|---|---|
| CKM 8 器官 atlas h5ad（4.11M cells） | 有 HVG 并集**零填充**硬伤；3W 主张"全基因交集重建共享空间"，借搬家甩掉此包袱。仅作 Phase 1 **可选额外测试床**，引用不依赖。 |
| CRM-FM（XOT/HXOA/DCL 基础模型） | 串烧、且 ARI 0.477 < scVI 0.532；非 3W 创新点。其 M4 塌缩仅作为 3W 引言的**循环验证负结果动机**。 |
| 服务器 `/data/CRMVC/`（36.134.185.142） | 算力阵地将迁至**新服务器**（待接入）。旧数据归档策略待定。 |
| paper3 的 MASTER_PLAN / handoff / audit 体系 | 属 CRM-VC 历史；3W 用全新文档体系。 |

---

## 3. 数据策略：干净启动

- 3W 数据**按需从公共库重新拉取**（CellxGene census / HCA / 公共空转），在**服务器**完成。
- 共享基因空间用**测到基因的交集 / 全基因**，**不复用** CKM 的 4000-HVG 并集。
- `data/` 本地仅放小样本 / 元数据；大数据在服务器。

---

## 4. 唯一可引用的既有结果

截至 2026-06-25，3W 名下**唯一**可引用的实证结果是：
- κ 在**线性高斯仿真**上的校准/恢复/抗混杂三论断（FDR 0.021/0.083/0.188；U 捕获 0.864 vs 组成 0.006；朴素法假阳 0.599）。

其余（真实数据有效性、可识别性定理、环境轴、reTissue）**均待 3W 内验证**。
