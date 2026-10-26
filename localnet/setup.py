#!/usr/bin/env python3
"""Install pinned local test tools. Downloads tools/docs only; never accesses chain RPC."""
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work/localnet'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable, help="Python interpreter for the test venv (3.12 recommended)")
    args = parser.parse_args()
    if (platform.system(), platform.machine()) != ('Darwin', 'arm64'):
        raise SystemExit('This installer pins the captured macOS ARM64 release. On other hosts supply Surfpool 1.6.1 explicitly to test_transactions.py --surfpool.')
    WORK.mkdir(parents=True, exist_ok=True)
    record = json.loads((ROOT/'research/imported-lab/evidence/tool-downloads.json').read_text())[0]
    archive = WORK/'surfpool.tar.gz'
    if not archive.exists():
        cached = ROOT/'work/surfpool-v1.6.1.tar.gz'
        if cached.exists(): shutil.copyfile(cached, archive)
        else:
            with urllib.request.urlopen(record['url'], timeout=120) as response, archive.open('wb') as target:
                shutil.copyfileobj(response, target)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == record['sha256'], 'Surfpool archive hash mismatch'
    with tarfile.open(archive) as tar:
        member = tar.getmember('surfpool')
        assert member.isfile()
        with tar.extractfile(member) as source, (WORK/'surfpool').open('wb') as target:
            shutil.copyfileobj(source, target)
    (WORK/'surfpool').chmod(0o755)
    assert subprocess.check_output([str(WORK/'surfpool'),'--version'],text=True).strip() == 'surfpool 1.6.1'
    environment = WORK/'venv'
    if not (environment/'bin/pip').exists(): subprocess.run([args.python,'-m','venv',str(environment)],check=True)
    subprocess.run([str(environment/'bin/python'),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
    docs = WORK/'pump-public-docs'
    commit = json.loads((ROOT/'research/imported-lab/analysis/pump_fun/program-manifest.json').read_text())['official_docs_commit']
    if not docs.exists():
        cached = ROOT/'work/pump-public-docs'
        source = str(cached) if cached.exists() else 'https://github.com/pump-fun/pump-public-docs.git'
        subprocess.run(['git','clone','--no-hardlinks',source,str(docs)],check=True)
    subprocess.run(['git','-C',str(docs),'cat-file','-e',commit+'^{commit}'],check=True)
    subprocess.run(['git','-C',str(docs),'checkout','--detach',commit],check=True)
    print('Ready: work/localnet/venv/bin/python localnet/test_transactions.py',flush=True)

if __name__ == '__main__': main()
