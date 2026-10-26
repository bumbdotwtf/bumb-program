"""Replay the bounded Git-location check for published Utilize source members."""
import argparse
import gzip
import json
from pathlib import Path
import tarfile
import tomllib

import analyze

OBSERVATIONS_SHA256 = 'd119c9a72c5d04255c51e5636fcd170c8f495404ce4bc8ef14081409849b7bfa'


def expected_queries(package, findings):
    queries = []
    for version in findings['versions']:
        vcs, handler = version['declared_vcs_info'], version['utilize']
        if vcs is None or handler is None:
            continue
        files = analyze.members(analyze.checked_read(package / version['archive'], version['archive_sha256']))
        prefix = f'mpl-token-metadata-{version["version"]}/'
        manifest = tomllib.loads(files[prefix + 'Cargo.toml.orig'].decode('utf-8'))
        repository = manifest['package']['repository']
        if repository != 'https://github.com/metaplex-foundation/metaplex-program-library':
            raise ValueError('Unexpected declared program repository')
        commit = vcs['git']['sha1']
        path = vcs['path_in_vcs'] + '/' + handler['member']
        queries.append({
            'version': version['version'], 'declared_repository': repository,
            'commit': commit, 'path': path,
            'url': repository.replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + commit + '/' + path,
            'archive_member_sha256': handler['sha256'],
            'member_bytes': files[prefix + handler['member']],
        })
    return queries


def compare_observations(queries, observations):
    if [row['version'] for row in queries] != [row['version'] for row in observations]:
        raise ValueError('Git query inventory or order differs')
    rows = []
    for query, observed in zip(queries, observations):
        expected = {key: value for key, value in query.items() if key != 'member_bytes'}
        if any(observed.get(key) != value for key, value in expected.items()):
            raise ValueError('Declared Git query binding differs: ' + query['version'])
        row = dict(expected, archive_member_bytes=len(query['member_bytes']))
        if observed['is_error'] is True:
            error = observed['result']
            if not (error['error_code'] == 'NOT_FOUND' and error['error_data']['status'] == '404'
                    and error['error_data']['message'] == 'No commit found for the ref ' + query['commit']):
                raise ValueError('Unexpected unresolved-query response')
            row['outcome'] = 'declared_commit_unresolved_at_observation'
        elif observed['is_error'] is False and isinstance(observed['result'], str):
            raw = observed['result'].encode('utf-8')
            row.update(retrieved_bytes=len(raw), retrieved_sha256=analyze.sha(raw),
                       outcome='exact_member_match' if raw == query['member_bytes'] else 'different_member')
        else:
            raise ValueError('Unexpected Git query result')
        rows.append(row)
    return rows


def verify(package=analyze.PACKAGE, repo=analyze.REPO):
    package, repo = Path(package), Path(repo)
    findings = analyze.analyze(package, repo)
    raw = gzip.decompress((package / 'vcs-observations.json.gz').read_bytes())
    if analyze.sha(raw) != OBSERVATIONS_SHA256:
        raise ValueError('Git observation seal differs')
    observed = json.loads(raw)
    rows = compare_observations(expected_queries(package, findings), observed['observations'])
    summary = {
        'program_versions': findings['summary']['program_handler_versions'],
        'program_versions_without_vcs_metadata': [v['version'] for v in findings['versions']
                                                if v['utilize'] and v['declared_vcs_info'] is None],
        'queried_program_versions': len(rows),
        'exact_member_matches': sum(r['outcome'] == 'exact_member_match' for r in rows),
        'different_members': [r['version'] for r in rows if r['outcome'] == 'different_member'],
        'unresolved_declared_commits': [r['version'] for r in rows
                                        if r['outcome'] == 'declared_commit_unresolved_at_observation'],
    }
    return {'schema': 'metaplex-published-utilize-git-locations-v1',
            'observed_at': observed['observed_at'], 'observations_sha256': OBSERVATIONS_SHA256,
            'scope': 'One complete handler-bearing source member per declared program Git location. '
                     'GitHub retrieval observations, not independent Git-object attestation, '
                     'whole-archive Git association, historical build attribution or deployed byte identity. '
                     'An unresolved query does not establish global or historical absence.',
            'summary': summary, 'versions': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=analyze.PACKAGE)
    parser.add_argument('--repo', type=Path, default=analyze.REPO)
    parser.add_argument('--output', type=Path, help='Fresh JSON output; otherwise verify vcs-findings.json')
    args = parser.parse_args()
    if args.output is not None and (args.output.exists() or args.output.is_symlink()):
        parser.error('Output already exists')
    try:
        result = verify(args.package, args.repo)
        if args.output is None:
            if json.loads((args.package / 'vcs-findings.json').read_bytes()) != result:
                raise ValueError('Saved Git findings differ')
        else:
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(result, indent=2) + '\n')
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError) as error:
        parser.error(str(error))
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
