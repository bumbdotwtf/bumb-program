"""Replay sealed hosted observations offline; never execute a retained compiler."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

import observe

PACKAGE = Path(__file__).resolve().parent
RECEIPTS_SHA256 = '69866a7976b816111d643ab49a505428587bc007311ab8e5cc7b8a103140b062'
RUNS = {
    40332914951: ('6c5a4c926a3bbb4b829490429d7f5938422ef29f', 'failure',
                  'd173a8e3837838491b1dcf3c6049c92016da63fb972dff411ce9ec996554db14'),
    40333550925: ('91bec1a763af9ddbbd6175ceb339f7ccf79d7eb5', 'success',
                  '5997bf576992f188487280cd2d8f4a701a8302a6fc4592127a37768ad82d0cbb'),
}
require, sha = observe.require, observe.sha


def checked(raw, digest, label):
    require(sha(raw) == digest, 'Changed evidence: ' + label)
    return raw


def read_artifact(package, receipt):
    run = receipt['run']
    run_id = run['id']
    head, conclusion, digest = RUNS[run_id]
    require(run['head_sha'] == head and run['conclusion'] == conclusion
            and run['status'] == 'completed' and run['run_attempt'] == 1,
            'Run revision or conclusion differs')
    require(run['repository']['full_name'] == 'startrack3r/pumpfun-source'
            and run['actor']['login'] == 'startrack3r', 'Run identity differs')
    job, = receipt['jobs']['jobs']
    require(job['run_id'] == run_id and job['conclusion'] == conclusion, 'Job receipt differs')
    artifact, = receipt['artifacts']['artifacts']
    require(artifact['workflow_run']['head_sha'] == head
            and artifact['workflow_run']['id'] == run_id
            and artifact['digest'] == 'sha256:' + digest, 'Artifact provenance differs')
    raw = checked((package / f'{run_id}.zip').read_bytes(), digest, f'{run_id}.zip')
    require(len(raw) == artifact['size_in_bytes'], 'Artifact length differs')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and all('/' not in n and '\\' not in n for n in names),
                'Unexpected artifact names')
        members = {name: archive.read(name) for name in names}
    require(members['source-commit.txt'] == (head + '\n').encode(), 'Executed revision differs')
    for source in receipt['source_files']:
        raw = checked(members[source['member']], source['sha256'], source['member'])
        require(len(raw) == source['bytes'], 'Source length differs')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == source['git_blob_sha1'], 'Source Git blob differs')
    return members


def check_commands(members, state):
    commands = {}
    expected_members = {'observation.json', 'observe.py', 'source-commit.txt', 'executed-workflow.yml',
                        'archive.json', 'archive-inventory.json.gz', 'loaded-libraries.json'}
    for row in state['commands']:
        require(row['label'] not in commands, 'Duplicate command label')
        # All queries succeeded in this particular retained run. Future failures must
        # keep their own evidence instead of being substituted into this fixture.
        require(row['returncode'] == 0, 'Retained command failed: ' + row['label'])
        commands[row['label']] = row
        for channel in ('stdout', 'stderr'):
            record = row[channel]
            require(record['file'] == row['label'] + '.' + channel + '.log', 'Log name differs')
            raw = checked(members[record['file']], record['sha256'], record['file'])
            require(len(raw) == record['bytes'], 'Log length differs')
            expected_members.add(record['file'])
    require(set(members) == expected_members, 'Artifact member inventory differs')
    return commands


def derive(members):
    state = json.loads(members['observation.json'])
    require(state['status'] == 'OBSERVED' and state['image'] == observe.IMAGE, 'Observation did not succeed')
    require(state['historical_loaded_library_identity_proven'] is False
            and state['actual_historical_target_cpu'] is None
            and state['program_builds'] == state['program_replays'] == 0,
            'Evidence scope was broadened')
    commands = check_commands(members, state)

    def text(label, channel='stdout'):
        return members[commands[label][channel]['file']].decode('utf-8')

    def command(label, expected):
        require(commands[label]['command'] == expected, 'Command differs: ' + label)

    inspected, = json.loads(text('inspect-image'))
    require(inspected['Id'] == observe.IMAGE_ID and observe.IMAGE in inspected['RepoDigests'], 'Image differs')
    start = commands['start-container']['command']
    container = text('start-container').strip()
    require(re.fullmatch('[0-9a-f]{64}', container), 'Invalid container identifier')
    archive_path = commands['download-archive']['command'][-2]
    require(archive_path.endswith('/downloads/platform-tools-linux-x86_64.tar.bz2'), 'Archive path differs')
    command('start-container', ['docker', 'run', '--rm', '--detach', '--name', start[5],
        '--platform', 'linux/amd64', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,noexec,nosuid,nodev,size=16m',
        '--tmpfs', '/root/.cache:rw,exec,nosuid,nodev,size=2g', '--mount',
        'type=bind,source=' + archive_path + ',target=/input/platform-tools.tar.bz2,readonly',
        '--entrypoint', 'sleep', observe.IMAGE, '1800'])
    prefix = ['docker', 'exec', container]
    command('cold-compiler-absent', prefix + ['test', '!', '-e', observe.RUSTC])
    command('install-authenticated-archive', prefix + ['tar', '--no-same-owner', '--no-same-permissions',
        '-xjf', '/input/platform-tools.tar.bz2', '-C', observe.CACHE])
    command('stop-container', ['docker', 'stop', '--time', '1', container])

    archive = json.loads(members['archive.json'])
    inventory = json.loads(gzip.decompress(members['archive-inventory.json.gz']))
    require(archive['url'] == observe.ARCHIVE_URL and archive['bytes'] == observe.ARCHIVE_BYTES
            and archive['sha256'] == observe.ARCHIVE_SHA256 and archive['publisher_digest'] is None,
            'Archive identity differs')
    require(len(inventory) == archive['members'] == 2426, 'Archive inventory differs')
    require(len({row['name'] for row in inventory}) == len(inventory), 'Duplicate archive entry')
    for index, (name, (size, digest)) in enumerate(observe.MEMBERS.items()):
        require(archive['selected'][name]['bytes'] == size and archive['selected'][name]['sha256'] == digest,
                'Selected archive member differs')
        label = f'installed-member-{index:02d}'
        command(label, prefix + ['sha256sum', observe.CACHE + '/' + name])
        require(text(label).strip() == digest + '  ' + observe.CACHE + '/' + name, 'Installed member differs')

    command('rustc-loaded-version', ['docker', 'exec', '-e', 'LD_DEBUG=libs', container,
                                   observe.RUSTC, '--version', '--verbose'])
    initializers = observe.loaded_initializers(text('rustc-loaded-version', 'stderr'))
    require(initializers == state['loaded_library_initializers'], 'Loader initializer summary differs')
    loaded = []
    for index, path in enumerate(initializers):
        path_label, hash_label = f'loaded-library-{index:02d}-path', f'loaded-library-{index:02d}-sha256'
        command(path_label, prefix + ['readlink', '-f', path])
        resolved = text(path_label).strip()
        command(hash_label, prefix + ['sha256sum', resolved])
        digest, recorded_path = text(hash_label).strip().split('  ', 1)
        require(recorded_path == resolved and re.fullmatch('[0-9a-f]{64}', digest), 'Library hash record differs')
        loaded.append({'reported_path': path, 'resolved_path': resolved, 'sha256': digest})
    require(loaded == json.loads(members['loaded-libraries.json']), 'Loaded-library summary differs')
    driver, = [row for row in loaded if row['resolved_path'] == observe.CACHE + '/' + observe.DRIVER]
    require(driver['sha256'] == observe.MEMBERS[observe.DRIVER][1], 'Loaded driver differs from archive')

    command('rustc-targets', prefix + [observe.RUSTC, '--print', 'target-list'])
    targets = [row for row in text('rustc-targets').splitlines() if 'bpf' in row or 'sbf' in row]
    require(targets == state['available_bpf_sbf_targets'] and len(targets) == 4, 'Target summary differs')
    capabilities = []
    for index, target in enumerate(targets):
        for label, arguments in [('spec', ['-Z', 'unstable-options', '--print', 'target-spec-json']),
                                  ('cpus', ['--print', 'target-cpus']), ('features', ['--print', 'target-features'])]:
            command(f'target-{index:02d}-{label}', prefix + [observe.RUSTC, *arguments, '--target', target])
        spec = json.loads(text(f'target-{index:02d}-spec'))
        cpus = [line.strip() for line in text(f'target-{index:02d}-cpus').splitlines()[1:] if line.strip()]
        features = re.findall(r'^    (\S+)\s+- ', text(f'target-{index:02d}-features'), re.M)
        capabilities.append({'target': target, 'llvm_target': spec['llvm-target'],
            'spec_features': spec.get('features'), 'spec_explicit_cpu': spec.get('cpu'),
            'available_cpus': cpus, 'available_features': features})
    require(len(commands) == 44 and len(initializers) == 9, 'Observation count differs')
    require(text('rustc-loaded-version') == state['rustc_version'], 'Compiler version summary differs')
    return {'successful_run': 40333550925, 'commands': len(commands), 'artifact_members': len(members),
        'archive_bytes': archive['bytes'], 'archive_members': len(inventory),
        'rustc_version': text('rustc-loaded-version'), 'initialized_libraries': loaded,
        'capabilities': capabilities, 'fresh_loaded_driver_matches_archive': True,
        'historical_loaded_library_identity_proven': False, 'actual_historical_target_cpu': None,
        'program_builds': 0, 'program_replays': 0, 'raw_target_byte_improvement_claimed': False}


def verify(package=PACKAGE):
    raw = checked(gzip.decompress((package / 'receipts.json.gz').read_bytes()), RECEIPTS_SHA256, 'receipts')
    receipts = json.loads(raw)
    require([row['run']['id'] for row in receipts] == list(RUNS), 'Run set differs')
    failed = read_artifact(package, receipts[0])
    failure = json.loads(failed['observation.json'])
    require(set(failed) == {'observation.json', 'observe.py', 'source-commit.txt', 'executed-workflow.yml'}
            and failure['status'] == 'FAILED' and failure['commands'] == []
            and failure['error_type'] == 'URLError' and 'Connection reset by peer' in failure['error'],
            'Original failed acquisition differs')
    observed = read_artifact(package, receipts[1])
    require((package / 'observe.py').read_bytes() == observed['observe.py'], 'Executed observer differs')
    result = derive(observed)
    result['retained_failed_run'] = 40332914951
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    args = parser.parse_args()
    print(json.dumps(verify(args.package), indent=2))
