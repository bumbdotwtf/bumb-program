#!/usr/bin/env python3
"""Build native recovered fee routing for original-versus-recovered tests."""
import argparse
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', type=pathlib.Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
src = ROOT / 'programs/pump-fees/recovered'
math = out / 'libpump_fees_math.rlib'
quote = out / 'libpump_quote_fees.rlib'
commands = [
    ['--crate-name', 'pump_fees_math', '--crate-type', 'rlib', str(src / 'fee_selection.rs'), '-o', str(math)],
    ['--crate-name', 'pump_quote_fees', '--crate-type', 'rlib', '--extern', f'pump_fees_math={math}', str(src / 'quote_fees.rs'), '-o', str(quote)],
    ['--extern', f'pump_fees_math={math}', '--extern', f'pump_quote_fees={quote}', '-L', f'dependency={out}', str(src / 'quote_fees_host.rs'), '-o', str(out / 'quote-fees-host')],
]
for cmd in commands:
    subprocess.run(['rustc', '--edition=2021', '-O', *cmd], check=True)
print(out / 'quote-fees-host')
