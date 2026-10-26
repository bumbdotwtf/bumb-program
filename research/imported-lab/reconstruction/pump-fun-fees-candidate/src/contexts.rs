//! IDL-derived account order/flags only; business constraints are open.
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct AdminCtoSharingConfig<'info> {
    pub pool_authority: Signer<'info>,
    pub authority: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub sharing_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct ClaimSocialFeePda<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub recipient: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub social_fee_pda: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    pub social_claim_authority: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct ClaimSocialFeePdaV2<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub recipient: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub social_fee_pda: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub quote_mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_social_fee_pda: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_recipient: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub quote_token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    pub social_claim_authority: Signer<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct CrankDonationFeePda<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub rent: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub donation_fee_pda: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub quote_mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub donation_fee_pda_ata: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub donation_relay_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub donation_relay_event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint_whitelist: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub epoch_tracker: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub debouncer: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub debouncer_ata: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct CreateDonationFeePda<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub donation_fee_pda: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub base_mint: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub bonding_curve: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pool: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub sharing_config: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct CreateFeeSharingConfig<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
    #[account(mut)]
    pub payer: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub sharing_config: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub bonding_curve: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_event_authority: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub pool: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_amm_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_amm_event_authority: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct CreateSocialFeePda<'info> {
    #[account(mut)]
    pub payer: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub social_fee_pda: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct ExtendFeeConfig<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub user: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct GetFees<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct GetFeesWithQuoteMint<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct InitializeBuyback<'info> {
    #[account(mut)]
    pub payer: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault_ata: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct InitializeFeeConfig<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct InitializeFeeProgramGlobal<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_global: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct RevokeFeeSharingAuthority {}

#[derive(Accounts)]
pub struct SetAuthority<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SetClaimRateLimit<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SetDisableFlags<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SetExoticFlatFees<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    #[account(mut)]
    pub admin: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SetSocialClaimAuthority<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct SweepBuyback<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub destination: UncheckedAccount<'info>,
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault_ata: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub destination_ata: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct TransferFeeSharingAuthority {}

#[derive(Accounts)]
pub struct UpdateAdmin<'info> {
    pub admin: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub new_admin: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateBuybackAuthority<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateBuybackClaimRateLimit<'info> {
    #[account(mut)]
    pub authority: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_program_global: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub buyback_vault: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateFeeConfig<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub admin: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateFeeShares<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
    pub authority: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub sharing_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub bonding_curve: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_creator_vault: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_amm_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub amm_event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub wsol_mint: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub coin_creator_vault_authority: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub coin_creator_vault_ata: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateFeeSharesV2<'info> {
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
    #[account(mut)]
    pub authority: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub global: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub sharing_config: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub bonding_curve: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_creator_vault: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_creator_vault_ata: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub pump_amm_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub amm_event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub quote_mint: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub associated_token_program: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub coin_creator_vault_authority: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub coin_creator_vault_ata: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpdateStableFeeConfig<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub admin: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpsertFeeTiers<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub admin: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct UpsertStableFeeTiers<'info> {
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub fee_config: UncheckedAccount<'info>,
    pub admin: Signer<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub config_program_id: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}

#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub referral_vault: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub quote_mint: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub vault_ata: UncheckedAccount<'info>,
    #[account(mut)]
    /// CHECK: Exact deployed constraint not recovered.
    pub user_ata: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub token_program: UncheckedAccount<'info>,
    pub system_program: Program<'info, System>,
    /// CHECK: Exact deployed constraint not recovered.
    pub event_authority: UncheckedAccount<'info>,
    /// CHECK: Exact deployed constraint not recovered.
    pub program: UncheckedAccount<'info>,
}
