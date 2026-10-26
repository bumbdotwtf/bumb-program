//! Static natural-source hypothesis, not historical source or build evidence.
//! 64-bit slice lengths; ordinary valid-memory, memcmp and RefCell premises.
//! Acquire an immutable mint-data borrow BEFORE calling safe_mint_data, retain
//! it throughout, and drop on every normal return. Borrow exhaustion follows
//! original panic/unwind behavior (116000), not a fabricated Relay error.
#[derive(Debug)]
pub enum DecodeError { InvalidAccountData, UninitializedAccount }

fn u16le(b: &[u8], p: usize) -> u16 {
    u16::from_le_bytes([b[p], b[p+1]])
}
fn u32le(b: &[u8], p: usize) -> u32 {
    u32::from_le_bytes([b[p], b[p+1], b[p+2], b[p+3]])
}
fn present(key: &[u8]) -> bool { key.iter().any(|b| *b != 0) }

// W33 -> W250: all base/header validation precedes the authority policy.
// Authority values are COption tags, NOT OptionalNonZeroPubkey values.
fn base_and_tlv(data: &[u8]) -> Result<(u32, u32, &[u8]), DecodeError> {
    let n = data.len();
    if n < 82 || n == 355 { return Err(DecodeError::InvalidAccountData); }
    let mint = u32le(data, 0);
    if mint > 1 { return Err(DecodeError::InvalidAccountData); }
    if data[45] > 1 { return Err(DecodeError::InvalidAccountData); }
    let freeze = u32le(data, 46);
    if freeze > 1 { return Err(DecodeError::InvalidAccountData); }
    if data[45] == 0 { return Err(DecodeError::UninitializedAccount); }
    if n == 82 { return Ok((mint, freeze, &data[82..82])); }
    // Original requires residual >=85, hence total >=167, not >=166.
    if n < 167 || data[82..165].iter().any(|b| *b != 0) || data[165] != 1 {
        return Err(DecodeError::InvalidAccountData);
    }
    Ok((mint, freeze, &data[166..]))
}

// Common specialization of the SIX independent scans in W106/W32/W31/W30.
// None means no successful typed lookup; it intentionally collapses lookup
// errors only because every caller here suppresses those errors. It does NOT
// claim that the underlying helper's Err values equal absence generally.
fn lookup(tlv: &[u8], wanted: u16, exact_len: usize) -> Option<&[u8]> {
    const MINT_TYPES: u32 = 0x07fd565a; // all recognized mint types, including wanted
    let mut cursor = 0usize;
    while cursor < tlv.len() {
        let length_at = cursor.saturating_add(2);
        let value_at = cursor.saturating_add(4);
        if value_at > tlv.len() { return None; }
        // With a real 64-bit slice and value_at <= len these range relations
        // hold. Original retains panic paths for impossible inverted ranges.
        let ty = u16le(tlv, cursor);
        if ty > 27 { return None; }
        if ty == wanted {
            let end = value_at.saturating_add(u16le(tlv, length_at) as usize);
            if end > tlv.len() || end - value_at != exact_len { return None; }
            return Some(&tlv[value_at..end]);
        }
        if (MINT_TYPES & (1u32 << ty)) == 0 { return None; }
        // Does not validate the skipped type's expected length or contents.
        // An oversize end leaves the loop; no global TLV error propagates.
        cursor = value_at.saturating_add(u16le(tlv, length_at) as usize);
    }
    None
}

/// Entire application policy of inferred window106 on already borrowed data.
/// token2022_owner is exact owner equality with ELF bytes[753152..753184].
/// Owner admission to Tokenkeg/Token2022 belongs to shared112 before this call.
pub fn safe_mint_data(data: &[u8], token2022_owner: bool) -> Result<bool, DecodeError> {
    let (mint_authority, freeze_authority, tlv) = base_and_tlv(data)?;
    if mint_authority != 0 || freeze_authority != 0 { return Ok(false); }
    if !token2022_owner { return Ok(true); }
    // 116040..116864: TransferFeeConfig; withdrawal key [32,64), withheld
    // amount, epochs, and maximum fees have NO policy tests here.
    if let Some(fee) = lookup(tlv, 1, 108) {
        if present(&fee[0..32]) || u16le(fee, 88) != 0 || u16le(fee, 106) != 0 {
            return Ok(false);
        }
    }
    // 116912..117728: TransferHook authority and program_id, each optional
    // nonzero key. Only None/None is admitted after successful typed lookup.
    if let Some(hook) = lookup(tlv, 14, 64) {
        if present(&hook[0..32]) || present(&hook[32..64]) { return Ok(false); }
    }
    // 117776..118320: rejects existence, not nonzero delegate authority.
    if lookup(tlv, 12, 32).is_some() { return Ok(false); }
    // W32 is extension tag3 (NOT tag32): MintCloseAuthority.
    if let Some(close) = lookup(tlv, 3, 32) {
        if present(close) { return Ok(false); }
    }
    // W31 is extension tag6: DefaultAccountState. Exactly byte1 admitted.
    if let Some(state) = lookup(tlv, 6, 1) {
        if state[0] != 1 { return Ok(false); }
    }
    // W30 is extension tag9: NonTransferable (zero-sized marker).
    if lookup(tlv, 9, 0).is_some() { return Ok(false); }
    Ok(true)
}

// Integration sketch (existing error/AccountInfo types, not compiled here):
// require(message.len() < 256, 6009)?;
// require(tip_bps <= 10000, 6018)?;
// require(mint.owner == TOKEN || mint.owner == TOKEN2022, 6029)?;
// if mint.key != NATIVE && mint.key != NATIVE2022 && !whitelist.contains(mint.key) {
//     let data = mint.data.borrow(); // panic contract, not try_borrow->6031
//     let safe = safe_mint_data(&data, mint.owner == TOKEN2022)
//         .map_err(original_program_error_to_anchor_652528)?;
//     require(safe, 6031)?;
// }
// Only after success does shared112 initialize tracker/debouncer and continue.
