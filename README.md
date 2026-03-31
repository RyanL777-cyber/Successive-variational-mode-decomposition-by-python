# SVMD Translation Audit

This folder is organized as a GitHub-ready package for an SVMD translation and validation project.

It contains three things in one place:

- my Python translation code
- the minimum original MATLAB reference files required for comparison
- the reference data used for parity checks

The point is not only to show a port of SVMD. The stronger engineering story is the audit process: tracing why a MATLAB-to-Python translation can look correct at the mode level while still disagree on some validation metrics, and narrowing that gap with controlled experiments instead of heuristic edits.

## What Is Included

This project has two layers that build on each other.

**Layer 1 — Translation audit** (`src/svmd_prototype.py`):
the original MATLAB-to-Python port with full validation metrics.
The engineering story here is the audit process itself: tracing why a translation
can look correct at the mode level while still disagreeing on some metrics,
and narrowing that gap with controlled experiments.

**Layer 2 — OOP refactor** (`src/svmd/`):
the prototype rewritten with Strategy Pattern + OOP to decouple math from control.
Every numerical operation lives in `NumpyBackend` and can be swapped for a C++ backend
without touching the loop logic or stopping criteria.
Verified bit-for-bit identical to the prototype across all stopc=1~4 combinations.

Other contents:
- `third_party/svmd_original_demo/` — bundled MATLAB reference code and validation assets
- `examples/` — runnable entry points (prototype validation + OOP runner)
- `results/` — saved outputs from the example runs
- `docs/ENGINEERING_CASE_STUDY.md` — writeup of the debugging process
- `docs/DEVELOPER.md` — which file to edit for each type of change (OOP package)

## Repo Layout

```text
.
|- README.md
|- requirements.txt
|- src/
|  |- svmd_prototype.py          # Layer 1: monolithic prototype
|  `- svmd/                      # Layer 2: OOP refactor
|     |- __init__.py
|     |- config.py               # SVMDConfig (all params)
|     |- interfaces.py           # Strategy ABCs
|     |- solver.py               # 3 nested loops (control only)
|     |- pipeline.py             # SVMDPipeline (top-level API)
|     |- validation.py           # SVMDValidator
|     |- backends/
|     |  |- numpy_backend.py     # all math lives here
|     |  `- cpp_backend.py       # C++ stub (future)
|     |- stopping/criteria.py    # stopc 1~4
|     `- schedule/alpha.py       # alpha growth schedule
|- examples/
|  |- README.md
|  |- run_validation.py          # prototype: parity check vs MATLAB
|  |- run_debug_trace.py         # prototype: short debug run
|  `- run_svmd.py                # OOP package runner
|- results/
|  |- validation_output.txt
|  `- debug_trace_output.txt
|- docs/
|  |- ENGINEERING_CASE_STUDY.md
|  |- DEVELOPER.md               # which file to edit for what
|  |- SVMD_translation_notes.md
|  `- THIRD_PARTY_NOTICE.md
`- third_party/
   `- svmd_original_demo/
      |- svmd.m  test_svmd.m  ECG.mat
      `- signal.csv  params.csv  u.csv  omega.csv  uhat_real.csv  uhat_imag.csv
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

**Layer 1 — run the prototype validation** (audit story):

```bash
python examples/run_validation.py      # parity check vs MATLAB, stopc=2
python examples/run_debug_trace.py     # short debug trace, first 5 modes
```

**Layer 2 — run the OOP package** (architecture story):

```bash
python examples/run_svmd.py                        # default: stopc=4, full validation
python examples/run_svmd.py --stopc 2              # change stopping criterion
python examples/run_svmd.py --max-modes 8          # cap modes
python examples/run_svmd.py --compare-prototype    # live parity check vs prototype
python examples/run_svmd.py --no-ref --no-plot     # fastest run
```

Saved example outputs:

```text
results/validation_output.txt
results/debug_trace_output.txt
```

If MATLAB is available:

```matlab
cd('third_party/svmd_original_demo');
test_svmd
```

## Sample Output

The Python validation run currently prints a result like this:

```text
Computed modes: 15, samples per mode: 7500
[validation] Reconstruction
  rel_recon_err        : 6.355475e-02
  freq_recon_err       : 6.355475e-02
[validation] Mode Matching
  matched_modes        : 15
  mean_abs_corr        : 9.999998e-01
[validation] Spectrum
  -- [MATLAB Bug (Simulated)] --
  uhat_nrmse_bug       : 7.969318e-05
  -- [Corrected] --
  uhat_nrmse_corr      : 1.073298e+00
```

This is intentionally useful for readers: it immediately shows that the project is not only about reproducing modes, but also about auditing how validation metrics differ between a bug-compatible reference view and a mathematically corrected view.

## What A Reviewer Can Understand From This Package

- how the Python translation is implemented
- what original MATLAB assets were used as the baseline
- what data was used for parity checking
- how the debugging process was structured
- why the project became an engineering-audit problem rather than a simple code port

## Why This Package Exists

This package is designed to be understandable to a hiring manager, interviewer, collaborator, or another code agent without extra verbal context.

The intended takeaway is:

- this was not random trial-and-error debugging
- the work followed a traceable validation process
- the code, reference, and comparison data are bundled together so the investigation can be reproduced

## Attribution

The SVMD method itself comes from the original work by Mojtaba Nazari and Sayed Mahmoud Sakhaei. The bundled MATLAB files and reference data are included only as a technical baseline for translation and validation. See `docs/THIRD_PARTY_NOTICE.md` and `third_party/svmd_original_demo/license.txt`.
