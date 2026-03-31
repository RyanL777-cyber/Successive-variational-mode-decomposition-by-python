# Examples

Three runnable entry points, covering both the original prototype and the refactored OOP package.

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

## 3. OOP package runner (refactored version)

Run:

```bash
python examples/run_svmd.py
```

Common options:

```bash
python examples/run_svmd.py --stopc 2          # reconstruction-based stopping
python examples/run_svmd.py --max-modes 8      # cap at 8 modes
python examples/run_svmd.py --no-plot          # skip matplotlib
python examples/run_svmd.py --compare-prototype  # verify parity with svmd_prototype.py
python examples/run_svmd.py --no-ref --no-plot   # fastest: no MATLAB reference, no plot
```

What it does:

- uses the refactored `src/svmd/` package (Strategy Pattern + OOP)
- loads the same bundled reference data as the prototype examples
- prints identical validation metrics to the prototype
- optional `--compare-prototype` flag confirms bit-for-bit parity on the spot

---

## MATLAB reference run

If MATLAB is available, the bundled original reference demo can be run from:

```matlab
cd('third_party/svmd_original_demo');
test_svmd
```

That uses the included `ECG.mat` together with the original `svmd.m`.
