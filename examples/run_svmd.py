"""
run_svmd.py — one-stop SVMD experiment runner (OOP package version).

Run from the repo root or from this directory:
  python examples/run_svmd.py                         # defaults: demo signal, stopc=4
  python examples/run_svmd.py --stopc 2               # stopc=2 (reconstruction-based)
  python examples/run_svmd.py --max-modes 8           # cap at 8 modes
  python examples/run_svmd.py --no-sgolay             # disable Savitzky-Golay
  python examples/run_svmd.py --compare-prototype     # verify new == svmd_prototype.py
  python examples/run_svmd.py --no-plot               # skip matplotlib

Custom signal:
  python examples/run_svmd.py --signal my.csv --params p.csv --no-ref
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup: add src/ so both `svmd` package and `svmd_prototype` are importable
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]   # For github/
_DEMO_DIR  = _REPO_ROOT / "third_party" / "svmd_original_demo"
sys.path.insert(0, str(_REPO_ROOT / "src"))

import numpy as np


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run SVMD (OOP package) and display validation results.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--signal",     type=Path, default=_DEMO_DIR / "signal.csv")
    p.add_argument("--params",     type=Path, default=_DEMO_DIR / "params.csv",
                   help="CSV with [fs, maxAlpha, stopc, tau, tol]")
    p.add_argument("--u-ref",      type=Path, default=_DEMO_DIR / "u.csv",
                   help="MATLAB reference modes (optional)")
    p.add_argument("--uhat-real",  type=Path, default=_DEMO_DIR / "uhat_real.csv")
    p.add_argument("--uhat-imag",  type=Path, default=_DEMO_DIR / "uhat_imag.csv")

    # Algorithm overrides
    p.add_argument("--stopc",      type=int,   default=None, choices=[1, 2, 3, 4],
                   help="Override stopc from params.csv  (1=noise 2=recon 3=BIC 4=polm)")
    p.add_argument("--max-alpha",  type=float, default=None)
    p.add_argument("--tau",        type=float, default=None)
    p.add_argument("--tol",        type=float, default=None)
    p.add_argument("--max-modes",  type=int,   default=0,
                   help="0 = unlimited")
    p.add_argument("--min-alpha",  type=float, default=10.0)
    p.add_argument("--tol-primal", type=float, default=1e-3)
    p.add_argument("--no-sgolay",  action="store_true")
    p.add_argument("--fixed-iter", action="store_true")
    p.add_argument("--save-prev",  action="store_true")
    p.add_argument("--no-sum-h",   action="store_true")

    # Output options
    p.add_argument("--no-plot",           action="store_true")
    p.add_argument("--compare-prototype", action="store_true",
                   help="Also run svmd_prototype.py and verify bit-for-bit parity")
    p.add_argument("--no-ref",            action="store_true",
                   help="Skip loading MATLAB reference files (faster)")
    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = build_parser().parse_args()

    # -- Load signal & params -----------------------------------------------
    print(f"Signal : {args.signal}")
    signal = np.loadtxt(args.signal, delimiter=",", dtype=np.float64)
    print(f"  shape={signal.shape}  range=[{signal.min():.4f}, {signal.max():.4f}]")

    params = np.loadtxt(args.params, delimiter=",", dtype=np.float64)
    _fs, max_alpha_p, stopc_p, tau_p, tol_p = params[:5]

    max_alpha = args.max_alpha if args.max_alpha is not None else float(max_alpha_p)
    tau       = args.tau       if args.tau       is not None else float(tau_p)
    tol       = args.tol       if args.tol       is not None else float(tol_p)
    stopc     = args.stopc     if args.stopc     is not None else int(stopc_p)
    max_modes = None if args.max_modes <= 0 else args.max_modes

    # -- Load MATLAB reference (optional) -----------------------------------
    u_ref = uhat_ref = None
    if not args.no_ref:
        if args.u_ref.exists():
            u_ref = np.loadtxt(args.u_ref, delimiter=",", dtype=np.float64)
        if args.uhat_real.exists() and args.uhat_imag.exists():
            uhat_ref = (np.loadtxt(args.uhat_real, delimiter=",", dtype=np.float64)
                      + 1j * np.loadtxt(args.uhat_imag, delimiter=",", dtype=np.float64))

    # -- Build config & run --------------------------------------------------
    from svmd import SVMDConfig, SVMDPipeline, SVMDValidator

    cfg = SVMDConfig(
        max_alpha        = max_alpha,
        tau              = tau,
        tol              = tol,
        stopc            = stopc,
        min_alpha        = args.min_alpha,
        max_modes        = max_modes,
        use_sgolay       = not args.no_sgolay,
        fixed_iterations = args.fixed_iter,
        save_prev_mode   = args.save_prev,
        use_sum_h        = not args.no_sum_h,
        tol_primal       = args.tol_primal,
        verbose          = True,
    )

    print(f"\nConfig: max_alpha={max_alpha}  tau={tau}  tol={tol}  stopc={stopc}")
    print(f"        sgolay={cfg.use_sgolay}  fixed_iter={cfg.fixed_iterations}  max_modes={max_modes}\n")

    t0 = time.perf_counter()
    u, u_hat, omega = SVMDPipeline(cfg).run(signal)
    elapsed = time.perf_counter() - t0

    print(f"\nExtracted {u.shape[0]} modes  ({elapsed:.2f}s)")
    print(f"Centre frequencies: {np.round(omega, 6)}")

    # -- Validation ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    report = SVMDValidator().validate(
        signal, u, omega,
        uhat_calc=u_hat,
        u_ref=u_ref,
        uhat_ref=uhat_ref,
    )
    SVMDValidator.print_report(report)

    # -- Parity check vs prototype (optional) --------------------------------
    if args.compare_prototype:
        print("\n" + "=" * 60)
        print("PROTOTYPE PARITY CHECK")
        print("=" * 60)
        try:
            from svmd_prototype import svmd as svmd_old
            u_old, _, om_old = svmd_old(
                signal, max_alpha, tau, tol, stopc,
                min_alpha        = cfg.min_alpha,
                max_modes        = max_modes,
                use_sgolay       = cfg.use_sgolay,
                fixed_iterations = cfg.fixed_iterations,
                save_prev_mode   = cfg.save_prev_mode,
                use_sum_h        = cfg.use_sum_h,
                tol_primal       = cfg.tol_primal,
                verbose          = False,
            )
            if u_old.shape[0] == u.shape[0]:
                du  = float(np.max(np.abs(u_old - u)))
                dom = float(np.max(np.abs(om_old - omega)))
                tag = "PASS" if du == 0 else "DIFF"
                print(f"  [{tag}] modes={u.shape[0]}  max|u_diff|={du:.2e}  max|omega_diff|={dom:.2e}")
            else:
                print(f"  [MISMATCH] prototype={u_old.shape[0]} modes, new={u.shape[0]} modes")
        except ImportError:
            print("  svmd_prototype.py not found in src/ — skipping")

    # -- Plot ----------------------------------------------------------------
    if not args.no_plot:
        _plot(signal, u, omega, report)


def _plot(signal, u, omega, report) -> None:
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not available — install it or use --no-plot)")
        return

    n_modes = u.shape[0]
    T = signal.shape[0]
    t = np.arange(T)
    freq_axis = np.fft.fftshift(np.fft.fftfreq(T))

    fig, axes = plt.subplots(
        n_modes + 1, 2,
        figsize=(14, max(3, 1.8 * (n_modes + 1))),
        gridspec_kw={"width_ratios": [3, 1]},
    )

    # Row 0: original signal
    axes[0, 0].plot(t, signal, "k", lw=0.8)
    axes[0, 0].set_title("Original signal", fontsize=9)
    axes[0, 1].plot(freq_axis, np.abs(np.fft.fftshift(np.fft.fft(signal))), "k", lw=0.8)
    axes[0, 1].set_title("Spectrum", fontsize=9)

    cmap = plt.cm.tab20
    for i in range(n_modes):
        color = cmap(i % 20)
        axes[i + 1, 0].plot(t, u[i], color=color, lw=0.8)
        axes[i + 1, 0].set_ylabel(f"M{i+1}", fontsize=7, rotation=0, labelpad=20)
        axes[i + 1, 0].tick_params(labelsize=6)
        axes[i + 1, 1].plot(freq_axis, np.abs(np.fft.fftshift(np.fft.fft(u[i]))), color=color, lw=0.8)
        axes[i + 1, 1].axvline(omega[i], color="red", lw=0.8, ls="--", alpha=0.7)
        axes[i + 1, 1].tick_params(labelsize=6)

    fig.suptitle(
        f"SVMD  {n_modes} modes  |  "
        f"recon_err={report.rel_recon_err:.3f}  corr={report.mean_abs_corr:.4f}",
        fontsize=10,
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
