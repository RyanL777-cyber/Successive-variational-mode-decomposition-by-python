# Bundled Reference Assets

This folder contains the minimum third-party files needed to explain and reproduce the SVMD parity investigation.

## Included MATLAB reference code

- `svmd.m`
- `test_svmd.m`
- `license.txt`

## Included parity data

- `signal.csv`
- `params.csv`
- `u.csv`
- `omega.csv`
- `uhat_real.csv`
- `uhat_imag.csv`

## Included original example signal

- `ECG.mat`

## Why these files are here

They cover the two public-facing use cases of this repo package:

- run the original MATLAB reference example
- run the Python parity check against exported reference outputs

Files not required for those two tasks were intentionally left out to keep the package focused.
