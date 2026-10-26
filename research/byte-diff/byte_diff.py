#!/usr/bin/env python3
"""Locate raw byte differences without padding, normalizing or rewriting inputs."""
import argparse
import json
from pathlib import Path
import sys

# Reuse the preserved comparator without changing the frozen scripts inventory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from compare import compare

PREVIEW_BYTES = 16


def differing_ranges(original, candidate):
    """Yield maximal shared-byte mismatch runs, then any length-only tail.

    Bounds are file offsets, with an inclusive start and exclusive end. A tail
    is a separate range even when adjacent to a shared-byte mismatch.
    """
    start = None
    shared = min(len(original), len(candidate))
    for offset, (left, right) in enumerate(zip(original, candidate)):
        if left != right and start is None:
            start = offset
        elif left == right and start is not None:
            yield start, offset, 'changed'
            start = None
    if start is not None:
        yield start, shared, 'changed'
    if len(original) > shared:
        yield shared, len(original), 'candidate_missing'
    elif len(candidate) > shared:
        yield shared, len(candidate), 'candidate_extra'


def report(original, candidate, max_ranges=1000):
    if max_ranges < 0:
        raise ValueError('max_ranges must be nonnegative')
    result = compare(original, candidate)
    ranges = []
    total_ranges = 0
    for start, end, kind in differing_ranges(original, candidate):
        total_ranges += 1
        if len(ranges) < max_ranges:
            preview_end = min(end, start + PREVIEW_BYTES)
            ranges.append({
                'start': start,
                'end': end,
                'length': end - start,
                'kind': kind,
                'original_hex_prefix': original[start:preview_end].hex(),
                'candidate_hex_prefix': candidate[start:preview_end].hex(),
            })
    missing = max(0, len(original) - len(candidate))
    extra = max(0, len(candidate) - len(original))
    result.update({
        'schema': 'raw-byte-diff-v1',
        'missing_candidate_bytes': missing,
        'extra_candidate_bytes': extra,
        'differing_or_missing_original_positions':
            result['different_positions_in_shared_length'] + missing,
        'total_differing_positions':
            result['different_positions_in_shared_length'] + missing + extra,
        'range_count': total_ranges,
        'ranges_omitted': total_ranges - len(ranges),
        'max_ranges': max_ranges,
        'preview_bytes_per_side': PREVIEW_BYTES,
        'ranges': ranges,
        'source_provenance_verified': False,
        'note': 'Offsets are positional file offsets, not aligned functions or '
                'semantic distance. End offsets are exclusive. Inputs are compared '
                'as supplied without padding or normalization. Byte equality alone '
                'does not prove compilation from source.',
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path, help='Captured payload to compare')
    parser.add_argument('candidate', type=Path, help='Unmodified compiler output')
    parser.add_argument('--max-ranges', type=int, default=1000,
                        help='Maximum ranges to include; 0 keeps only totals (default: 1000)')
    parser.add_argument('--output', type=Path, required=True,
                        help='Fresh JSON report path; existing files are never overwritten')
    args = parser.parse_args()
    if args.max_ranges < 0:
        parser.error('--max-ranges must be nonnegative')
    try:
        original = args.original.read_bytes()
        candidate = args.candidate.read_bytes()
        result = report(original, candidate, args.max_ranges)
        result.update(original_path=str(args.original), candidate_path=str(args.candidate))
        rendered = json.dumps(result, indent=2) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            output.write(rendered)
    except OSError as error:
        parser.error(str(error))
    print(rendered, end='')
    return 0 if result['full_byte_equality'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
