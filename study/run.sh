#!/usr/bin/env bash
# Run a python script inside the nix-provided env with pandas/numpy.
cd "$(dirname "$0")"
exec nix-shell -p "python3.withPackages(ps: with ps; [pandas numpy pyarrow])" --run "python3 $*"
