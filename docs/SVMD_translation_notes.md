# SVMD MATLAB → Python/C++ Translation Notes

- `sgolayfilt(signal, 8, 25)`  
  - Python: `scipy.signal.savgol_filter(signal, window_length=25, polyorder=8, mode="interp")` gives matching behavior.
  - Edge handling matters; `interp` matches MATLAB’s default for sgolayfilt on vectors.

- Mirror extension in `svmd.m`  
  - MATLAB indices: first half reversed, then full signal, then second half reversed.  
    Python equivalent: `np.concatenate([sig[:T//2][::-1], sig, sig[T//2:][::-1]])`.
  - Length becomes `2*T`, with both signal and noise mirrored.

- Frequency grid  
  - `t = (1:T)/T; omega_freqs = t - 0.5 - 1/T`.  
  - Keep the same grid to align center-frequency estimation and reconstruction.

- One-sided spectrum  
  - MATLAB uses `fftshift(fft(f))` then zeros the negative half (`1:T/2`).  
  - Python: `f_hat = fftshift(fft(f)); f_hat[:T//2] = 0`.

- Alpha growth schedule  
  - MATLAB grows `Alpha` via a log/exp schedule with flags `m`, `bf`; it warm-starts with the previous mode estimate.  
  - In the Python prototype we simplified to “double until near max, then jump to max-1” while warm-starting. If tighter parity is needed, port the exact `m/bf` logic.

- Dual variable `lambda` and `tau`  
  - Demo sets `tau = 0`, so `lambda` stays zero; we omit it.  
  - If future demos set `tau > 0`, reintroduce `lambda` terms in the numerator/denominator updates.

- Stopping criteria (4 options)  
  - Demo ECG uses stopc=4 (power of last mode). Other criteria rely on noise power or BIC; keep formulas identical if parity is required.

- Reconstruction  
  - After modes are collected, MATLAB rebuilds full spectra (conjugate symmetry), iFFT back, then removes mirror: keep only `T/2 ... 3*T/2` (i.e., middle half).  
  - Sorting by `omega` afterward ensures modes are ordered low→high frequency.

- Parity references  
  - `signal.csv`, `params.csv`, `u.csv`, `omega.csv`, `uhat_real.csv`, `uhat_imag.csv` in `SVMD original demo/` are good numerical checkpoints for any port.
