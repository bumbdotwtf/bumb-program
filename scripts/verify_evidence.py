#!/usr/bin/env python3
"""Verify saved evidence locally. This is NOT a rebuilt-source verification."""
import hashlib,json,pathlib,struct
from capture import b58
from analyze import elf_layout
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    count=0
    upstream=json.loads((ROOT/'evidence/upstream/provenance.json').read_text())
    for name,expected in upstream['file_sha256'].items():
        assert sha((ROOT/'evidence/upstream'/name).read_bytes())==expected
    for f in sorted((ROOT/'evidence').glob('**/capture.json')):
        m=json.loads(f.read_text()); folder=f.parent
        if m.get('loader')=='legacy-v2':
            p=(folder/'program-account.bin').read_bytes(); b=(folder/'deployed.so').read_bytes()
            assert p==b and sha(b)==m['payload_sha256']==m['program_sha256'] and len(b)==m['payload_bytes']
            assert m['owner']=='BPFLoader2111111111111111111111111111111111'
            assert m['genesis_hash']=='5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d'
            elf_layout(b); print(folder.relative_to(ROOT),'OK (legacy loader)'); count+=1; continue
        p=(folder/'program-account.bin').read_bytes(); d=(folder/'programdata-account.bin').read_bytes(); b=(folder/'deployed.so').read_bytes()
        assert sha(p)==m['program_sha256']; assert sha(d)==m['programdata_sha256']; assert sha(b)==m['payload_sha256']
        assert len(p)==36 and struct.unpack_from('<I',p)[0]==2
        assert b58(p[4:])==m['programdata']
        assert struct.unpack_from('<I',d)[0]==3
        assert struct.unpack_from('<Q',d,4)[0]==m['last_deploy_slot']
        assert (b58(d[13:45]) if d[12] else None)==m['upgrade_authority']
        assert d[45:]==b and len(b)==m['payload_bytes'] and len(d)==m['programdata_bytes']
        assert m['genesis_hash']=='5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d'
        assert m['context_slots']==sorted(m['context_slots']) and m['last_deploy_slot']<=min(m['context_slots'])
        layout=elf_layout(b); assert layout['trailing_all_zero']
        print(folder.relative_to(ROOT),'OK'); count+=1
    assert count>=4
    print(f'{count} captures verified; no source rebuild claimed.')
if __name__=='__main__': main()
