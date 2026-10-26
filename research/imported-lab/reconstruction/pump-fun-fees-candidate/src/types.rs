//! IDL argument types needed for instruction deserialization.
use anchor_lang::prelude::*;

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct FeeTier {
    pub market_cap_lamports_threshold: u128,
    pub fees: Fees,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Fees {
    pub lp_fee_bps: u64,
    pub protocol_fee_bps: u64,
    pub creator_fee_bps: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct OptionBool(pub bool);

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct Shareholder {
    pub address: Pubkey,
    pub share_bps: u16,
}
