"""Offline source-provenance comparison of checksum-pinned crate archives.

No archive is extracted, imported, compiled or executed. Original contract
binaries are not inputs; target-coordinate observations come from saved evidence.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
METADATA_SHA256 = 'c0acb63ab9bf0873cd2cd4996fbae2ea25aa36e04fc1c1bbdc3cabbc2e8e3f26'
RECEIPTS_SHA256 = '283f921b1d904b346409147876b7f12725f04a28478e34159621390078585280'
EXTERNAL = {
    'repro/pump/metaplex-candidate-build-11/patch-source-inputs.json': '33b7864da5c9776ff0e1eb1d9aefa35e94e3c42e93025d32610d508b22ce4479',
    'repro/pump/metaplex-candidate-build-11/raw-difference-classification.json': 'feab02821178ed7e6f85293ac033ca898eef332fc47cfe0849c227b2a5e1cea4',
    'repro/pump/metaplex-zero-use-source-recovery/source-snapshot.tar.gz': 'cfce6c5037f2fa39ceb0d07fa5301d2ae663d354507a035872424df61b27808d',
    'repro/pump/metaplex-authentic-source-history/recovered-hunk-lineage.json': '8562b72105689bfb56a656a295afbff538a947b46394bc9c422ec178267e3f24',
    'repro/pump/metaplex-authentic-source-history/history-snapshots.json': '2c3e47558e1f4809e4e013495630dd60d17b9572cbf979939592b1b0506d1a0c',
    'repro/pump/metaplex-authentic-source-history/nearby-primary-downloads.json': '7c865876ef69461ffcfe6c0f2afa70114fce519035d0fbcf7fd6a909d0e079a2',
}
SOURCE_PREFIX = 'programs/token-metadata/program/'
UTILIZE = 'src/processor/uses/utilize.rs'
TWO_DISJUNCTS = 'if number_of_uses > metadata_uses.total || number_of_uses > metadata_uses.remaining {'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_read(path, expected):
    if path.is_symlink():
        raise ValueError(f'Symlink input: {path}')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError(f'SHA-256 mismatch: {path}')
    return raw


def members(raw):
    """Read regular members in memory, rejecting ambiguity and unsafe names."""
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        total = 0
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or '\\' in member.name:
                raise ValueError(f'Unsafe archive name: {member.name}')
            if member.isdir():
                continue
            if not member.isfile() or member.name in result:
                raise ValueError(f'Nonregular or duplicate archive member: {member.name}')
            total += member.size
            if member.size > 4 * 1024 * 1024 or total > 16 * 1024 * 1024:
                raise ValueError('Archive member size limit exceeded')
            result[member.name] = archive.extractfile(member).read()
    return result


def selected_versions(metadata):
    if metadata['crate']['name'] != 'mpl-token-metadata':
        raise ValueError('Unexpected crate')
    rows = [v for v in metadata['versions'] if v['num'].startswith('1.')
            or v['num'] in ('2.0.0-beta.1', '2.0.0')]
    if len({v['num'] for v in rows}) != len(rows):
        raise ValueError('Duplicate registry version')
    return sorted(rows, key=lambda v: (v['created_at'], v['num']))


def normalized_lines(text):
    return [re.sub(r'\s+', '', line) for line in text.splitlines()]


def block_present(text, block):
    needle, haystack = normalized_lines(block), normalized_lines(text)
    return bool(needle) and any(haystack[i:i + len(needle)] == needle
                               for i in range(len(haystack) - len(needle) + 1))


def utilize_observation(name, raw):
    text = raw.decode('utf-8')
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines)
              if re.match(r'^pub fn process_utilize\s*\(', line)]
    if len(starts) != 1:
        raise ValueError(f'Expected one top-level process_utilize in {name}')
    start = starts[0]
    # This is a textual span bounded by top-level function declarations, not a
    # Rust parser or proof of semantics. Preserve full member identity separately.
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r'^(?:pub(?:\([^)]*\))?\s+)?fn\s+\w+', lines[i])), len(lines))
    body = '\n'.join(lines[start:end])
    flat = re.sub(r'\s+', ' ', body)
    return {
        'member': name, 'sha256': sha(raw), 'bytes': len(raw),
        'function_start_line': start + 1, 'function_end_line_exclusive': end + 1,
        'contains_exact_two_disjunct_guard': TWO_DISJUNCTS in flat,
        'literal_zero_equality_in_function': bool(re.search(
            r'number_of_uses\s*==\s*0\b|\b0\s*==\s*number_of_uses', body)),
        'metadata_unwrap_lines': [i + 1 for i in range(start, end)
                                  if 'metadata.uses.unwrap()' in lines[i]],
        'checked_sub_occurrences_in_function': body.count('.checked_sub(number_of_uses)'),
    }


def analyze(package=PACKAGE, repo=REPO):
    package, repo = Path(package), Path(repo)
    metadata = json.loads(checked_read(package / 'crate-metadata.json', METADATA_SHA256))
    receipt = json.loads(checked_read(package / 'download-receipts.json', RECEIPTS_SHA256))
    if receipt['metadata_sha256'] != METADATA_SHA256:
        raise ValueError('Acquisition metadata binding differs')
    inputs = {name: checked_read(repo / name, digest) for name, digest in EXTERNAL.items()}
    source_map = json.loads(inputs[next(p for p in EXTERNAL if p.endswith('patch-source-inputs.json'))])
    recovered = members(inputs[next(p for p in EXTERNAL if p.endswith('source-snapshot.tar.gz'))])
    if set(recovered) != set(source_map['patched']):
        raise ValueError('Recovered source inventory differs')
    for name, raw in recovered.items():
        if sha(raw) != source_map['patched'][name]:
            raise ValueError(f'Recovered source mismatch: {name}')
    coordinates = json.loads(inputs[next(p for p in EXTERNAL if p.endswith('raw-difference-classification.json'))])['different_source_locations']
    hunks = json.loads(inputs[next(p for p in EXTERNAL if p.endswith('recovered-hunk-lineage.json'))])
    history = json.loads(inputs[next(p for p in EXTERNAL if p.endswith('history-snapshots.json'))])
    downloads = json.loads(inputs[next(p for p in EXTERNAL if p.endswith('nearby-primary-downloads.json'))])
    previous = {(group['recovered_path'], row['sha256']) for group in history
                for row in group['unique_accessible_sources']}
    previous.update((row['recovered_path'], row['sha256']) for row in downloads if 'sha256' in row)
    selected = selected_versions(metadata)
    receipts = {r['version']: r for r in receipt['archives']}
    if len(receipts) != len(receipt['archives']) or set(receipts) != {v['num'] for v in selected}:
        raise ValueError('Acquisition receipt inventory differs')
    expected_archives = {f'mpl-token-metadata-{v["num"]}.crate' for v in selected}
    if {p.name for p in (package / 'archives').iterdir()} != expected_archives:
        raise ValueError('Archive inventory differs from selected registry versions')
    versions, source_pairs = [], set()
    for version in selected:
        number = version['num']
        archive_name = f'mpl-token-metadata-{number}.crate'
        raw = checked_read(package / 'archives' / archive_name, version['checksum'])
        observed = receipts[number]
        if not (observed['verified'] is True and observed['status'] == 200
                and observed['sha256'] == observed['expected_sha256'] == version['checksum']
                and observed['bytes'] == len(raw) and observed['saved'] == f'archives/{archive_name}'
                and observed['url'] == f'https://crates.io/api/v1/crates/mpl-token-metadata/{number}/download'
                and observed['final_url'] == f'https://static.crates.io/crates/mpl-token-metadata/{archive_name}'):
            raise ValueError(f'Acquisition receipt differs: {number}')
        all_files = members(raw)
        prefix = f'mpl-token-metadata-{number}/'
        if any(not name.startswith(prefix) for name in all_files):
            raise ValueError(f'Unexpected archive prefix: {number}')
        files = {name[len(prefix):]: data for name, data in all_files.items()}
        manifest = tomllib.loads(files['Cargo.toml'].decode())
        if (manifest['package']['name'], manifest['package']['version']) != ('mpl-token-metadata', number):
            raise ValueError(f'Package identity differs: {number}')
        row = {
            'version': number, 'published_at': version['created_at'], 'yanked_at_observation': version['yanked'],
            'archive': f'archives/{archive_name}', 'archive_bytes': len(raw), 'archive_sha256': sha(raw),
            'regular_member_count': len(files),
            'declared_vcs_info': json.loads(files['.cargo_vcs_info.json'])
                                 if '.cargo_vcs_info.json' in files else None,
            'vcs_commit_association_independently_verified': False,
            'utilize': None, 'source_files': [], 'hunk_observations': [], 'coordinate_observations': [],
        }
        handler = UTILIZE if UTILIZE in files else 'src/processor.rs' if 'src/processor.rs' in files else None
        if handler:
            row['utilize'] = utilize_observation(handler, files[handler])
        for name, digest in sorted(source_map['patched'].items()):
            relative = name.removeprefix(SOURCE_PREFIX)
            found = relative in files
            item = {'recovered_path': name, 'member': relative, 'present': found}
            if found:
                data = files[relative]
                source_pairs.add((name, sha(data)))
                item.update(sha256=sha(data), bytes=len(data),
                            exact_recovered_file_match=sha(data) == digest,
                            whitespace_insensitive_recovered_match=
                            re.sub(rb'\s+', b'', data) == re.sub(rb'\s+', b'', recovered[name]),
                            present_in_prior_git_history_packet=(name, sha(data)) in previous)
            row['source_files'].append(item)
        for entry in hunks:
            relative = entry['path'].removeprefix(SOURCE_PREFIX)
            if relative not in files:
                continue
            text = files[relative].decode('utf-8')
            for index, change in enumerate(entry['changes']):
                row['hunk_observations'].append({
                    'recovered_path': entry['path'], 'hunk_index': index,
                    'nonempty_added_block': bool(normalized_lines(change['added_source'])),
                    'added_block_present_as_consecutive_normalized_lines': block_present(text, change['added_source']),
                })
        for index, record in enumerate(coordinates):
            name = 'programs/token-metadata/' + record['file']
            relative = name.removeprefix(SOURCE_PREFIX)
            if relative not in files:
                continue
            lines = files[relative].decode('utf-8').splitlines()
            anchor = recovered[name].decode('utf-8').splitlines()[record['candidate_line'] - 1].strip()
            at_target = lines[record['original_line'] - 1].strip() if record['original_line'] <= len(lines) else None
            row['coordinate_observations'].append({
                'saved_coordinate_record_index': index, 'recovered_path': name,
                'target_line': record['original_line'], 'accepted_anchor': anchor,
                'published_source_at_target_line': at_target,
                'exact_stripped_anchor_at_target_line': at_target == anchor,
                'anchor_occurrence_lines': [i + 1 for i, line in enumerate(lines) if line.strip() == anchor],
            })
        versions.append(row)
    handlers = [v['utilize'] for v in versions if v['utilize'] is not None]
    summary = {
        'archives': len(versions), 'archive_bytes': sum(v['archive_bytes'] for v in versions),
        'program_handler_versions': len(handlers),
        'versions_without_program_handler': [v['version'] for v in versions if v['utilize'] is None],
        'distinct_utilize_member_hashes': len({v['sha256'] for v in handlers}),
        'two_disjunct_guard_versions': sum(v['contains_exact_two_disjunct_guard'] for v in handlers),
        'literal_zero_guard_versions': sum(v['literal_zero_equality_in_function'] for v in handlers),
        'distinct_recovered_path_source_pairs': len(source_pairs),
        'pairs_not_in_prior_git_history_packet': len(source_pairs - previous),
        'exact_recovered_file_matches': sum(f.get('exact_recovered_file_match', False) for v in versions for f in v['source_files']),
        'whitespace_insensitive_recovered_file_matches': sum(f.get('whitespace_insensitive_recovered_match', False) for v in versions for f in v['source_files']),
        'matching_added_hunk_observations': sum(h['added_block_present_as_consecutive_normalized_lines'] for v in versions for h in v['hunk_observations']),
        'matching_coordinate_anchor_observations': sum(c['exact_stripped_anchor_at_target_line'] for v in versions for c in v['coordinate_observations']),
    }
    return {'schema': 'metaplex-published-source-v1', 'metadata_sha256': METADATA_SHA256,
            'download_receipts_sha256': RECEIPTS_SHA256,
            'external_sha256': EXTERNAL, 'summary': summary, 'versions': versions,
            'scope': 'Saved registry distributions and literal source observations only. '
                     'No original binary parsing, compilation, VM execution, source promotion, '
                     'historical build attribution, semantic or byte-identity proof.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=REPO)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--output', type=Path, help='Fresh JSON output; omit to verify saved findings.json.gz')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('Output already exists')
    try:
        result = analyze(args.package, args.repo)
        if args.output is None:
            if json.loads(gzip.decompress((args.package / 'findings.json.gz').read_bytes())) != result:
                raise ValueError('Saved findings differ from recomputation')
        else:
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.error(str(error))
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
