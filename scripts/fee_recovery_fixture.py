"""Synthetic local Pump Fees query fixtures. No RPC, signatures stay in LiteSVM."""
import json,pathlib,struct
from solders.litesvm import LiteSVM
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.account import Account
from solders.instruction import Instruction,AccountMeta
from solders.transaction import Transaction
from solders.transaction_metadata import FailedTransactionMetadata
ROOT=pathlib.Path(__file__).resolve().parents[1]
class FeeFixture:
 def __init__(self,binary=None):
  self.idl=json.loads((ROOT/'evidence/upstream/pump_fees.json').read_text());self.program=Pubkey.from_string(self.idl['address'])
  self.config_program=Pubkey.from_string('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P')
  self.key,self.bump=Pubkey.find_program_address([b'fee_config',bytes(self.config_program)],self.program)
  self.discriminator=bytes(next(a for a in self.idl['accounts'] if a['name']=='FeeConfig')['discriminator'])
  self.vm=LiteSVM().with_transaction_history(0);self.payer=Keypair.from_seed(bytes(32));self.vm.airdrop(self.payer.pubkey(),10**10)
  self.vm.add_program_from_file(self.program,binary or ROOT/'evidence/original/pump_fees/deployed.so');self.vm.set_account(self.config_program,Account(10**9,b'',Pubkey.default()))
 def config(self,normal,stable,flat,exotic,allocation=4097):
  def fees(f):return struct.pack('<QQQ',*f)
  def tiers(xs):return struct.pack('<I',len(xs))+b''.join(t.to_bytes(16,'little')+fees(f) for t,f in xs)
  data=self.discriminator+bytes([self.bump])+bytes(32)+fees(flat)+tiers(normal)+tiers(stable)+fees(exotic)
  self.vm.set_account(self.key,Account(10**9,data.ljust(allocation,b'\0')[:allocation],self.program))
 def query(self,pool,cap,quote):
  ix=next(i for i in self.idl['instructions'] if i['name']=='get_fees_with_quote_mint')
  payload=bytes(ix['discriminator'])+bytes([pool])+cap.to_bytes(16,'little')+quote
  tx=Transaction.new_signed_with_payer([Instruction(self.program,payload,[AccountMeta(self.key,False,False),AccountMeta(self.config_program,False,False)])],self.payer.pubkey(),[self.payer],self.vm.latest_blockhash())
  r=self.vm.send_transaction(tx)
  if isinstance(r,FailedTransactionMetadata):return {'error':str(r.err()),'logs':r.meta().logs()}
  return {'fees':list(struct.unpack('<QQQ',r.return_data().data))}
