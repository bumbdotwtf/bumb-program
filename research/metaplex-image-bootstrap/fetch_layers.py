"""Download the eight pinned public registry blobs to a fresh directory; never extract them."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

from verify import IMAGE, PACKAGE, checked

REPOSITORY = 'solanafoundation/solana-verifiable-build'


def download(directory, descriptor, headers):
    digest = descriptor['digest']
    name = digest.split(':')[1] + '.tar.gz'
    url = 'https://registry-1.docker.io/v2/' + REPOSITORY + '/blobs/' + digest
    partial = directory / (name + '.partial')
    measured, count = hashlib.sha256(), 0
    record = {'url': url, 'digest': digest, 'expected_bytes': descriptor['size'], 'saved': name}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as response, partial.open('xb') as out:
            record['status'] = response.status
            while raw := response.read(1024 * 1024):
                measured.update(raw)
                count += len(raw)
                out.write(raw)
        if count != descriptor['size'] or 'sha256:' + measured.hexdigest() != digest:
            raise ValueError('Downloaded layer identity differs')
        partial.rename(directory / name)
        record['verified'] = True
    except Exception as error:
        record.update(verified=False, error_type=type(error).__name__, error=str(error))
    record.update(observed_at=datetime.now(timezone.utc).isoformat(), bytes=count, sha256=measured.hexdigest())
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    directory = args.output.resolve()
    if directory.exists():
        parser.error('Output already exists; use a fresh directory to preserve observations')
    manifest = json.loads(checked(PACKAGE / 'manifest.json', IMAGE.split(':')[1]))
    directory.mkdir(parents=True)
    records = []
    error = None
    try:
        url = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:' + REPOSITORY + ':pull'
        with urllib.request.urlopen(url, timeout=60) as response:
            token = json.load(response)['token']
        headers = {'Authorization': 'Bearer ' + token}
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(download, directory, layer, headers) for layer in manifest['layers']]
            for future in as_completed(futures):
                row = future.result()
                records.append(row)
                print(json.dumps({key: row[key] for key in ('digest', 'bytes', 'verified')}), flush=True)
        if not all(row['verified'] for row in records):
            raise ValueError('One or more downloads failed; partial bytes and receipts are preserved')
    except Exception as exception:
        error = {'type': type(exception).__name__, 'message': str(exception)}
        raise
    finally:
        # Never retain the anonymous registry bearer token or signed redirect URLs.
        (directory / 'download-receipts.json').write_text(json.dumps({
            'image': IMAGE, 'files': records, 'error': error}, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
