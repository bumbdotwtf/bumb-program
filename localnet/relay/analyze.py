#!/usr/bin/env python3
"""Extract source attribution and match on-chain IDL discriminators to captured SBF."""
import hashlib
import io
import json
import re
import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def main():
    blob=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
    capture=json.loads((ROOT/'evidence/dependencies/donation_relay/capture.json').read_text())
    assert hashlib.sha256(blob).hexdigest()==capture['payload_sha256']
    begin=b'=======BEGIN SECURITY.TXT V1======='
    end=b'=======END SECURITY.TXT V1======='
    at=blob.index(begin);stop=blob.index(end,at)+len(end)
    security=blob[at:stop]
    (OUT/'embedded-security.txt').write_text(security.replace(b'\0',b'\n').decode()+'\n')
    strings=security[len(begin):len(security)-len(end)].strip(b'\0').split(b'\0')
    fields={strings[i].decode():strings[i+1].decode() for i in range(0,len(strings),2)}
    elf=ELFFile(io.BytesIO(blob));section=elf.get_section_by_name('.text')
    start=section['sh_offset'];endtext=start+section['sh_size'];delta=section['sh_addr']-start
    idl=json.loads((OUT/'idl.json').read_text());assert idl['address']==capture['program']
    instructions={}
    for ix in idl['instructions']:
        disc=bytes(ix['discriminator']);hits=[];pc=start
        while pc<endtext:
            op,regs,off,imm=struct.unpack_from('<BBhi',blob,pc)
            if op==0x18:
                if blob[pc+4:pc+8]+blob[pc+12:pc+16]==disc:
                    j=pc+16
                    while j<pc+48 and blob[j] in (0xbf,0x79) and (blob[j+1]&15)!=(regs&15): j+=8
                    jop,jregs,joff,_=struct.unpack_from('<BBhi',blob,j)
                    if jop in (0x1d,0x5d) and ((jregs>>4)==(regs&15) or (jregs&15)==(regs&15)):
                        target=j+8+joff*8 if jop==0x1d else j+8
                        hits.append({'constant_address':pc+delta,'comparison_address':j+delta,'matched_branch_address':target+delta})
                pc+=16
            else: pc+=8
        instructions[ix['name']]={'discriminator':disc.hex(),'matches':hits}
    paths=sorted(set(x.decode() for x in re.findall(rb'programs/contracts/[A-Za-z0-9_/]+\.rs',blob)))
    report={'program':capture['program'],'binary_sha256':capture['payload_sha256'],'idl_version':idl['metadata']['version'],
        'idl_file_sha256':hashlib.sha256((OUT/'idl.json').read_bytes()).hexdigest(),
        'embedded_security_fields':fields,'security_byte_offset':at,'security_byte_length':stop-at,
        'rust_source_paths':paths,'compiler_version':None,'compiler_reason':'No .comment section or exact Rust compiler version string found; platform-tools source paths alone do not identify a version.',
        'instructions':instructions,'matched_discriminators':sum(bool(x['matches']) for x in instructions.values()),
        'source_available':False,'source_check':'Embedded repository URL returned GitHub HTTP404 in both API and browser checks. No source commit pinned by metadata.',
        'scope':'Embedded publisher attribution and IDL/dispatcher correspondence only; metadata is not independent audit verification or byte-identical source evidence.'}
    (OUT/'attribution.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Matched',report['matched_discriminators'],'/',len(instructions),'IDL selectors; source paths',len(paths))
if __name__=='__main__':main()
