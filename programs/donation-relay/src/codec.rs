//! Normal-allocation wire values. Rich error allocation/cleanup equivalence is open.
use crate::*;
pub mod constants;
struct Reader<'a>{rest:&'a [u8],code:u32}
impl<'a> Reader<'a> {
 fn take(&mut self,n:usize)->R<&'a [u8]> {if self.rest.len()<n{return Err(Error::Code(self.code));}let (a,b)=self.rest.split_at(n);self.rest=b;Ok(a)}
 fn key(&mut self)->R<Key>{Ok(self.take(32)?.try_into().unwrap())}
 fn u8(&mut self)->R<u8>{Ok(self.take(1)?[0])}
 fn u16(&mut self)->R<u16>{Ok(u16::from_le_bytes(self.take(2)?.try_into().unwrap()))}
 fn u32(&mut self)->R<u32>{Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()))}
 fn u64(&mut self)->R<u64>{Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))}
 fn u128(&mut self)->R<u128>{Ok(u128::from_le_bytes(self.take(16)?.try_into().unwrap()))}
 fn bytes(&mut self)->R<Vec<u8>>{let n=self.u32()? as usize;Ok(self.take(n)?.to_vec())}
 fn shares(&mut self)->R<Vec<Share>> {
  let n=self.u32()? as usize;let mut v=Vec::with_capacity(n.min(113));
  for _ in 0..n {let kind=match self.u8()? {0=>ShareKind::Beneficiary,1=>ShareKind::Fee,2=>ShareKind::Tip,_=>return Err(Error::Code(self.code))};
   let authority=self.key()?;let bps=self.u16()?;v.push(Share{kind,authority,bps});}Ok(v)
 }
 fn keys(&mut self)->R<Vec<Key>> {let n=self.u32()? as usize;let mut v=Vec::with_capacity(n.min(128));for _ in 0..n{v.push(self.key()?);}Ok(v)}
 fn donation(&mut self)->R<DonationArgs>{let amount=self.u64()?;let config_id=self.key()?;let tip_bps=self.u16()?;let message=String::from_utf8(self.bytes()?).map_err(|_|Error::Code(self.code))?;let credited_to=self.key()?;Ok(DonationArgs{amount,config_id,tip_bps,message,credited_to})}
}
pub enum Instruction {
 Donation(DonationVariant,DonationArgs),Close(Key,u128),After(Vec<Share>),NonSwap(Vec<Share>),JustSwap(Vec<u8>),Combined(Vec<u8>,Vec<Share>),Whitelist(Vec<Key>)
}
// Takes a known IDL instruction name and its bytes AFTER the eight-byte selector.
// Entrypoint selector/fallback/event-recursion dispatch is intentionally separate.
pub fn decode_arguments(name:&str,bytes:&[u8])->R<Instruction> {
 let mut r=Reader{rest:bytes,code:102};
 let v=match name {
 "donate_v1"=>Instruction::Donation(DonationVariant::TokenBytes,r.donation()?),
 "donate_pubkey_config_id_v1"=>Instruction::Donation(DonationVariant::TokenPubkey,r.donation()?),
 "donate_pubkey_config_id_with_payer_v1"=>Instruction::Donation(DonationVariant::TokenPubkeyWithPayer,r.donation()?),
 "donate_native_v1"=>Instruction::Donation(DonationVariant::NativeBytes,r.donation()?),
 "donate_native_pubkey_config_id_v1"=>Instruction::Donation(DonationVariant::NativePubkey,r.donation()?),
 "close_donation_epoch_v1"=>Instruction::Close(r.key()?,r.u128()?),
 "distribute_after_just_swapping_v1"=>Instruction::After(r.shares()?),
 "distribute_non_swap_output_mint_v1"=>Instruction::NonSwap(r.shares()?),
 "just_swap_v1"=>Instruction::JustSwap(r.bytes()?),
 "swap_then_distribute_v1"=>Instruction::Combined(r.bytes()?,r.shares()?),
 "upsert_mint_whitelist_v1"=>Instruction::Whitelist(r.keys()?),
 _=>return Err(Error::Incomplete("entrypoint fallback dispatch")),
 };Ok(v) // Suffix accepted. No max113 shares / max1MiB opaque data policy.
}
fn header<'a>(b:&'a [u8],disc:[u8;8],checked:bool)->R<Reader<'a>> {
 if checked {require(b.len()>=8,3001)?;require(b[..8]==disc,3002)?;} else {assert!(b.len()>=8,"unchecked state discriminator slice");}Ok(Reader{rest:&b[8..],code:3003})
}
fn common(r:&mut Reader)->R<(u8,State,Key,Key)> {
 let bump=r.u8()?;let state=match r.u8()?{0=>State::Uninitialized,1=>State::Initialized,_=>return Err(Error::Code(3003))};
 Ok((bump,state,r.key()?,r.key()?))
}
pub fn tracker_mode(b:&[u8],checked:bool)->R<Tracker>{let mut r=header(b,constants::TRACKER_DISC,checked)?;let(bump,state,config_id,mint)=common(&mut r)?;Ok(Tracker{bump,state,config_id,mint,current_epoch:r.u128()?})}
pub fn debouncer_mode(b:&[u8],checked:bool)->R<Debouncer>{let mut r=header(b,constants::DEBOUNCER_DISC,checked)?;let(bump,state,config_id,mint)=common(&mut r)?;Ok(Debouncer{bump,state,config_id,mint,total_amount:r.u64()?})}
pub fn distribution_mode(b:&[u8],checked:bool)->R<Distribution>{let mut r=header(b,constants::DISTRIBUTION_DISC,checked)?;let(bump,state,config_id,mint)=common(&mut r)?;Ok(Distribution{bump,state,config_id,mint,epoch:r.u128()?,total_amount:r.u64()?})}
pub fn swap_receipt_mode(b:&[u8],checked:bool)->R<SwapReceipt>{let mut r=header(b,constants::RECEIPT_DISC,checked)?;Ok(SwapReceipt{bump:r.u8()?,distribution:r.key()?,output_amount:r.u64()?})}
pub fn whitelist_mode(b:&[u8],checked:bool)->R<Whitelist>{let mut r=header(b,constants::WHITELIST_DISC,checked)?;Ok(Whitelist{bump:r.u8()?,mints:r.keys()?})}
fn prefix(v:&mut Vec<u8>,bump:u8,state:State,config:Key,mint:Key){v.push(bump);v.push(match state{State::Uninitialized=>0,State::Initialized=>1});v.extend(config);v.extend(mint);}
pub fn tracker_bytes(t:&Tracker)->Vec<u8>{let mut v=constants::TRACKER_DISC.to_vec();prefix(&mut v,t.bump,t.state,t.config_id,t.mint);v.extend(t.current_epoch.to_le_bytes());v}
pub fn debouncer_bytes(t:&Debouncer)->Vec<u8>{let mut v=constants::DEBOUNCER_DISC.to_vec();prefix(&mut v,t.bump,t.state,t.config_id,t.mint);v.extend(t.total_amount.to_le_bytes());v}
pub fn distribution_bytes(t:&Distribution)->Vec<u8>{let mut v=constants::DISTRIBUTION_DISC.to_vec();prefix(&mut v,t.bump,t.state,t.config_id,t.mint);v.extend(t.epoch.to_le_bytes());v.extend(t.total_amount.to_le_bytes());v}
pub fn receipt_bytes(t:&SwapReceipt)->Vec<u8>{let mut v=constants::RECEIPT_DISC.to_vec();v.push(t.bump);v.extend(t.distribution);v.extend(t.output_amount.to_le_bytes());v}
pub fn whitelist_bytes(t:&Whitelist)->R<Vec<u8>>{let mut v=constants::WHITELIST_DISC.to_vec();v.push(t.bump);let n=u32::try_from(t.mints.len()).map_err(|_|Error::Code(3004))?;v.extend(n.to_le_bytes());for k in &t.mints{v.extend(k);}Ok(v)}
// Prefix writes preserve unconsumed old allocation bytes. Partial write on short data.
pub fn write_prefix(out:&mut [u8],bytes:&[u8])->R<()> {let n=out.len().min(bytes.len());out[..n].copy_from_slice(&bytes[..n]);require(n==bytes.len(),3004)}
fn event_head(tag:u8,config:&Key,mint:&Key,epoch:u128)->Vec<u8>{let mut v=vec![tag];v.extend(config);v.extend(mint);v.extend(epoch.to_le_bytes());v}
pub fn event_bytes(e:&Event)->R<([u8;8],Vec<u8>)> {
 use Event::*;
 Ok(match e {
 Made{config_id,mint,epoch,gross,tip,message,credited_to}=>{let mut v=event_head(0,config_id,mint,*epoch);v.extend(gross.to_le_bytes());v.extend(tip.to_le_bytes());let n=u32::try_from(message.len()).map_err(|_|Error::Code(3004))?;v.extend(n.to_le_bytes());v.extend(message.as_bytes());v.extend(credited_to);(constants::MADE_EVENT,v)},
 Closed{config_id,mint,epoch,gross}=>{let mut v=event_head(1,config_id,mint,*epoch);v.extend(gross.to_le_bytes());(constants::CLOSED_EVENT,v)},
 Processed{config_id,mint,epoch,amount,settlement,receipts}=>{let mut v=event_head(2,config_id,mint,*epoch);v.extend(amount.to_le_bytes());v.extend(settlement);let n=u32::try_from(receipts.len()).map_err(|_|Error::Code(3004))?;v.extend(n.to_le_bytes());for r in receipts{v.push(match r.share.kind{ShareKind::Beneficiary=>0,ShareKind::Fee=>1,ShareKind::Tip=>2});v.extend(r.share.authority);v.extend(r.amount.to_le_bytes());v.extend(r.share.bps.to_le_bytes());}(constants::PROCESSED_EVENT,v)},
 Swapped{config_id,mint,epoch,distribution,receipt,output_vault,amount,settlement}=>{let mut v=event_head(3,config_id,mint,*epoch);v.extend(distribution);v.extend(receipt);v.extend(output_vault);v.extend(amount.to_le_bytes());v.extend(settlement);(constants::SWAPPED_EVENT,v)},
 })
}

pub fn tracker(b:&[u8])->R<Tracker> {tracker_mode(b,true)}

pub fn debouncer(b:&[u8])->R<Debouncer> {debouncer_mode(b,true)}

pub fn distribution(b:&[u8])->R<Distribution> {distribution_mode(b,true)}

pub fn swap_receipt(b:&[u8])->R<SwapReceipt> {swap_receipt_mode(b,true)}

pub fn whitelist(b:&[u8])->R<Whitelist> {whitelist_mode(b,true)}
