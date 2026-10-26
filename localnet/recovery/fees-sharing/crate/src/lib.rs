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
 pub fn create_fee_sharing_config(ctx:Context<CreateFeeSharingConfig>)->Result<()> {
  if ctx.accounts.sharing_config.version!=0{return Ok(());}
  let graduated=ctx.accounts.bonding_curve.real_token_reserves==0;
  let creator=if graduated {
   let pool=ctx.accounts.pool.as_ref().ok_or(error!(FeeError::AmmAccountsRequiredForGraduatedCoin))?;
   require!(ctx.accounts.pump_amm_program.is_some() && ctx.accounts.pump_amm_event_authority.is_some(),FeeError::AmmAccountsRequiredForGraduatedCoin);
   let state=pool;
   require_keys_eq!(state.base_mint,ctx.accounts.mint.key(),FeeError::InvalidPool);
   let authority=Pubkey::find_program_address(&[b"pool-authority",ctx.accounts.mint.key().as_ref()],&PUMP).0;
   require_keys_eq!(state.creator,authority,FeeError::InvalidPool);
   let expected=Pubkey::create_program_address(&[b"pool",&state.index.to_le_bytes(),state.creator.as_ref(),state.base_mint.as_ref(),state.quote_mint.as_ref(),&[state.pool_bump]],&AMM).map_err(|_|error!(FeeError::InvalidPool))?;
   require_keys_eq!(expected,pool.key(),FeeError::InvalidPool);state.coin_creator
  }else{ctx.accounts.bonding_curve.creator};
  require_keys_eq!(creator,ctx.accounts.payer.key(),FeeError::NotAuthorized);
  let state=&mut ctx.accounts.sharing_config;state.bump=ctx.bumps.sharing_config;state.version=2;state.status=ConfigStatus::Active;state.mint=ctx.accounts.mint.key();state.admin=ctx.accounts.bonding_curve.creator;state.admin_revoked=false;state.shareholders=vec![Shareholder{address:ctx.accounts.bonding_curve.creator,share_bps:10000}];state.exit(&ID)?;
  call(PUMP,vec![ctx.accounts.bonding_curve.to_account_info(),ctx.accounts.payer.to_account_info(),ctx.accounts.system_program.to_account_info(),ctx.accounts.pump_event_authority.to_account_info(),ctx.accounts.pump_program.to_account_info()],&[(true,false),(true,true),(false,false),(false,false),(false,false)],vec![234,102,194,203,150,72,62,229])?;
  call(PUMP,vec![ctx.accounts.mint.to_account_info(),ctx.accounts.bonding_curve.to_account_info(),state.to_account_info(),ctx.accounts.pump_event_authority.to_account_info(),ctx.accounts.pump_program.to_account_info()],&[(false,false),(true,false),(false,false),(false,false),(false,false)],vec![87,124,52,191,52,38,214,232])?;
  state.admin=creator;state.shareholders=vec![Shareholder{address:creator,share_bps:10000}];state.exit(&ID)?;
  if graduated {
   let pool=ctx.accounts.pool.as_ref().unwrap();let program=ctx.accounts.pump_amm_program.as_ref().unwrap();let event=ctx.accounts.pump_amm_event_authority.as_ref().unwrap();
   call(AMM,vec![pool.to_account_info(),ctx.accounts.payer.to_account_info(),ctx.accounts.system_program.to_account_info(),event.to_account_info(),program.to_account_info()],&[(true,false),(true,true),(false,false),(false,false),(false,false)],vec![234,102,194,203,150,72,62,229])?;
   call(AMM,vec![pool.to_account_info(),state.to_account_info(),event.to_account_info(),program.to_account_info()],&[(true,false),(false,false),(false,false),(false,false)],vec![208,8,159,4,74,175,16,58])?;
  }
  let event=CreateFeeSharingConfigEvent{timestamp:Clock::get()?.unix_timestamp,mint:ctx.accounts.mint.key(),bonding_curve:ctx.accounts.bonding_curve.key(),pool:ctx.accounts.pool.as_ref().map(|x|x.key()),sharing_config:state.key(),admin:creator,initial_shareholders:state.shareholders.clone(),status:ConfigStatus::Active};emit!(event);emit_cpi!(event);Ok(())
 }
}
fn call<'info>(program_id:Pubkey,infos:Vec<AccountInfo<'info>>,flags:&[(bool,bool)],data:Vec<u8>)->Result<()>{let accounts=infos.iter().zip(flags).map(|(a,(w,s))|if *w{AccountMeta::new(a.key(),*s)}else{AccountMeta::new_readonly(a.key(),*s)}).collect();invoke(&Instruction{program_id,accounts,data},&infos)?;Ok(())}
#[derive(Accounts)]
pub struct CreateFeeSharingConfig<'info>{
 /// CHECK: event PDA.
 #[account(seeds=[b"__event_authority"],bump)]pub event_authority:UncheckedAccount<'info>,
 pub program:Program<'info,crate::program::PumpFeesCandidate>,
 #[account(mut)]pub payer:Signer<'info>,
 #[account(seeds=[b"global"],bump,seeds::program=PUMP)]pub global:Box<Account<'info,pump_global::Global>>,
 pub mint:InterfaceAccount<'info,anchor_spl::token_interface::Mint>,
 #[account(init_if_needed,payer=payer,space=1024,seeds=[b"sharing-config",mint.key().as_ref()],bump)]pub sharing_config:Account<'info,SharingConfig>,
 pub system_program:Program<'info,System>,
 #[account(mut,seeds=[b"bonding-curve",mint.key().as_ref()],bump,seeds::program=PUMP)]pub bonding_curve:Account<'info,BondingCurve>,
 pub pump_program:Program<'info,Pump>,
 /// CHECK: external event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=PUMP)]pub pump_event_authority:UncheckedAccount<'info>,
 /// CHECK: optional pool validated in handler.
 #[account(mut)]pub pool:Option<Account<'info,Pool>>,
 pub pump_amm_program:Option<Program<'info,Amm>>,
 /// CHECK: external event PDA.
 #[account(seeds=[b"__event_authority"],bump,seeds::program=AMM)]pub pump_amm_event_authority:Option<UncheckedAccount<'info>>,
}
#[event]
pub struct CreateFeeSharingConfigEvent{pub timestamp:i64,pub mint:Pubkey,pub bonding_curve:Pubkey,pub pool:Option<Pubkey>,pub sharing_config:Pubkey,pub admin:Pubkey,pub initial_shareholders:Vec<Shareholder>,pub status:ConfigStatus}
