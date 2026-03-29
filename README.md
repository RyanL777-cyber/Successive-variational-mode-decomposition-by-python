# SVMD Translation Audit

This folder is organized as a GitHub-ready package for an SVMD translation and validation project.

It contains three things in one place:

- my Python translation code
- the minimum original MATLAB reference files required for comparison
- the reference data used for parity checks

The point is not only to show a port of SVMD. The stronger engineering story is the audit process: tracing why a MATLAB-to-Python translation can look correct at the mode level while still disagree on some validation metrics, and narrowing that gap with controlled experiments instead of heuristic edits.

## What Is Included

- `src/svmd_prototype.py`
  - the main Python translation and validation entry point
- `third_party/svmd_original_demo/`
  - bundled original MATLAB reference code and the minimum reference assets needed for reproduction
- `examples/`
  - runnable entry points for a quick validation demo and a shorter debug-style run
- `results/`
  - saved outputs generated from the bundled example runs
- `docs/ENGINEERING_CASE_STUDY.md`
  - the interview-ready writeup of the debugging process
- `docs/SVMD_translation_notes.md`
  - notes collected during MATLAB-to-Python translation
- `docs/THIRD_PARTY_NOTICE.md`
  - copyright and redistribution guidance for the bundled third-party files

## Repo Layout

```text
For github/
|- README.md
|- requirements.txt
|- src/
|  `- svmd_prototype.py
|- examples/
|  |- README.md
|  |- run_validation.py
|  `- run_debug_trace.py
|- results/
|  |- README.md
|  |- validation_output.txt
|  `- debug_trace_output.txt
|- docs/
|  |- ENGINEERING_CASE_STUDY.md
|  |- SVMD_translation_notes.md
|  `- THIRD_PARTY_NOTICE.md
`- third_party/
   `- svmd_original_demo/
      |- README.md
      |- license.txt
      |- svmd.m
      |- test_svmd.m
      |- ECG.mat
      |- signal.csv
      |- params.csv
      |- u.csv
      |- omega.csv
      |- uhat_real.csv
      `- uhat_imag.csv
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main Python parity validation:

```bash
python examples/run_validation.py
```

This public validation wrapper runs the Python implementation with `stopc=2`.

Run a shorter debug-oriented example:

```bash
python examples/run_debug_trace.py
```

Saved example outputs can be found in:

```text
results/validation_output.txt
results/debug_trace_output.txt
```

If MATLAB is available, run the bundled original reference demo:

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
