use anchor_lang::prelude::*;
#[error_code]
pub enum FeeError {
    #[msg("Only Pump and PumpSwap programs can call this instruction")]
    UnauthorizedProgram,
    #[msg("Invalid admin")]
    InvalidAdmin,
    #[msg("No fee tiers provided")]
    NoFeeTiers,
    #[msg("format")]
    TooManyFeeTiers,
    #[msg("The offset should be <= fee_config.fee_tiers.len()")]
    OffsetNotContinuous,
    #[msg("Fee tiers must be sorted by market cap threshold (ascending)")]
    FeeTiersNotSorted,
    #[msg("Fee total must not exceed 10_000bps")]
    InvalidFeeTotal,
    #[msg("Invalid Sharing Config")]
    InvalidSharingConfig,
    #[msg("Invalid Pool")]
    InvalidPool,
    #[msg("Sharing config authority has been revoked - sharing config can only be updated once")]
    SharingConfigAdminRevoked,
    #[msg("No shareholders provided")]
    NoShareholders,
    #[msg("format")]
    TooManyShareholders,
    #[msg("Duplicate shareholder address")]
    DuplicateShareholder,
    #[msg("Not enough remaining accounts")]
    NotEnoughRemainingAccounts,
    #[msg("Invalid share total - must equal 10_000 basis points")]
    InvalidShareTotal,
    #[msg("Share calculation overflow")]
    ShareCalculationOverflow,
    #[msg("The given account is not authorized to execute this instruction.")]
    NotAuthorized,
    #[msg("Shareholder cannot have zero share")]
    ZeroShareNotAllowed,
    #[msg("Fee sharing config is not active")]
    SharingConfigNotActive,
    #[msg("AMM accounts are required for graduated coins")]
    AmmAccountsRequiredForGraduatedCoin,
    #[msg("Remaining account key doesn't match shareholder address")]
    ShareholderAccountMismatch,
    #[msg("Feature is currently deactivated")]
    FeatureDeactivated,
    #[msg("User ID exceeds maximum length")]
    UserIdTooLong,
    #[msg("Instruction is deprecated")]
    DeprecatedInstruction,
    #[msg("Reward split can only be updated once")]
    FeeSharesAlreadyUpdated,
    #[msg("Math overflow")]
    MathOverflow,
    #[msg("Invalid buybackindex")]
    InvalidBuybackIndex,
    #[msg("Claim rate limit exceeded")]
    ClaimRateLimitExceeded,
    #[msg("Account is not a valid FeeConfig for this instruction")]
    InvalidFeeConfigAccount,
    #[msg("Account type not supported")]
    AccountTypeNotSupported,
    #[msg("Mint does not match quote mint")]
    InvalidMint,
    #[msg("Unsupported quote mint")]
    UnsupportedQuoteMint,
    #[msg("Invalid remaining accounts")]
    InvalidRemainingAccounts,
    #[msg("Pool creator_fees must be swept before the shares change")]
    PoolCreatorFeesNotSwept,
    #[msg("quote_mint is not the bonding curve's quote mint")]
    InvalidQuoteMint,
    #[msg("Token withdrawals need quote_mint, vault_ata, user_ata and token_program")]
    IncompleteTokenAccounts,
    #[msg("Nothing to withdraw")]
    NothingToWithdraw,
}
