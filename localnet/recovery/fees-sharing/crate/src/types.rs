use super::*;
#[derive(AnchorSerialize,AnchorDeserialize,Clone)]
pub struct BondingCurve {pub virtual_token_reserves:u64,pub virtual_quote_reserves:u64,pub real_token_reserves:u64,pub real_quote_reserves:u64,pub token_total_supply:u64,pub complete:bool,pub creator:Pubkey,pub is_mayhem_mode:bool}
impl Owner for BondingCurve {fn owner()->Pubkey {PUMP}}
impl Discriminator for BondingCurve {const DISCRIMINATOR:&'static [u8]=&[23,183,248,55,96,216,172,96];}
impl AccountSerialize for BondingCurve {}
impl AccountDeserialize for BondingCurve {
 fn try_deserialize(buf:&mut &[u8])->Result<Self>{
  if buf.len()<8{return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorNotFound));}
  if &buf[..8]!=Self::DISCRIMINATOR{return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorMismatch));}
  Self::try_deserialize_unchecked(buf)
 }
 fn try_deserialize_unchecked(buf:&mut &[u8])->Result<Self>{Self::deserialize(&mut &buf[8..]).map_err(|_|error!(anchor_lang::error::ErrorCode::AccountDidNotDeserialize))}
}
#[derive(AnchorSerialize,AnchorDeserialize,Clone)]
pub struct Pool {pub pool_bump:u8,pub index:u16,pub creator:Pubkey,pub base_mint:Pubkey,pub quote_mint:Pubkey,pub lp_mint:Pubkey,pub pool_base_token_account:Pubkey,pub pool_quote_token_account:Pubkey,pub lp_supply:u64,pub coin_creator:Pubkey,pub is_mayhem_mode:bool,pub is_cashback_coin:bool,pub virtual_quote_reserves:i128}
#[derive(AnchorSerialize,AnchorDeserialize,Clone,PartialEq)]
pub enum ConfigStatus {Paused,Active}
#[derive(AnchorSerialize,AnchorDeserialize,Clone)]
pub struct Shareholder {pub address:Pubkey,pub share_bps:u16}
#[account]
pub struct SharingConfig {pub bump:u8,pub version:u8,pub status:ConfigStatus,pub mint:Pubkey,pub admin:Pubkey,pub admin_revoked:bool,pub shareholders:Vec<Shareholder>}


impl Owner for Pool {fn owner()->Pubkey {AMM}}
impl Discriminator for Pool {const DISCRIMINATOR:&'static [u8]=&[241,154,109,4,17,177,109,188];}
impl AccountSerialize for Pool {}
impl AccountDeserialize for Pool {
 fn try_deserialize(buf:&mut &[u8])->Result<Self>{
  if buf.len()<8{return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorNotFound));}
  if &buf[..8]!=Self::DISCRIMINATOR{return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorMismatch));}
  Self::try_deserialize_unchecked(buf)
 }
 fn try_deserialize_unchecked(buf:&mut &[u8])->Result<Self>{Self::deserialize(&mut &buf[8..]).map_err(|_|error!(anchor_lang::error::ErrorCode::AccountDidNotDeserialize))}
}
