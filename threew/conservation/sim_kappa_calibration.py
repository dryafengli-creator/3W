"""
First falsification experiment for the kappa (Conserved Co-Regulation) method.
==============================================================================
Pure-numpy simulation (no scanpy/torch needed). Tests the THREE core claims of
the method design (audit/METHOD_DESIGN_kappa_conservation_2026-06-23.md):

  (1) CALIBRATION  : under a composition-preserving null with NO shared program,
                     kappa-based testing controls false positives at the nominal
                     FDR (no integration, no cross-domain cell correspondence).
  (2) RECOVERY     : with planted shared programs + a cell-composition confound,
                     the top-kappa significant directions align with the TRUE
                     shared subspace and NOT with the composition subspace.
  (3) CONFOUND FIX : a NAIVE baseline (per-domain PCA loading correlation, no
                     residualization) is fooled by composition -> calls it
                     "conserved" (false positive). Our residualization removes it.

This script DOES NOT fabricate results. Run it and paste the printed metrics
into the design doc's validation section.

Run:
  python sim_kappa_calibration.py
  (numpy only; ~seconds)
"""
from __future__ import annotations

import numpy as np


# ----------------------------------------------------------------------------- #
# Simulation
# ----------------------------------------------------------------------------- #
def simulate_domains(
    D=6, G=300, Nd=2000, T=4, K_shared=3, K_priv=2,
    shared_presence=0.85, comp_strength=2.0, noise=0.5, seed=0,
):
    """Each domain = shared programs (subset present) + private programs
    + cell-type mean structure (the composition confound) + noise.
    Returns ground-truth shared loadings U and composition templates."""
    rng = np.random.default_rng(seed)

    U = rng.normal(size=(G, K_shared)) if K_shared > 0 else np.zeros((G, 0))
    if K_shared > 0:
        U /= np.linalg.norm(U, axis=0, keepdims=True)

    # cell-type mean templates: SHARED across domains -> drives spurious
    # cross-domain co-expression (the Simpson / composition confound).
    celltype_means = rng.normal(scale=comp_strength, size=(G, T))

    domains = []
    for d in range(D):
        comp = rng.dirichlet(alpha=np.ones(T) * 0.5)          # composition varies
        labels = rng.choice(T, size=Nd, p=comp)

        Wd = rng.normal(size=(G, K_priv))                     # private programs
        Wd /= np.linalg.norm(Wd, axis=0, keepdims=True)

        present = (rng.random(K_shared) < shared_presence) if K_shared > 0 else np.zeros(0, bool)

        X = celltype_means[:, labels].T.copy()                # composition structure
        if K_shared > 0:
            a_shared = rng.normal(size=(Nd, K_shared)) * present[None, :]
            X += a_shared @ U.T
        a_priv = rng.normal(size=(Nd, K_priv))
        X += a_priv @ Wd.T
        X += rng.normal(scale=noise, size=(Nd, G))

        domains.append({"X": X, "labels": labels})

    return {"U": U, "celltype_means": celltype_means, "domains": domains,
            "G": G, "T": T, "K_shared": K_shared}


# ----------------------------------------------------------------------------- #
# Method primitives
# ----------------------------------------------------------------------------- #
def residualize(X, labels, T):
    """Domain-private nuisance removal: subtract per-cell-type mean (kills
    composition-driven gene-gene correlation), then center genes."""
    R = X.copy()
    for t in range(T):
        m = labels == t
        if m.sum() > 1:
            R[m] -= X[m].mean(0, keepdims=True)
    R -= R.mean(0, keepdims=True)
    return R


def candidate_dirs(residuals, n_per_domain=8):
    """Candidate program basis from the UNION of per-domain residual PCA dirs.
    Crucially uses NO cross-domain information (no circularity)."""
    cands = []
    for R in residuals:
        _, _, Vt = np.linalg.svd(R, full_matrices=False)
        cands.append(Vt[:n_per_domain])
    return np.vstack(cands)  # (D*n_per_domain, G), unit rows


def rho_d(V, R):
    """Relative co-regulation strength of each direction (rows of V) in domain
    residual R. For a random unit direction this is ~1."""
    proj_var = np.var(R @ V.T, axis=0)                # (k,)
    mean_eig = np.var(R, axis=0).sum() / R.shape[1]   # mean per-gene residual var
    return proj_var / (mean_eig + 1e-12)


def kappa_breadth(V, residuals, trim_top=1):
    """Breadth across domains via a TRIMMED geometric mean of per-domain rho:
    drop the `trim_top` largest rho per candidate, then geomean the rest. This
    requires a program to be strong in >= 2 domains (a single strong "home"
    domain cannot inflate the statistic) -> measures conservation, not privacy.
    Rows of V are candidate directions."""
    rhos = np.stack([rho_d(V, R) for R in residuals], axis=0)  # (D, k)
    rhos = np.clip(rhos, 1e-6, None)
    if trim_top > 0:
        rhos = np.sort(rhos, axis=0)[:-trim_top, :]            # drop largest trim_top
    return np.exp(np.mean(np.log(rhos), axis=0))               # (k,)


def null_scramble_alignment(R, rng):
    """Conservation null: independently permute GENES (columns) within the
    domain. Preserves the domain's full covariance spectrum (its private
    co-regulation magnitude) but destroys CROSS-domain gene correspondence.
    H0 = 'each domain has its own structure, but nothing is shared/aligned'."""
    return R[:, rng.permutation(R.shape[1])]


def kappa_test(residuals, V, n_perm=30, seed=1, trim_top=1):
    """Observed kappa per candidate + empirical p-values vs the
    alignment-scrambling null (preserves per-domain co-regulation) + BH-FDR."""
    rng = np.random.default_rng(seed)
    obs = kappa_breadth(V, residuals, trim_top=trim_top)
    null_pool = []
    for _ in range(n_perm):
        Rn = [null_scramble_alignment(R, rng) for R in residuals]
        null_pool.append(kappa_breadth(V, Rn, trim_top=trim_top))
    null_pool = np.concatenate(null_pool)                      # global null
    pvals = np.array([(np.sum(null_pool >= k) + 1) / (null_pool.size + 1) for k in obs])
    # BH-FDR
    order = np.argsort(pvals)
    m = len(pvals)
    qvals = np.empty(m)
    prev = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        i = m - rank
        q = pvals[idx] * m / (i + 1)
        prev = min(prev, q)
        qvals[idx] = prev
    return obs, pvals, qvals


# ----------------------------------------------------------------------------- #
# Evaluation helpers
# ----------------------------------------------------------------------------- #
def subspace_capture(V, B):
    """Mean fraction of each direction's norm that lies in span(B).
    V: (k, G) unit rows; B: (G, m). Returns scalar in [0, 1]."""
    if B.shape[1] == 0 or V.shape[0] == 0:
        return float("nan")
    Q, _ = np.linalg.qr(B)
    proj = V @ Q                       # (k, r)
    return float(np.mean(np.sum(proj ** 2, axis=1) / (np.sum(V ** 2, axis=1) + 1e-12)))


def naive_conserved_dirs(domains, n_top=5):
    """NAIVE baseline: per-domain PCA on RAW centered data (no residualization),
    pick directions whose loadings are most correlated across domains."""
    pcs = []
    for dom in domains:
        X = dom["X"] - dom["X"].mean(0, keepdims=True)
        _, _, Vt = np.linalg.svd(X, full_matrices=False)
        pcs.append(Vt[:n_top])
    ref = pcs[0]
    scored = []
    for v in ref:
        agree = np.mean([np.max(np.abs(pcs[d] @ v)) for d in range(1, len(pcs))])
        scored.append((agree, v))
    scored.sort(key=lambda s: -s[0])
    return np.array([v for _, v in scored[:n_top]])


# ----------------------------------------------------------------------------- #
# Experiments
# ----------------------------------------------------------------------------- #
def run():
    print("=" * 70)
    print("EXP A — CALIBRATION (no shared program; FDR should be controlled)")
    print("=" * 70)
    simA = simulate_domains(K_shared=0, seed=10)
    resA = [residualize(d["X"], d["labels"], simA["T"]) for d in simA["domains"]]
    VA = candidate_dirs(resA)
    _, _, qA = kappa_test(resA, VA, n_perm=30, seed=11)
    for alpha in (0.05, 0.10, 0.20):
        frac = float(np.mean(qA <= alpha))
        print(f"  FDR={alpha:.2f}: fraction of candidates called significant = {frac:.3f}  (target <= {alpha:.2f})")

    print()
    print("=" * 70)
    print("EXP B — RECOVERY + COMPOSITION ROBUSTNESS (3 shared programs)")
    print("=" * 70)
    simB = simulate_domains(K_shared=3, seed=20)
    U = simB["U"]
    comp = simB["celltype_means"]
    resB = [residualize(d["X"], d["labels"], simB["T"]) for d in simB["domains"]]
    VB = candidate_dirs(resB)
    obs, _, qB = kappa_test(resB, VB, n_perm=30, seed=21)
    sig = VB[qB <= 0.10]
    top = VB[np.argsort(-obs)[:5]]
    print(f"  # significant @FDR 0.10: {sig.shape[0]} / {VB.shape[0]}")
    print(f"  [OURS] top-kappa dirs  capture of TRUE shared U  : {subspace_capture(top, U):.3f}  (want HIGH)")
    print(f"  [OURS] top-kappa dirs  capture of COMPOSITION     : {subspace_capture(top, comp):.3f}  (want LOW)")

    naive = naive_conserved_dirs(simB["domains"])
    print(f"  [NAIVE] conserved dirs capture of COMPOSITION     : {subspace_capture(naive, comp):.3f}  (high => FALSE POSITIVE)")
    print(f"  [NAIVE] conserved dirs capture of TRUE shared U   : {subspace_capture(naive, U):.3f}")

    print()
    print("Interpretation guide (claims to verify):")
    print("  A: significant fraction ~<= nominal FDR  -> null is calibrated.")
    print("  B-OURS: high U-capture & low composition  -> recovers conserved, ignores confound.")
    print("  B-NAIVE: high composition-capture         -> integration-free naive is fooled (what we fix).")


if __name__ == "__main__":
    run()
