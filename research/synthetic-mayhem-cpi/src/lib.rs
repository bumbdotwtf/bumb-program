//! Synthetic local-only caller. It replaces the Mayhem program in a private VM.
//! It does not establish that the deployed Mayhem program exposes this CPI.
#![allow(unexpected_cfgs)]
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint, entrypoint::ProgramResult,
    instruction::{AccountMeta, Instruction},
    program::invoke_signed,
    program_error::ProgramError,
    pubkey::Pubkey,
};

entrypoint!(process_instruction);

fn process_instruction(program_id: &Pubkey, accounts: &[AccountInfo], _data: &[u8]) -> ProgramResult {
    if accounts.len() != 8 {
        return Err(ProgramError::NotEnoughAccountKeys);
    }
    let mut iter = accounts.iter();
    let vault = next_account_info(&mut iter)?;
    let token_vault = next_account_info(&mut iter)?;
    let mint = next_account_info(&mut iter)?;
    let global = next_account_info(&mut iter)?;
    let curve = next_account_info(&mut iter)?;
    let token_program = next_account_info(&mut iter)?;
    let event = next_account_info(&mut iter)?;
    let pump = next_account_info(&mut iter)?;
    let (expected, bump) = Pubkey::find_program_address(&[b"sol-vault"], program_id);
    if *vault.key != expected || !pump.executable {
        return Err(ProgramError::InvalidArgument);
    }
    let ix = Instruction {
        program_id: *pump.key,
        accounts: vec![
            AccountMeta::new(*vault.key, true),
            AccountMeta::new(*token_vault.key, false),
            AccountMeta::new_readonly(*mint.key, false),
            AccountMeta::new_readonly(*global.key, false),
            AccountMeta::new(*curve.key, false),
            AccountMeta::new_readonly(*token_program.key, false),
            AccountMeta::new_readonly(*event.key, false),
            AccountMeta::new_readonly(*pump.key, false),
        ],
        data: vec![0x3d, 0xa9, 0xbc, 0xbf, 0x99, 0x95, 0x2a, 0x61],
    };
    let bump_seed = [bump];
    invoke_signed(&ix, accounts, &[&[b"sol-vault", &bump_seed]])
}
