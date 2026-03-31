# svmd Package — Developer Guide

All source lives under `src/svmd/`.

## Package Structure

```
src/svmd/
├── config.py               [CONFIG]      All hyperparameters
├── state.py                [DATA]        State dataclasses
├── interfaces.py           [CONTRACTS]   ABC interfaces (Strategy Pattern)
├── solver.py               [CONTROL]     3 nested loops — DO NOT put math here
├── pipeline.py             [API]         Top-level entry point
├── validation.py           [VALIDATION]  Metrics and reporting
├── backends/
│   ├── numpy_backend.py    [MATH CORE]   Current numpy implementation
│   └── cpp_backend.py      [FUTURE]      C++ ctypes stub
├── stopping/
│   └── criteria.py         [STRATEGY]    stopc 1~4 implementations
└── schedule/
    └── alpha.py            [STRATEGY]    Alpha growth schedule
```

---

## Which file to modify?

### I want to change a hyperparameter default

Edit `src/svmd/config.py` — `SVMDConfig` dataclass.

---

### I want to change the ADMM update formula / math

Edit `src/svmd/backends/numpy_backend.py` — `NumpyBackend.admm_step()`.

This is the **only** place where the core ADMM mathematics lives:
- Mode spectrum update: `u_hat_L[n+1] = numer / denom`
- Centre frequency update: energy-weighted centroid over positive frequencies
- Dual ascent: lambda update
- Convergence residuals: `udiff`, `primal_res`

Do **not** put math in `solver.py`.

---

### I want to change how the signal is preprocessed (mirror, FFT, noise)

Edit `src/svmd/backends/numpy_backend.py` — `NumpyBackend.preprocess()`.

Covers: Savitzky-Golay, mirror extension, FFT, one-sided masking, noise power.

---

### I want to change mode reconstruction (Hermitian symmetry, IFFT, sort)

Edit `src/svmd/backends/numpy_backend.py` — `NumpyBackend.reconstruct_modes()`.

---

### I want to change when the algorithm stops

Edit `src/svmd/stopping/criteria.py` — the relevant `StopXxx` class.

| stopc | Class |
|-------|-------|
| 1 | `StopNoise.should_stop()` |
| 2 | `StopRecon.should_stop()` |
| 3 | `StopBIC.should_stop()` |
| 4 | `StopPolm.should_stop()` |

To add a new stopping criterion (stopc=5):
1. Add `class StopMyNew(IStoppingCriterion)` in `criteria.py`
2. Register it in `make_stopping_criterion()`

---

### I want to change the alpha growth schedule

Edit `src/svmd/schedule/alpha.py` — `LinearAlphaSchedule.advance()`.

The schedule logic mirrors the MATLAB prototype exactly:
- `m`, `bf` counters control the log-to-linear transition
- When `is_done()` returns True, the middle loop exits
- `needs_warm_restart()` triggers ADMM state reinitialisation

---

### I want to add a new output feature for feature extraction

Edit `src/svmd/pipeline.py` — `SVMDPipeline.extract_features()`.

Currently returns `[centre_omega, energy, std, kurtosis]` per mode.

---

### I want to replace numpy math with C++

Edit `src/svmd/backends/cpp_backend.py` — fill in `CppBackend`:
1. Set `_DEFAULT_DLL` path to the built DLL
2. Declare argtypes/restype in `_setup_signatures()`
3. Implement `preprocess()`, `admm_step()`, `reconstruct_modes()`

Then pass `CppBackend()` to `SVMDPipeline`:
```python
from svmd import SVMDConfig, SVMDPipeline
from svmd.backends import CppBackend

pipeline = SVMDPipeline(cfg, backend=CppBackend("path/to/svmd_core.dll"))
```
`SVMDSolver`, all stopping criteria, and alpha schedule remain unchanged.

---

## Files that must NOT be modified (math contracts)

| File | Why |
|------|-----|
| `src/svmd/interfaces.py` | Defines the ABC contracts that both `NumpyBackend` and `CppBackend` must satisfy. Changing method signatures breaks the swap guarantee. |
| `src/svmd/state.py` | Data contracts between layers. Changing field names/types requires updating every backend. |
| `src/svmd/solver.py` | Pure control logic with no math. Correct functioning depends on backends honouring the interface exactly. |

---

## Layer diagram

```
SVMDPipeline.run(signal)
       |
       ├── IComputeBackend.preprocess()      ← NumpyBackend or CppBackend
       |
       └── SVMDSolver.solve()
             |
             ├── [OUTER LOOP]  extract one mode per iteration
             |     |
             |     ├── [MIDDLE LOOP]  IAlphaSchedule.advance()
             |     |     |
             |     |     └── [INNER LOOP]  IComputeBackend.admm_step()
             |     |
             |     ├── IComputeBackend.compute_h_row()
             |     └── IStoppingCriterion.should_stop()
             |
             └── IComputeBackend.reconstruct_modes()
```

The **only** thing that changes when moving to C++: replace `NumpyBackend` with `CppBackend` at construction time. Everything else is untouched.

---

## Key implementation note: StopPolm alpha value

In the MATLAB prototype, the `stopc==4` polm computation uses `Alpha` that has **already been reset to `min_alpha`** (not the accepted alpha). `StopPolm` therefore correctly reads `cfg.min_alpha`, not `svmd_state.alpha_hist[-1]`. Do not change this.
