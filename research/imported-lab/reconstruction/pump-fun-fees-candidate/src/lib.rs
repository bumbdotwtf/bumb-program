//! Fail-closed full-interface candidate for pinned Pump Fees.
//! It is not the deployed program source.
use anchor_lang::prelude::*;

mod contexts;
mod types;
use contexts::*;
use types::*;

declare_id!("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ");

#[program]
pub mod pump_fees_candidate {
    use super::*;

    #[allow(unused_variables)]
    pub fn admin_cto_sharing_config(_ctx: Context<AdminCtoSharingConfig>, new_admin: Option<Pubkey>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn claim_social_fee_pda(_ctx: Context<ClaimSocialFeePda>, user_id: String, platform: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn claim_social_fee_pda_v2(_ctx: Context<ClaimSocialFeePdaV2>, user_id: String, platform: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn crank_donation_fee_pda(_ctx: Context<CrankDonationFeePda>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn create_donation_fee_pda(_ctx: Context<CreateDonationFeePda>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn create_fee_sharing_config(_ctx: Context<CreateFeeSharingConfig>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn create_social_fee_pda(_ctx: Context<CreateSocialFeePda>, user_id: String, platform: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn extend_fee_config(_ctx: Context<ExtendFeeConfig>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn get_fees(_ctx: Context<GetFees>, is_pump_pool: bool, market_cap_lamports: u128, trade_size_lamports: u64, is_new_quote_mint: OptionBool) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn get_fees_with_quote_mint(_ctx: Context<GetFeesWithQuoteMint>, is_pump_pool: bool, market_cap_lamports: u128, quote_mint: Pubkey) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn initialize_buyback(_ctx: Context<InitializeBuyback>, index: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn initialize_fee_config(_ctx: Context<InitializeFeeConfig>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn initialize_fee_program_global(_ctx: Context<InitializeFeeProgramGlobal>, social_claim_authority: Pubkey, disable_flags: u8, claim_rate_limit: u64) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn revoke_fee_sharing_authority(_ctx: Context<RevokeFeeSharingAuthority>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn set_authority(_ctx: Context<SetAuthority>, new_authority: Pubkey) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn set_claim_rate_limit(_ctx: Context<SetClaimRateLimit>, claim_rate_limit: u64) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn set_disable_flags(_ctx: Context<SetDisableFlags>, disable_flags: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn set_exotic_flat_fees(_ctx: Context<SetExoticFlatFees>, exotic_flat_fees: Fees) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn set_social_claim_authority(_ctx: Context<SetSocialClaimAuthority>, social_claim_authority: Pubkey) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn sweep_buyback(_ctx: Context<SweepBuyback>, index: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn transfer_fee_sharing_authority(_ctx: Context<TransferFeeSharingAuthority>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_admin(_ctx: Context<UpdateAdmin>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_buyback_authority(_ctx: Context<UpdateBuybackAuthority>, index: u8, new_authority: Pubkey) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_buyback_claim_rate_limit(_ctx: Context<UpdateBuybackClaimRateLimit>, index: u8, claim_rate_limit: i64) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_fee_config(_ctx: Context<UpdateFeeConfig>, fee_tiers: Vec<FeeTier>, flat_fees: Fees) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_fee_shares(_ctx: Context<UpdateFeeShares>, shareholders: Vec<Shareholder>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_fee_shares_v2(_ctx: Context<UpdateFeeSharesV2>, shareholders: Vec<Shareholder>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn update_stable_fee_config(_ctx: Context<UpdateStableFeeConfig>, fee_tiers: Vec<FeeTier>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn upsert_fee_tiers(_ctx: Context<UpsertFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn upsert_stable_fee_tiers(_ctx: Context<UpsertStableFeeTiers>, fee_tiers: Vec<FeeTier>, offset: u8) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

    #[allow(unused_variables)]
    pub fn withdraw(_ctx: Context<Withdraw>) -> Result<()> {
        Err(error!(CandidateError::Unsupported))
    }

}

#[error_code]
pub enum CandidateError {
    #[msg("Research candidate handler not reconstructed")]
    Unsupported,
}
