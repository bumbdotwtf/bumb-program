"""Verify the pinned image's compiler-installation boundary without executing it."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
IMAGE = 'sha256:43206149a565ec35da95b1a909f4714f5d5f0d8241c31df24189e517acd18467'
LAYERS_SHA256 = '0bf5959df75c4f9c5c3dc43e3758d3a70354e4d5daff45423d4e3029d400adb7'
SDK_COMMIT = '8dd7d060a83a4310c14d9b931d4409fc1ad27117'
INSTALL_SHA256 = '428b42a324e89789e8d6ce732803032bb56f9165f79a5872217d896b8d7508ee'
SDK_SOURCE_SHA256 = 'e5ec6e0d5cc3ef59e250b67f3202980ace7f746a01110290c8d8d960df6fa0eb'
HISTORICAL = {
    'build-script.py': '840e72690b1b034a3f073ceb29cbdb0c56c4b6346b293b5fd9561c1d075a6cb2',
    'tool-versions.json': '2cc4c0b8aa6b9641d860d575aa8652521ab47493daf1b5c9457e005f8c6d6ece',
    'image-inspect.json': '6afecfca7094807a6f5fcbc679da9680a342a1551cd711f7a08c1cefc248bd45',
    'comparison.json': '9dc7dfb1ccd2c4b92ee6de5a9e2254f5e817e1cc8ed3e699428264b8ccf154d1',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, digest):
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    require(sha(raw) == digest, 'Changed evidence: ' + str(path))
    return raw


def inventory_bytes(rows):
    return (json.dumps(rows, separators=(',', ':')) + '\n').encode('utf-8')


def selected_member(name):
    return (name.endswith(('/cargo-build-sbf', '/cargo-build-bpf', '/rustc'))
            or '/sdk/sbf/scripts/' in name or name.endswith('/solana-release/version.yml'))


class HashedReader:
    def __init__(self, stream):
        self.stream, self.digest, self.count = stream, hashlib.sha256(), 0

    def read(self, size=-1):
        raw = self.stream.read(size)
        self.digest.update(raw)
        self.count += len(raw)
        return raw


def measure_layer(blob, expected):
    """Authenticate both tar representations, then read headers/selected files in memory."""
    digest = hashlib.sha256()
    count = 0
    with blob.open('rb') as stream:
        while raw := stream.read(1024 * 1024):
            digest.update(raw)
            count += len(raw)
    require(count == expected['compressed_bytes'] and 'sha256:' + digest.hexdigest() == expected['blob_digest'],
            'Compressed layer identity differs')
    inventory, selected, retained = [], [], {}
    with gzip.open(blob, 'rb') as decompressed:
        stream = HashedReader(decompressed)
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for member in archive:
                row = {'name': member.name, 'type': member.type.decode('ascii'), 'size': member.size,
                       'mode': member.mode, 'linkname': member.linkname}
                inventory.append(row)
                if member.isfile() and selected_member(member.name):
                    digest, contents = hashlib.sha256(), bytearray()
                    file = archive.extractfile(member)
                    while raw := file.read(1024 * 1024):
                        digest.update(raw)
                        if member.size < 1024 * 1024:
                            contents.extend(raw)
                    record = dict(row, sha256=digest.hexdigest())
                    if member.size < 1024 * 1024:
                        record['saved'] = 'selected/' + digest.hexdigest()
                        retained[record['saved']] = bytes(contents)
                    selected.append(record)
        # Include tar padding beyond the end marker in the uncompressed diff ID.
        while stream.read(1024 * 1024):
            pass
        require('sha256:' + stream.digest.hexdigest() == expected['diff_id']
                and stream.count == expected['uncompressed_bytes'], 'Uncompressed layer identity differs')
    require(sha(inventory_bytes(inventory)) == expected['inventory_raw_sha256'], 'Layer header inventory differs')
    require(selected == expected['selected'], 'Selected layer members differ')
    return inventory, retained


def check_cache_boundary(inventories):
    """Narrow proof for this image, not a general overlay-filesystem resolver."""
    roots = []
    for rows in inventories:
        for row in rows:
            path = PurePosixPath(row['name'])
            require(not path.is_absolute() and '..' not in path.parts, 'Noncanonical layer path')
            name = path.as_posix()
            if name == 'root':
                require(row['type'] == '5', 'Root home is not a directory')
                roots.append(row)
            require(name != 'root/.cache' and not name.startswith('root/.cache/'),
                    'Image contains a root cache entry; absence conclusion does not apply')
    require(roots, 'No root home directory observed')
    return roots


def verify(package=PACKAGE, repo=REPO, layers=None):
    package, repo = Path(package), Path(repo)
    manifest = json.loads(checked(package / 'manifest.json', IMAGE.split(':')[1]))
    config = json.loads(checked(package / 'config.json', manifest['config']['digest'].split(':')[1]))
    checked(package / 'manifest-receipts.json.gz', '1a6ebe148aaba785db3905b58b131a3815262e5913eadd9b0f00489f87db37bd')
    upstream = json.loads(checked(package / 'upstream-receipts.json.gz',
                                 '115551476c86215f2c87953df91e74d0800e2f70f134a746aac9966c541893e2'))
    for row in upstream['files']:
        require(len(checked(package / row['name'], row['sha256'])) == row['bytes'], 'Upstream source size differs')
    records = json.loads(checked(package / 'layers.json.gz', LAYERS_SHA256))
    require(config['architecture'] == 'amd64' and config['os'] == 'linux', 'Wrong image platform')
    require(len(records) == len(manifest['layers']) == len(config['rootfs']['diff_ids']) == 8,
            'Incomplete image layer chain')
    inventories = []
    selected = []
    for index, (record, descriptor, diff_id) in enumerate(zip(records, manifest['layers'], config['rootfs']['diff_ids'])):
        require(record['index'] == index and record['blob_digest'] == descriptor['digest']
                and record['compressed_bytes'] == descriptor['size'] and record['diff_id'] == diff_id,
                'Layer chain binding differs')
        raw = gzip.decompress((package / f'inventory-{index:02d}.json.gz').read_bytes())
        require(sha(raw) == record['inventory_raw_sha256'], 'Saved inventory seal differs')
        inventory = json.loads(raw)
        require(len(inventory) == record['members'], 'Header count differs')
        inventories.append(inventory)
        if layers is not None:
            actual, retained = measure_layer(Path(layers) / (descriptor['digest'].split(':')[1] + '.tar.gz'), record)
            require(actual == inventory, 'Saved and measured inventories differ')
            for name, raw in retained.items():
                require((package / name).read_bytes() == raw, 'Retained member differs from authenticated layer')
        for member in record['selected']:
            header = {key: member[key] for key in ('name', 'type', 'size', 'mode', 'linkname')}
            require(header in inventory, 'Selected member missing from inventory')
            if 'saved' in member:
                require(member['saved'] == 'selected/' + member['sha256'], 'Unexpected retained member path')
                require(len(checked(package / member['saved'], member['sha256'])) == member['size'], 'Member size differs')
            selected.append(member)
    roots = check_cache_boundary(inventories)
    version = next(m for m in selected if m['name'].endswith('/solana-release/version.yml'))
    require(('channel: v1.16.25\ncommit: ' + SDK_COMMIT + '\n').encode() in
            (package / version['saved']).read_bytes(), 'SDK revision differs')
    installer = checked(package / 'upstream/install.sh', INSTALL_SHA256)
    require(installer == checked(package / ('selected/' + INSTALL_SHA256), INSTALL_SHA256),
            'Image and upstream SDK installers differ')
    source = checked(package / 'upstream/cargo-build-sbf-main.rs', SDK_SOURCE_SHA256).decode()
    for fragment in ('let platform_tools_version = String::from("v1.37");',
                     'fn install_if_missing(', '.join(".cache")', '.join("solana")',
                     'download_file(url.as_str(), &download_file_path, true, &mut None)?;',
                     'archive.unpack(target_path)', 'link_solana_toolchain(config);'):
        require(fragment in source, 'SDK installation source observation differs')
    historic = {name: checked(repo / 'repro/pump/metaplex-candidate-build-11' / name, digest)
                for name, digest in HISTORICAL.items()}
    inspection = json.loads(historic['image-inspect.json'])[0]
    require(inspection['Id'] == manifest['config']['digest'], 'Historical image config differs')
    require(inspection['RootFS']['Layers'] == config['rootfs']['diff_ids'], 'Historical rootfs differs')
    tools = json.loads(historic['tool-versions.json'])
    require(tools['selected_rustc_resolved'] == '/root/.cache/solana/v1.37/platform-tools/rust/bin/rustc',
            'Historical compiler path differs')
    script = historic['build-script.py'].decode()
    build_at = script.index('result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)')
    recorded_at = script.index("selected_resolved=read(['docker','exec',container,'readlink','-f',selected_rustc])")
    require(build_at < recorded_at, 'Historical tool observation is not after the build')
    return {'scope': 'Pinned clean-image contents and SDK installation source; no container, compiler or target execution.',
            'image': IMAGE, 'config': manifest['config']['digest'], 'layers': len(records),
            'compressed_layer_bytes': sum(r['compressed_bytes'] for r in records),
            'headers_observed': sum(len(rows) for rows in inventories),
            'root_directory_records': len(roots), 'root_cache_entries': 0,
            'sdk_release': '1.16.25', 'sdk_declared_commit': SDK_COMMIT,
            'image_installer_equals_upstream': True, 'source_default_platform_tools': 'v1.37',
            'historical_tool_path_observed_after_build': True,
            'full_layer_replay': layers is not None,
            'historical_loaded_library_identity_proven': False,
            'candidate_rebuilt': False, 'raw_target_byte_identity_improved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--repo', type=Path, default=REPO)
    parser.add_argument('--layers', type=Path, help='Optional directory of exact compressed registry blobs')
    args = parser.parse_args()
    print(json.dumps(verify(args.package, args.repo, args.layers), indent=2))


if __name__ == '__main__':
    main()
