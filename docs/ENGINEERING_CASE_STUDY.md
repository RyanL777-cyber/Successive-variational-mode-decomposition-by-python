# Engineering Case Study

## Title

Tracing a Numerical Mismatch in an SVMD MATLAB-to-Python Translation

## Context

I was building toward a faster research pipeline for rolling-window and walk-forward experiments. The original SVMD reference code was in MATLAB, but the target stack needed to move toward Python first and eventually C++ for performance-critical components.

At first glance, the task looked like a standard algorithm port. In practice, it became a reproducibility problem: the translated implementation produced strong mode-level similarity, but some aggregate validation metrics still disagreed with the MATLAB reference.

## Problem

The hard part was not writing a Python version of SVMD. The hard part was deciding whether the mismatch came from:

- my implementation
- my validation method
- the reference behavior itself

That distinction mattered. If I guessed wrong, I would spend time fixing the wrong layer and carry a false assumption into the later C++ version.

## What I Did

I turned the work into a controlled debugging audit.

1. I added structural validation instead of relying on a single RMSE number.
2. I compared reconstruction error, one-sided frequency-domain error, mode matching, spectral overlap, and per-mode accumulation behavior.
3. I tested and ruled out several plausible causes one by one:
   - final reconstruction symmetry
   - stopping-rule choice
   - save-current versus save-previous mode timing
   - one-sided bin convention mismatches
4. I added trace-level diagnostics inside the ADMM loop and alpha schedule to inspect whether the solver was drifting or exiting early.
5. After ruling out the major implementation-side suspects, I separated the validation logic into two views:
   - a MATLAB-bug-compatible view for reference comparison
   - a mathematically corrected view for actual complex-spectrum error

## Key Finding

The important finding was that the visible discrepancy was not explained by a simple reconstruction mistake. The translation path was largely behaving as intended, but the comparison path for complex spectra likely contained a reference-side issue. In other words, the debugging process showed that matching the reported metric and being mathematically correct were not the same problem.

## Why This Matters

This project demonstrates a few engineering behaviors that matter in real production work:

- I did not blindly trust a reference implementation.
- I did not casually accuse the reference implementation either.
- I used experiments to narrow the search space instead of patching randomly.
- I separated algorithm correctness from validation correctness.
- I documented the result in a way that a future Python or C++ implementation can reuse.

## Short Interview Version

I was translating an SVMD research algorithm from MATLAB into Python as a step toward a faster C++-backed research stack. The port looked mostly correct at the mode level, but some validation numbers still disagreed with the MATLAB baseline. Instead of patching heuristically, I instrumented the solver, compared one-sided spectral accumulation, audited stopping behavior, and ruled out reconstruction and save-timing issues. That process showed the remaining discrepancy was most likely in the reference comparison path for complex spectra rather than in the main algorithm logic. The result was not just a translation; it was a reproducible engineering audit that made the next production step safer.

## Resume / Interview Framing

Useful phrases:

- "Built a trace-based validation harness for a MATLAB-to-Python translation of a numerically sensitive signal decomposition algorithm."
- "Systematically ruled out reconstruction, stopping, and state-timing explanations before isolating a likely reference-side validation issue."
- "Converted a research-code port into a reproducible engineering debugging case study suitable for future C++ productionization."
