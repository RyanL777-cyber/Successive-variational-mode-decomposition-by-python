# Examples

This folder shows the two fastest entry points for a reviewer.

## 1. Full Python parity validation

Run:

```bash
python examples/run_validation.py
```

What it does:

- runs the translated Python SVMD implementation
- forces `stopc=2` for the public validation example
- loads the bundled parity reference data
- prints reconstruction and spectrum validation metrics

## 2. Short debug trace

Run:

```bash
python examples/run_debug_trace.py
```

What it does:

- runs only the first few extracted modes
- prints one-sided accumulation diagnostics
- is useful for demonstrating how the parity investigation was performed

## MATLAB reference run

If MATLAB is available, the bundled original reference demo can be run from:

```matlab
cd('third_party/svmd_original_demo');
test_svmd
```

That uses the included `ECG.mat` together with the original `svmd.m`.
