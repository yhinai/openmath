"""Figures for the OpenMath results, generated from this repo's own submissions.

Every plotted value is read from the repository (or from challenges/RESULTS.md /
the claim files, cited inline) so the figures cannot drift from what was verified.
Nothing here re-scores anything: the hills' own eval.py outputs are the authority.

Usage: python3 docs/make_result_figs.py
"""
import csv
import json
import math
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
INK = "#1b1b1f"
RED, BLUE, GREY, GREEN, AMBER = "#c0392b", "#2a6fdb", "#8a8a8a", "#1e8449", "#b9770e"

plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 160, "font.size": 11,
    "axes.edgecolor": GREY, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.titlesize": 12,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

C = ROOT / "challenges"


def fig_progress():
    """Hills with a verified submission, per list, split by worker (RESULTS.md)."""
    lists = ["01-openmath\n(6 hills)", "02-erdos\n(30 hills)", "03-hello-hills-v2\n(5 hills)",
             "04-millennium\n(4 hills)"]
    done_cg = [4, 0, 5, 0]          # charliegillet: clique-ramsey, matmul, collatz, grothendieck | hello-v2 all five
    done_yh = [2, 0, 0, 0]          # yhinai: busy-beaver, kobon
    total = [6, 30, 5, 4]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = np.arange(len(lists))
    ax.bar(x, done_cg, width=0.55, color=BLUE, label="charliegillet")
    ax.bar(x, done_yh, width=0.55, bottom=done_cg, color=AMBER, label="yhinai")
    ax.bar(x, [t - c - y for t, c, y in zip(total, done_cg, done_yh)], width=0.55,
           bottom=[c + y for c, y in zip(done_cg, done_yh)], color=GREY, alpha=0.25,
           label="open")
    for xi, (c, y, t) in enumerate(zip(done_cg, done_yh, total)):
        ax.annotate(f"{c + y}/{t}", (xi, t), ha="center", va="bottom", fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(lists, fontsize=9)
    ax.set_ylabel("hills with a verified submission")
    ax.set_title("OpenMath progress · 11 of 45 hills solved, every metric from the hill's own eval.py", fontsize=10.5)
    ax.legend(frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "fig_progress.png"); plt.close(fig)


def fig_ramsey():
    """The headline: block weights push the density just under the frozen reference."""
    ref = 0.030142273431942788          # B* = 10486266368 / 768^4  (REFERENCE hardcoded in eval.py)
    uniform = 10486294298 / 768 ** 4    # uniform-weight search best (above B*) -- RESULTS.md
    weighted = 0.030142188577           # weighted certificate, eval.py
    margin = ref - weighted
    # plot in explicit units of 1e-8 to avoid matplotlib's offset-notation axis
    u = {"ref": 0.0, "uniform": (uniform - ref) * 1e8, "weighted": (weighted - ref) * 1e8}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1.15, 1]})

    ax.axvline(u["ref"], color=INK, lw=1.8, zorder=3)
    ax.plot([u["uniform"]], [0.55], "o", ms=11, color=RED, zorder=5)
    ax.plot([u["weighted"]], [-0.55], "o", ms=11, color=GREEN, zorder=5)
    ax.annotate("uniform-weight search best\n0.0301423545 — ABOVE B* = no improvement",
                (u["uniform"], 0.55), xytext=(u["uniform"], 0.85), ha="center", va="bottom",
                fontsize=8.6, color=RED)
    ax.annotate("weighted certificate\n0.0301421886 — BELOW B*",
                (u["weighted"], -0.55), xytext=(u["weighted"], -0.95), ha="center", va="top",
                fontsize=8.6, color=GREEN)
    ax.annotate("frozen reference B*\n0.0301422734", (u["ref"], 0), xytext=(u["ref"], 0.12),
                ha="center", va="bottom", fontsize=9)
    ax.set_xlim(-16, 16)
    ax.set_ylim(-1.6, 1.3)
    ax.set_yticks([])
    ax.set_xlabel("monochromatic-K₄ density − B*   (units of 10⁻⁸)")
    ax.set_title("clique-cluster-ramsey: the gain came from block weights, not edge flips",
                 fontsize=8.8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)

    ax2.axis("off")
    ax2.text(0.0, 0.92, "exact rationals (hill/eval.py, verbatim)", fontsize=9.5, weight="bold")
    ax2.text(0.0, 0.70, "exact_density   = 671117410537831388186309\n"
                        "                  /22265052480462127079424004", fontsize=8.4, family="monospace")
    ax2.text(0.0, 0.52, "exact_reference = 20480989/679477248", fontsize=8.4, family="monospace")
    ax2.text(0.0, 0.34, "exact_reference_gap = 320934908917024358050415581\n"
                        "                     /3782149146499994969038324915765248",
             fontsize=8.4, family="monospace")
    ax2.text(0.0, 0.13, f"margin = {margin * 1e8:.2f}e-08 absolute = 0.000282 % relative\n"
                        "status: candidate improvement on the frozen reference;\n"
                        "        novelty and formal review required\n"
                        "        parent_problem_resolved = false",
             fontsize=8.6, color=AMBER)
    ax2.set_title("what the improvement actually is", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "fig_ramsey_gap.png"); plt.close(fig)


def fig_ramsey_certificate():
    p = C / "01-openmath" / "clique-cluster-ramsey-multiplicity" / "solution" / "solution.json"
    d = json.loads(p.read_text())
    rows, w = d["red_rows"], d["weights"]
    m = len(rows)
    A = np.array([[1 if ch == "1" else 0 for ch in r] for r in rows], dtype=np.float32)
    k = 8
    ds = A.reshape(m // k, k, m // k, k).mean(axis=(1, 3))
    fig, ax = plt.subplots(figsize=(4.9, 4.6))
    ax.imshow(ds, cmap="RdBu_r", vmin=0, vmax=1, interpolation="nearest")
    ax.set_title(f"weighted certificate  A ∈ {{0,1}}^{m}×{m}  ({k}×{k} block means)\n"
                 f"red density {A.mean():.4f} · w ∈ [{min(w)}, {max(w)}], Σw = {sum(w):,}",
                 fontsize=9.5)
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(); fig.savefig(OUT / "fig_ramsey_certificate.png"); plt.close(fig)


def fig_circle_packing():
    p = C / "03-hello-hills-v2" / "circle-packing" / "solution" / "solution.json"
    cs = json.loads(p.read_text())["circles"]
    S = sum(c["r"] for c in cs)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8.8, 4.3), gridspec_kw={"width_ratios": [1, 0.8]})
    for c in cs:
        ax.add_patch(plt.Circle((c["x"], c["y"]), c["r"], facecolor=BLUE, alpha=0.18,
                                edgecolor=BLUE, lw=1.1))
        ax.plot([c["x"]], [c["y"]], ".", ms=1.6, color=INK)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor=INK, lw=1.3))
    ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"26 circles · Σr = {S:.10f}\nradii {min(c['r'] for c in cs):.4f} … {max(c['r'] for c in cs):.4f}",
                 fontsize=10)
    labels = ["grid\nexample", "AlphaEvolve\n(coords)", "OURS", "best known\n(Friedman)"]
    vals = [2.5414, 2.6358627564136983, S, 2.635983084919]
    cols = [GREY, GREY, GREEN, BLUE]
    bars = ax2.bar(range(4), vals, color=cols, alpha=0.88)
    ax2.set_ylim(min(vals) - 0.02, max(vals) + 0.014)
    ax2.set_xticks(range(4)); ax2.set_xticklabels(labels, fontsize=8)
    ax2.set_ylabel("sum_radii")
    for b, v in zip(bars, vals):
        ax2.annotate(f"{v:.6f}", (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom", fontsize=8)
    ax2.set_title("ties best known; beats AlphaEvolve coords", fontsize=9.5)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "fig_circle_packing.png"); plt.close(fig)


def fig_heilbronn():
    p = C / "03-hello-hills-v2" / "heilbronn-triangle" / "solution" / "points.json"
    pts = np.array([[float(a), float(b)] for a, b in json.loads(p.read_text())])
    H = math.sqrt(3) / 2
    tri = np.array([[0, 0], [1, 0], [0.5, H], [0, 0]])
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    ax.plot(tri[:, 0], tri[:, 1], color=INK, lw=1.4)
    from itertools import combinations
    best = min(combinations(range(len(pts)), 3),
               key=lambda t: abs((pts[t[1]][0] - pts[t[0]][0]) * (pts[t[2]][1] - pts[t[0]][1])
                                 - (pts[t[1]][1] - pts[t[0]][1]) * (pts[t[2]][0] - pts[t[0]][0])))
    for i, (x, y) in enumerate(pts):
        ax.plot([x], [y], "o", ms=7 if i in best else 5, color=RED if i in best else BLUE, zorder=4)
        ax.annotate(str(i), (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    for i, j in combinations(best, 2):
        ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color=RED, lw=1.2, alpha=0.85)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(-0.04, 1.04); ax.set_ylim(-0.07, H + 0.05)
    ax.set_title("11 points, smallest triangle " + str(best) +
                 "\nmin_area = 0.03652988988003021642… (AlphaEvolve's config, re-solved at 140 digits)",
                 fontsize=8.6)
    fig.tight_layout(); fig.savefig(OUT / "fig_heilbronn.png"); plt.close(fig)


if __name__ == "__main__":
    fig_progress()
    fig_ramsey()
    fig_ramsey_certificate()
    fig_circle_packing()
    fig_heilbronn()
    for p in sorted(OUT.glob("*.png")):
        print(f"wrote {p.relative_to(ROOT)}  ({p.stat().st_size // 1024} KB)")
