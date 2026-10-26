use anchor_lang::prelude::*;
use anchor_lang::Discriminator;
use anchor_lang::solana_program::{instruction::{Instruction,AccountMeta},program::invoke};
mod errors;use errors::*;
mod pump_global;
mod types;use types::*;
declare_id!("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ");
pub const PUMP:Pubkey=pump_global::PUMP_ID;
pub const AMM:Pubkey=anchor_lang::solana_program::pubkey!("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA");
#[derive(Clone)]pub struct Pump;impl Id for Pump{fn id()->Pubkey{PUMP}}
#[derive(Clone)]pub struct Amm;impl Id for Amm{fn id()->Pubkey{AMM}}
#[program]
pub mod pump_fees_candidate {
 use super::*;
 pub fn update_fee_shares<'info>(ctx:Context<'_, '_, '_, 'info,UpdateFeeShares<'info>>,shareholders:Vec<Shareholder>)->Result<()> {
  require!(ctx.accounts.sharing_config.version!=1,FeeError::FeeSharesAlreadyUpdated);
  authorize(&ctx.accounts.sharing_config,ctx.accounts.authority.key())?;
  let quote=ctx.accounts.wsol_mint.key();
  let native=quote==anchor_spl::token::spl_token::native_mint::ID;
  validate_remaining(&ctx.accounts.sharing_config,ctx.remaining_accounts,1)?;
  if ctx.accounts.bonding_curve.real_token_reserves==0 && ctx.accounts.coin_creator_vault_ata.owner != &System::id() && ctx.accounts.coin_creator_vault_ata.lamports()!=0 {
   call(AMM,vec![ctx.accounts.wsol_mint.to_account_info(),ctx.accounts.token_program.to_account_info(),ctx.accounts.system_program.to_account_info(),ctx.accounts.associated_token_program.to_account_info(),ctx.accounts.sharing_config.to_account_info(),ctx.accounts.coin_creator_vault_authority.to_account_info(),ctx.accounts.coin_creator_vault_ata.to_account_info(),ctx.accounts.pump_creator_vault.to_account_info(),ctx.accounts.amm_event_authority.to_account_info(),ctx.accounts.pump_amm_program.to_account_info()],&[(false,false),(false,false),(false,false),(false,false),(false,false),(true,false),(true,false),(true,false),(false,false),(false,false)],vec![139,52,134,85,228,229,108,241],&[])?;
  }
  call(PUMP,vec![ctx.accounts.mint.to_account_info(),ctx.accounts.bonding_curve.to_account_info(),ctx.accounts.sharing_config.to_account_info(),ctx.accounts.pump_creator_vault.to_account_info(),ctx.accounts.system_program.to_account_info(),ctx.accounts.pump_event_authority.to_account_info(),ctx.accounts.pump_program.to_account_info()],&[(false,false),(false,false),(false,false),(true,false),(false,false),(false,false),(false,false)],vec![165,114,103,0,121,206,247,81],ctx.remaining_accounts)?;
  validate_shares(&shareholders)?;
  let state=&mut ctx.accounts.sharing_config;state.shareholders=shareholders.clone();state.admin_revoked=true;
  let event=UpdateFeeSharesEvent{timestamp:Clock::get()?.unix_timestamp,mint:ctx.accounts.mint.key(),sharing_config:state.key(),admin:state.admin,new_shareholders:shareholders,version:state.version};emit!(event);emit_cpi!(event);Ok(())
 }
 pub fn update_fee_shares_v2<'info>(ctx:Context<'_, '_, '_, 'info,UpdateFeeSharesV2<'info>>,shareholders:Vec<Shareholder>)->Result<()> {
  require!(ctx.accounts.sharing_config.version!=1,FeeError::FeeSharesAlreadyUpdated);
  authorize(&ctx.accounts.sharing_config,ctx.accounts.authority.key())?;
  let quote=ctx.accounts.quote_mint.key();
  let native=quote==anchor_spl::token::spl_token::native_mint::ID;
  let curve_info=ctx.accounts.bonding_curve.to_account_info();let data=curve_info.try_borrow_data()?;
  let stored=if data.len()>=115{Pubkey::new_from_array(data[83..115].try_into().unwrap())}else{Pubkey::default()};drop(data);
  let expected=if stored==Pubkey::default(){anchor_spl::token::spl_token::native_mint::ID}else{stored};require_keys_eq!(quote,expected,FeeError::InvalidQuoteMint);
  validate_remaining(&ctx.accounts.sharing_config,ctx.remaining_accounts,if native{1}else{2})?;
  if ctx.accounts.bonding_curve.real_token_reserves==0 && ctx.accounts.coin_creator_vault_ata.owner != &System::id() && ctx.accounts.coin_creator_vault_ata.lamports()!=0 {
   call(AMM,vec![ctx.accounts.authority.to_account_info(),ctx.accounts.quote_mint.to_account_info(),ctx.accounts.token_program.to_account_info(),ctx.accounts.system_program.to_account_info(),ctx.accounts.associated_token_program.to_account_info(),ctx.accounts.sharing_config.to_account_info(),ctx.accounts.coin_creator_vault_authority.to_account_info(),ctx.accounts.coin_creator_vault_ata.to_account_info(),ctx.accounts.pump_creator_vault.to_account_info(),ctx.accounts.pump_creator_vault_ata.to_account_info(),ctx.accounts.amm_event_authority.to_account_info(),ctx.accounts.pump_amm_program.to_account_info()],&[(true,true),(false,false),(false,false),(false,false),(false,false),(false,false),(true,false),(true,false),(true,false),(true,false),(false,false),(false,false)],vec![1,33,78,185,33,67,44,92],&[])?;
  }
  call(PUMP,vec![ctx.accounts.authority.to_account_info(),ctx.accounts.mint.to_account_info(),ctx.accounts.bonding_curve.to_account_info(),ctx.accounts.sharing_config.to_account_info(),ctx.accounts.pump_creator_vault.to_account_info(),ctx.accounts.system_program.to_account_info(),ctx.accounts.pump_event_authority.to_account_info(),ctx.accounts.pump_program.to_account_info(),ctx.accounts.pump_creator_vault_ata.to_account_info(),ctx.accounts.quote_mint.to_account_info(),ctx.accounts.token_program.to_account_info(),ctx.accounts.associated_token_program.to_account_info()],&[(true,true),(false,false),(false,false),(false,false),(true,false),(false,false),(false,false),(false,false),(true,false),(false,false),(false,false),(false,false)],vec![255,203,19,79,244,68,8,159,1],ctx.remaining_accounts)?;
  validate_shares(&shareholders)?;
  let state=&mut ctx.accounts.sharing_config;state.shareholders=shareholders.clone();state.admin_revoked=true;
  let event=UpdateFeeSharesEvent{timestamp:Clock::get()?.unix_timestamp,mint:ctx.accounts.mint.key(),sharing_config:state.key(),admin:state.admin,new_shareholders:shareholders,version:state.version};emit!(event);emit_cpi!(event);Ok(())
 }
}
fn authorize(state:&SharingConfig,authority:Pubkey)->Result<()>{
 require_keys_eq!(state.admin,authority,FeeError::NotAuthorized);
 require!(!state.admin_revoked,FeeError::SharingConfigAdminRevoked);
 require!(state.status==ConfigStatus::Active,FeeError::SharingConfigNotActive);Ok(())
}
fn validate_remaining(state:&SharingConfig,remaining:&[AccountInfo],stride:usize)->Result<()>{
 require!(remaining.len()>=state.shareholders.len()*stride,FeeError::NotEnoughRemainingAccounts);
 for (i,share) in state.shareholders.iter().enumerate(){require_keys_eq!(remaining[i].key(),share.address,FeeError::ShareholderAccountMismatch);}Ok(())
}
fn validate_shares(shares:&[Shareholder])->Result<()>{
 require!(!shares.is_empty(),FeeError::NoShareholders);require!(shares.len()<=10,FeeError::TooManyShareholders);
 let mut sum=0u16;let mut seen=Vec::new();
 for share in shares {require!(share.share_bps>0,FeeError::ZeroShareNotAllowed);sum=sum.checked_add(share.share_bps).ok_or(error!(FeeError::ShareCalculationOverflow))?;require!(!seen.contains(&share.address),FeeError::DuplicateShareholder);seen.push(share.address);}
 require!(sum==10000,FeeError::InvalidShareTotal);Ok(())
}
fn call<'info>(program_id:Pubkey,mut infos:Vec<AccountInfo<'info>>,flags:&[(bool,bool)],data:Vec<u8>,remaining:&[AccountInfo<'info>])->Result<()>{
 let mut accounts:Vec<AccountMeta>=infos.iter().zip(flags).map(|(a,(w,s))|if *w{AccountMeta::new(a.key(),*s)}else{AccountMeta::new_readonly(a.key(),*s)}).collect();
 accounts.extend(remaining.iter().map(|a|if a.is_writable{AccountMeta::new(a.key(),a.is_signer)}else{AccountMeta::new_readonly(a.key(),a.is_signer)}));infos.extend_from_slice(remaining);invoke(&Instruction{program_id,accounts,data},&infos)?;Ok(())
}
#[event]
pub struct UpdateFeeSharesEvent{pub timestamp:i64,pub mint:Pubkey,pub sharing_config:Pubkey,pub admin:Pubkey,pub new_shareholders:Vec<Shareholder>,pub version:u8}
#[derive(Accounts)]
pub struct UpdateFeeShares<'info>{
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 pub program:Program<'info,crate::program::PumpFeesCandidate>,
 pub authority:Signer<'info>,
 #[account(seeds=[b"global"],bump,seeds::program=PUMP)]pub global:Box<Account<'info,pump_global::Global>>,
 pub mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
 #[account(mut,seeds=[b"sharing-config",mint.key().as_ref()],bump=sharing_config.bump,has_one=mint @ FeeError::InvalidSharingConfig)]pub sharing_config:Account<'info,SharingConfig>,
 #[account(seeds=[b"bonding-curve",mint.key().as_ref()],bump,seeds::program=PUMP)]pub bonding_curve:Account<'info,BondingCurve>,
 /// CHECK: creator vault PDA.
 #[account(mut,seeds=[b"creator-vault",sharing_config.key().as_ref()],bump,seeds::program=PUMP)]pub pump_creator_vault:UncheckedAccount<'info>,
 pub system_program:Program<'info,System>,
 pub pump_program:Program<'info,Pump>,
 /// CHECK: Pump event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=PUMP)]pub pump_event_authority:UncheckedAccount<'info>,
 pub pump_amm_program:Program<'info,Amm>,
 /// CHECK: AMM event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=AMM)]pub amm_event_authority:UncheckedAccount<'info>,
 #[account(address=anchor_spl::token::spl_token::native_mint::ID)]pub wsol_mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
 #[account(address=anchor_spl::token::ID)]pub token_program:Interface<'info,anchor_spl::token_interface::TokenInterface>,
 pub associated_token_program:Program<'info,anchor_spl::associated_token::AssociatedToken>,
 /// CHECK: AMM creator vault PDA.
 #[account(mut,seeds=[b"creator_vault",sharing_config.key().as_ref()],bump,seeds::program=AMM)]pub coin_creator_vault_authority:UncheckedAccount<'info>,
 /// CHECK: canonical token account address; dependency validates data.
 #[account(mut,address=anchor_spl::associated_token::get_associated_token_address_with_program_id(&coin_creator_vault_authority.key(),&wsol_mint.key(),&token_program.key()))]pub coin_creator_vault_ata:UncheckedAccount<'info>,
}
#[derive(Accounts)]
pub struct UpdateFeeSharesV2<'info>{
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 pub program:Program<'info,crate::program::PumpFeesCandidate>,
 #[account(mut)]pub authority:Signer<'info>,
 #[account(seeds=[b"global"],bump,seeds::program=PUMP)]pub global:Box<Account<'info,pump_global::Global>>,
 pub mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
 #[account(mut,seeds=[b"sharing-config",mint.key().as_ref()],bump=sharing_config.bump,has_one=mint @ FeeError::InvalidSharingConfig)]pub sharing_config:Account<'info,SharingConfig>,
 #[account(seeds=[b"bonding-curve",mint.key().as_ref()],bump,seeds::program=PUMP)]pub bonding_curve:Account<'info,BondingCurve>,
 /// CHECK: creator vault PDA.
 #[account(mut,seeds=[b"creator-vault",sharing_config.key().as_ref()],bump,seeds::program=PUMP)]pub pump_creator_vault:UncheckedAccount<'info>,
 /// CHECK: canonical token address, validated by dependency.
 #[account(mut,seeds=[pump_creator_vault.key().as_ref(),token_program.key().as_ref(),quote_mint.key().as_ref()],bump,seeds::program=associated_token_program.key())]pub pump_creator_vault_ata:UncheckedAccount<'info>,
 pub system_program:Program<'info,System>,
 pub pump_program:Program<'info,Pump>,
 /// CHECK: Pump event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=PUMP)]pub pump_event_authority:UncheckedAccount<'info>,
 pub pump_amm_program:Program<'info,Amm>,
 /// CHECK: AMM event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=AMM)]pub amm_event_authority:UncheckedAccount<'info>,
pub quote_mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
pub token_program:Interface<'info,anchor_spl::token_interface::TokenInterface>,
 pub associated_token_program:Program<'info,anchor_spl::associated_token::AssociatedToken>,
 /// CHECK: AMM creator vault PDA.
 #[account(mut,seeds=[b"creator_vault",sharing_config.key().as_ref()],bump,seeds::program=AMM)]pub coin_creator_vault_authority:UncheckedAccount<'info>,
 /// CHECK: canonical token account address; dependency validates data.
 #[account(mut,seeds=[coin_creator_vault_authority.key().as_ref(),token_program.key().as_ref(),quote_mint.key().as_ref()],bump,seeds::program=associated_token_program.key())]pub coin_creator_vault_ata:UncheckedAccount<'info>,
}
