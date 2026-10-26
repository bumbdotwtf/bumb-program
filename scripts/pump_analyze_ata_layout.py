#!/usr/bin/env python3
"""Read-only instruction correspondence analysis; never emits a transformed ELF."""
import hashlib,json,pathlib,struct
R=pathlib.Path(__file__).resolve().parents[1]
a=(R/'evidence/dependencies/associated_token/deployed.so').read_bytes();b=(R/'repro/pump/ata-candidate-build-2/spl_associated_token_account.so').read_bytes()
def correspondence(pc):
 if 3574<=pc<3629:return pc+44
 if 3629<=pc<3673:return pc-55
 return pc
mismatches=[];relocated_calls=[]
for pc in range(36,(288+92056)//8):
 mapped=correspondence(pc);x=a[pc*8:pc*8+8];y=b[mapped*8:mapped*8+8]
 if x[0:2]==bytes([0x85,0x10]) and struct.unpack_from('<i',x,4)[0]!=-1:
  target=pc+1+struct.unpack_from('<i',x,4)[0];actual=mapped+1+struct.unpack_from('<i',y,4)[0]
  same=x[:4]==y[:4] and correspondence(target)==actual
  if same and x!=y:relocated_calls.append({'original_pc':pc,'candidate_pc':mapped,'original_target':target,'candidate_target':actual})
 else:same=x==y
 if not same:mismatches.append({'original_pc':pc,'candidate_pc':mapped,'original_hex':x.hex(),'candidate_hex':y.hex()})
report={'scope':'Read-only correspondence proof. No bytes written to candidate and no claim of byte equality.','original_sha256':hashlib.sha256(a).hexdigest(),'candidate_sha256':hashlib.sha256(b).hexdigest(),'full_byte_equality':a==b,'differing_byte_positions':sum(x!=y for x,y in zip(a,b)),'text_offset':288,'text_bytes':92056,'function_correspondence':[{'original_start_pc':3574,'candidate_start_pc':3618,'instruction_count':55},{'original_start_pc':3629,'candidate_start_pc':3574,'instruction_count':44}],'non_text_byte_equality':a[:288]==b[:288] and a[92344:]==b[92344:],'instruction_mismatches_after_address_correspondence':mismatches,'relocated_calls':relocated_calls}
from elftools.elf.elffile import ELFFile
with (R/'evidence/dependencies/associated_token/deployed.so').open('rb') as stream:
 elf=ELFFile(stream);rel=elf.get_section_by_name('.rel.dyn');off=rel['sh_offset'];size=rel['sh_size']
 original_relocations=[struct.unpack_from('<QQ',a,i) for i in range(off,off+size,16)]
 candidate_relocations=[struct.unpack_from('<QQ',b,i) for i in range(off,off+size,16)]
 mapped_relocations=[(correspondence(address//8)*8+address%8,kind) for address,kind in original_relocations]
 report['relocation_table_offset']=off;report['relocation_table_bytes']=size
 report['relocation_multiset_equality_after_address_correspondence']=sorted(mapped_relocations)==sorted(candidate_relocations)
 report['all_other_non_text_bytes_identical']=a[:288]==b[:288] and a[92344:off]==b[92344:off] and a[off+size:]==b[off+size:]
print(json.dumps(report,indent=2))
