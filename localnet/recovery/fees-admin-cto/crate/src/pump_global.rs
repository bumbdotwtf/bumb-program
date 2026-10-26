//! The historical Pump Global layout consumed by the captured Fees program.
use anchor_lang::prelude::*;
use anchor_lang::Discriminator;
pub const PUMP_ID: Pubkey = anchor_lang::solana_program::pubkey!("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P");
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Global {
    pub initialized: bool,
    pub authority: Pubkey,
    pub fee_recipient: Pubkey,
    pub initial_virtual_token_reserves: u64,
    pub initial_virtual_sol_reserves: u64,
    pub initial_real_token_reserves: u64,
    pub token_total_supply: u64,
    pub fee_basis_points: u64,
    pub withdraw_authority: Pubkey,
    pub enable_migrate: bool,
    pub pool_migration_fee: u64,
    pub creator_fee_basis_points: u64,
    pub fee_recipients: [Pubkey; 7],
    pub set_creator_authority: Pubkey,
    pub admin_set_creator_authority: Pubkey,
    pub create_v2_enabled: bool,
    pub whitelist_pda: Pubkey,
    pub reserved_fee_recipient: Pubkey,
    pub mayhem_mode_enabled: bool,
    pub reserved_fee_recipients: [Pubkey; 7],
}
impl Owner for Global { fn owner() -> Pubkey { PUMP_ID } }
impl Discriminator for Global { const DISCRIMINATOR: &'static [u8] = &[167, 232, 232, 177, 200, 108, 114, 127]; }
impl AccountDeserialize for Global {
    fn try_deserialize(buf: &mut &[u8]) -> Result<Self> {
        if buf.len() < 8 { return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorNotFound)); }
        if &buf[..8] != Self::DISCRIMINATOR { return Err(error!(anchor_lang::error::ErrorCode::AccountDiscriminatorMismatch)); }
        Self::try_deserialize_unchecked(buf)
    }
    fn try_deserialize_unchecked(buf: &mut &[u8]) -> Result<Self> {
        Self::deserialize(&mut &buf[8..]).map_err(|_| error!(anchor_lang::error::ErrorCode::AccountDidNotDeserialize))
    }
}
// This type is consumed read-only by the recovered Fees contexts.
impl AccountSerialize for Global {}
