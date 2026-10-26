//! Captured relay IDL170 application reconstruction; static, UNCOMPILED.
//! Requires the real aliased AccountInfo adapter in idl_runtime.rs. No IDL body,
//! parser, serialization or generated exit is delegated to a success callback.
use crate::{Account, Key, Cpi, Meta};
use crate::codec::constants::RELAY;
use crate::dispatch_interfaces::DispatchRuntime;
use crate::idl_runtime::IdlRuntime;

pub const DISC: [u8; 8] = [24, 70, 98, 191, 58, 144, 123, 158];
const SYSTEM: Key = [0; 32];
const HEADER: usize = 44;
// Captured original origin programs/contracts/src/lib.rs:36 is evidence only.
// The new source does not claim that original path/line; see diagnostic-gaps.json.

pub type ProgramFailure = solana_program::program_error::ProgramError;
#[derive(Debug)]
pub enum Cause { Framework(u32), Program(ProgramFailure), Owned(crate::generated_exit::ExitError) }
#[derive(Debug)]
pub struct IdlError {
    pub cause: Cause,
    pub account: Option<&'static str>,
    pub keys: Option<(Key, Key)>,
    pub values: Option<(u64, u64)>,
    pub origin: Option<(&'static str, u32)>,
}
pub type I<T> = Result<T, IdlError>;
fn code(n: u32) -> IdlError {
    IdlError { cause: Cause::Framework(n), account: None, keys: None, values: None, origin: None }
}
pub fn program_error(error: ProgramFailure) -> IdlError {
    IdlError { cause: Cause::Program(error), account: None, keys: None, values: None, origin: None }
}
// Typed Account::try_from boxes a borrow failure before outer account naming.
fn own_typed_borrow_failure(mut error: IdlError) -> IdlError {
    error.cause = match error.cause {
        Cause::Program(program) => Cause::Owned(program.into()),
        cause => cause,
    };
    error
}
fn named<T>(r: I<T>, name: &'static str) -> I<T> {
    r.map_err(|mut e| {
        match e.cause {
            Cause::Owned(error) => { e.cause = Cause::Owned(error.with_account_name(name)); }
            _ => { e.account = Some(name); e.origin = None; }
        }
        e
    })
}
fn require(ok: bool, n: u32, name: &'static str) -> I<()> {
    named(if ok { Ok(()) } else { Err(code(n)) }, name)
}
fn require_keys(left: Key, right: Key, n: u32, name: &'static str) -> I<()> {
    if left == right { return Ok(()); }
    let mut e = code(n); e.keys = Some((left, right)); named(Err(e), name)
}

#[derive(Clone, Copy, Debug)]
pub struct Header { pub authority: Key, pub data_len: u32 }
struct Typed { info: Account, value: Header }
enum Instruction {
    Create(u64), CreateBuffer, Write(Vec<u8>), SetBuffer,
    SetAuthority(Key), Close, Resize(u64),
}
// W170 enum decoder consumes a prefix, not the entire suffix. Allocation/OOM
// details of W77's Vec reader remain a stated framework premise.
fn decode(data: &[u8]) -> I<Instruction> {
    let (&tag, tail) = data.split_first().ok_or_else(||code(102))?;
    let u64_arg = || -> I<u64> {
        Ok(u64::from_le_bytes(tail.get(..8).ok_or_else(||code(102))?.try_into().unwrap()))
    };
    Ok(match tag {
        0 => Instruction::Create(u64_arg()?),
        1 => Instruction::CreateBuffer,
        2 => {
            let len = u32::from_le_bytes(tail.get(..4).ok_or_else(||code(102))?.try_into().unwrap()) as usize;
            let bytes = tail.get(4..).and_then(|s|s.get(..len)).ok_or_else(||code(102))?;
            Instruction::Write(bytes.to_vec())
        }
        3 => Instruction::SetBuffer,
        4 => Instruction::SetAuthority(tail.get(..32).ok_or_else(||code(102))?.try_into().unwrap()),
        5 => Instruction::Close,
        6 => Instruction::Resize(u64_arg()?),
        _ => return Err(code(102)),
    })
}
// W218: skip eight bytes even unchecked; <8 is a slice panic, 8..43 ->3003.
// Neither checked nor unchecked decode validates data_len against capacity.
fn unchecked_header(data: &[u8]) -> I<Header> {
    use std::io::{Error, ErrorKind, Read};
    let mut tail = &data[8..];
    let mut decode = || -> std::io::Result<Header> {
        let mut read_field = |field: &mut [u8]| {
            tail.read_exact(field).map_err(|error| {
                if error.kind() == ErrorKind::UnexpectedEof {
                    Error::new(ErrorKind::InvalidInput, "Unexpected length of input")
                } else {
                    error
                }
            })
        };
        let mut authority = [0; 32];
        read_field(&mut authority)?;
        let mut data_len = [0; 4];
        read_field(&mut data_len)?;
        Ok(Header { authority, data_len: u32::from_le_bytes(data_len) })
    };
    decode().map_err(|error| {
        let owned = crate::generated_exit::exit_error::account_did_not_deserialize();
        drop(error);
        IdlError { cause: Cause::Owned(owned), account: None, keys: None, values: None, origin: None }
    })
}
fn checked_header(data: &[u8]) -> I<Header> {
    if data.len() < 8 {
        return Err(IdlError {
            cause: Cause::Owned(crate::generated_exit::exit_error::account_discriminator_not_found()),
            account: None, keys: None, values: None, origin: None,
        });
    }
    if data[..8] != DISC {
        let owned = crate::generated_exit::exit_error::account_discriminator_mismatch(
            crate::generated_exit::exit_error::Source { filename: file!(), line: line!() },
        ).with_account_name("IdlAccount");
        return Err(IdlError {
            cause: Cause::Owned(owned), account: None, keys: None, values: None, origin: None,
        }); // enclosing generated parser replaces the owned account name.
    }
    unchecked_header(data)
}
struct Cursor<'a> { accounts: &'a [Account], at: usize }
impl<'a> Cursor<'a> {
    fn new(accounts: &'a [Account]) -> Self { Self { accounts, at: 0 } }
    fn raw(&mut self) -> I<Account> {
        let a = self.accounts.get(self.at).copied().ok_or_else(||code(3005))?;
        self.at += 1; Ok(a)
    }
    fn raw_named(&mut self, name: &'static str) -> I<Account> { named(self.raw(), name) }
    fn signer(&mut self, name: &'static str) -> I<Account> {
        let a = self.raw_named(name)?;
        require(a.signer, 3010, name)?; Ok(a) // W80 ->W280, not constraint2002.
    }
    fn system<R: IdlRuntime>(&mut self, rt: &R) -> I<Account> {
        let a = self.raw_named("system_program")?;
        require_keys(a.key, SYSTEM, 3008, "system_program")?;
        require(rt.idl_executable(a), 3009, "system_program")?; Ok(a)
    }
    fn typed<R: IdlRuntime>(&mut self, rt: &R, name: &'static str) -> I<Typed> {
        let a = self.raw_named(name)?;
        named(typed(rt, a, true), name)
    }
}
fn typed<R: IdlRuntime>(rt: &R, info: Account, checked: bool) -> I<Typed> {
    let owner = rt.idl_owner(info);
    if owner == SYSTEM && rt.idl_lamports_panicking(info) == 0 { return Err(code(3012)); }
    if owner != RELAY { let mut e = code(3007); e.keys = Some((owner, RELAY)); return Err(e); }
    let bytes = if checked {
        rt.idl_data(info).map_err(own_typed_borrow_failure)?
    } else {
        rt.idl_data(info)?
    };
    let value = if checked { checked_header(&bytes)? } else { unchecked_header(&bytes)? };
    drop(bytes); Ok(Typed { info, value })
}
fn writable(a: Account, name: &'static str) -> I<()> { require(a.writable, 2000, name) }
fn authorized(idl: &Typed, authority: Account, name: &'static str) -> I<()> {
    require_keys(idl.value.authority, authority.key, 2001, name)
}
fn active_authority(a: Account) -> I<()> { require(a.key != SYSTEM, 2003, "authority") }
// W213: typed idl, signer, then idl mut/has_one, then non-erased authority.
fn admit_write<R: IdlRuntime>(rt: &R, c: &mut Cursor<'_>) -> I<Typed> {
    let idl = c.typed(rt, "idl")?;
    let authority = c.signer("authority")?;
    writable(idl.info, "idl")?; authorized(&idl, authority, "idl")?;
    active_authority(authority)?; Ok(idl)
}
// W211: System program typing precedes all derived constraints. Authority is
// writable here (payer), unlike Write/SetAuthority/SetBuffer/Close.
fn admit_resize<R: IdlRuntime>(rt: &R, c: &mut Cursor<'_>) -> I<(Typed, Account, Account)> {
    let idl = c.typed(rt, "idl")?;
    let authority = c.signer("authority")?;
    let system = c.system(rt)?;
    writable(idl.info, "idl")?; authorized(&idl, authority, "idl")?;
    writable(authority, "authority")?; active_authority(authority)?;
    Ok((idl, authority, system))
}
// W207: buffer's raw constraint compares BOTH STORED authorities; only then
// does the destination's has_one compare against the actual Signer.
fn admit_set_buffer<R: IdlRuntime>(rt: &R, c: &mut Cursor<'_>) -> I<(Typed, Typed)> {
    let buffer = c.typed(rt, "buffer")?;
    let idl = c.typed(rt, "idl")?;
    let authority = c.signer("authority")?;
    writable(buffer.info, "buffer")?;
    require(buffer.value.authority == idl.value.authority, 2003, "buffer")?;
    writable(idl.info, "idl")?; authorized(&idl, authority, "idl")?;
    active_authority(authority)?; Ok((buffer, idl))
}
// W205: generated close-key inequality precedes authority raw constraint and
// destination mutability. No extra authority writable or destination owner test.
fn admit_close<R: IdlRuntime>(rt: &R, c: &mut Cursor<'_>) -> I<(Typed, Account)> {
    let account = c.typed(rt, "account")?;
    let authority = c.signer("authority")?;
    let destination = c.raw_named("sol_destination")?;
    writable(account.info, "account")?; authorized(&account, authority, "account")?;
    require(account.info.key != destination.key, 2011, "account")?;
    active_authority(authority)?; writable(destination, "sol_destination")?;
    Ok((account, destination))
}
fn admit_buffer<R: IdlRuntime>(rt: &R, c: &mut Cursor<'_>) -> I<(Typed, Account)> {
    let info = c.raw()?; // W209 initial missing buffer is unnamed3005.
    let authority = c.signer("authority")?;
    let rent = rt.idl_rent()?;
    let data = rt.idl_data(info)?; // initial borrow errors also unnamed.
    if data[..8] != [0; 8] { return named(Err(code(2013)), "buffer"); }
    // Original holds the first immutable guard through the unchecked typed load.
    let buffer = named(typed(rt, info, false), "buffer")?;
    drop(data);
    writable(info, "buffer")?;
    let balance = rt.idl_lamports_panicking(info);
    let size = rt.idl_data(info)?.len();
    require(balance >= rent.minimum_balance(size), 2005, "buffer")?;
    active_authority(authority)?;
    Ok((buffer, authority))
}
fn admit_create<R: IdlRuntime>(rt: &mut R, c: &mut Cursor<'_>, program: &Key) -> I<(Account, Account, Account, Account, Account)> {
    let from = c.raw_named("from")?;
    let to = c.raw_named("to")?;
    let base = c.raw_named("base")?;
    let system = c.system(rt)?;
    let executable = c.raw_named("program")?;
    require(from.signer, 2002, "from")?;
    writable(to, "to")?;
    let (expected, _bump) = rt.find_program_address(&[], program);
    require_keys(base.key, expected, 2006, "base")?;
    require(rt.idl_executable(executable), 2007, "program")?;
    Ok((from, to, base, system, executable))
}

// W281/19/216 stream each field. A short account has its available prefix
// overwritten before3004; no upfront capacity check or trailing-byte erasure.
fn write_header(data: &mut [u8], h: Header) -> I<()> {
    use std::io::Write;
    let serialize = || -> std::io::Result<()> {
        let mut writer = crate::generated_exit::bpf_writer::BpfWriter::new(data);
        writer.write_all(&DISC)?;
        writer.write_all(&h.authority)?;
        writer.write_all(&h.data_len.to_le_bytes())
    };
    serialize().map_err(|error| {
        drop(error);
        IdlError {
            cause: Cause::Owned(crate::generated_exit::exit_error::account_did_not_serialize()),
            account: None, keys: None, values: None, origin: None,
        }
    })
}
fn exit_header<R: IdlRuntime>(rt: &R, program: &Key, idl: &Typed, name: &'static str) -> I<()> {
    if *program != RELAY { return Ok(()); } // TYPE owner comparison, not live owner.
    if rt.idl_owner(idl.info) == SYSTEM && rt.idl_data(idl.info).unwrap().is_empty() { return Ok(()); }
    named((|| { let mut bytes = rt.idl_data_mut(idl.info)?; write_header(&mut bytes, idl.value) })(), name)
}
fn create<R: IdlRuntime>(rt: &mut R, program: &Key, from: Account, to: Account,
    base_info: Account, system: Account, executable: Account, requested_payload: u64) -> I<()> {
    rt.log_instruction("Instruction: IdlCreateAccount");
    if *program != executable.key { return Err(code(1001)); }
    let (base, bump) = rt.find_program_address(&[], program); // recomputed by171.
    let address = rt.idl_create_with_seed(&base, b"anchor:idl", &executable.key).unwrap();
    let requested = requested_payload.checked_add(44).expect("IDL create space overflow");
    let rent = rt.idl_rent()?;
    let space = requested.min(10_000);
    let lamports = rent.minimum_balance(space as usize);
    // W320 ->W307: System bincode tag3, base32, seed length u64, seed bytes,
    // lamports u64, space u64, owner32. `to` is NOT pre-compared to address;
    // the real System CPI matches the derived writable meta to supplied infos.
    let mut data = 3u32.to_le_bytes().to_vec();
    data.extend_from_slice(&base); data.extend_from_slice(&10u64.to_le_bytes());
    data.extend_from_slice(b"anchor:idl"); data.extend_from_slice(&lamports.to_le_bytes());
    data.extend_from_slice(&space.to_le_bytes()); data.extend_from_slice(&executable.key);
    let ix = Cpi { program: SYSTEM, metas: vec![
        Meta {key:from.key, writable:true, signer:true},
        Meta {key:address, writable:true, signer:false},
        Meta {key:base, writable:false, signer:true}], data };
    rt.idl_invoke_signed(ix, &[from,to,base_info,system], &[vec![vec![bump]]])?;
    let bytes = rt.idl_data(to)?;
    let mut h = unchecked_header(&bytes)?; drop(bytes);
    h.authority = from.key; // preserve decoded data_len; genuine new account is zeroed.
    let mut bytes = rt.idl_data_mut(to)?;
    write_header(&mut bytes, h) // W216 directly, no extra typed owner/closed gate.
}
fn resize<R: IdlRuntime>(rt: &mut R, idl: &Typed, authority: Account, _system: Account, requested_total: u64) -> I<()> {
    rt.log_instruction("Instruction: IdlResizeAccount");
    if idl.value.data_len != 0 { return Err(code(1002)); }
    let current = rt.idl_data(idl.info).unwrap().len();
    let second = rt.idl_data(idl.info).unwrap().len();
    let delta = requested_total.checked_sub(second as u64)
        .expect("data_len should always be >= the current account space").min(10_000);
    let new_len = current.checked_add(delta as usize).expect("IDL resize space overflow");
    if new_len <= rt.idl_data(idl.info).unwrap().len() { return Ok(()); }
    let rent = rt.idl_rent()?;
    let minimum = rent.minimum_balance(new_len);
    let balance = rt.idl_lamports_panicking(idl.info);
    let amount = minimum.checked_sub(balance).expect("IDL resize rent subtraction overflow");
    let mut data = 2u32.to_le_bytes().to_vec(); data.extend_from_slice(&amount.to_le_bytes());
    let ix = Cpi {program:SYSTEM, metas:vec![Meta {key:authority.key,writable:true,signer:true},
        Meta {key:idl.info.key,writable:true,signer:false}], data};
    rt.idl_invoke_signed(ix, &[authority,idl.info], &[])?; // also when amount==0.
    rt.idl_realloc_zero_filled(idl.info, new_len) // W332 always zeros growth.
}
fn write<R: IdlRuntime>(rt: &mut R, idl: &mut Typed, input: &[u8]) -> I<()> {
    rt.log_instruction("Instruction: IdlWrite");
    let old = idl.value.data_len as usize;
    let end = old.checked_add(input.len()).expect("IDL write usize overflow");
    let n = u32::try_from(input.len()).unwrap();
    idl.value.data_len = idl.value.data_len.checked_add(n).expect("IDL write u32 overflow");
    let mut data = rt.idl_data_mut(idl.info).unwrap(); // panic, not propagated borrow error.
    data[HEADER..][old..end].copy_from_slice(input);
    Ok(())
}
fn set_buffer<R: IdlRuntime>(rt: &mut R, buffer: &Typed, idl: &mut Typed) -> I<()> {
    rt.log_instruction("Instruction: IdlSetBuffer");
    idl.value.data_len = buffer.value.data_len; // BEFORE both borrows and capacity checks.
    let mut dst_data = rt.idl_data_mut(idl.info).unwrap();
    let dst = &mut dst_data[HEADER..];
    let src_data = rt.idl_data(buffer.info).unwrap();
    let src = &src_data[HEADER..][..buffer.value.data_len as usize];
    let result = if dst.len() < src.len() {
        let mut e = code(2506);
        e.values = Some((dst.len() as u64, src.len() as u64)); Err(e)
    } else { dst[..src.len()].copy_from_slice(src); Ok(()) };
    drop(src_data); drop(dst_data); result
}
fn close<R: IdlRuntime>(rt: &mut R, source: Account, destination: Account) -> I<()> {
    // W173 is only this log; W206 then invokes282. Real adapter pins/releases
    // aliased Rc handles as destination first, source second; no byte cloning.
    rt.log_instruction("Instruction: IdlCloseAccount");
    let destination_balance = rt.idl_lamports_panicking(destination);
    let source_balance = rt.idl_lamports_panicking(source);
    let total = destination_balance.checked_add(source_balance).expect("IDL close lamport overflow");
    rt.idl_set_lamports_panicking(destination, total);
    rt.idl_set_lamports_panicking(source, 0);
    rt.idl_assign_system(source);
    named(rt.idl_realloc_zero_filled(source, 0), "account")
}

pub fn dispatch170<R: IdlRuntime>(rt: &mut R, program: &Key, accounts: &[Account], raw_args: &[u8]) -> I<()> {
    let instruction = decode(raw_args)?;
    let mut c = Cursor::new(accounts); // extra accounts are not rejected.
    match instruction {
        Instruction::Create(size) => {
            let (from,to,base,system,executable) = admit_create(rt,&mut c,program)?;
            create(rt,program,from,to,base,system,executable,size)
        }
        Instruction::CreateBuffer => {
            let (mut buffer,authority) = admit_buffer(rt,&mut c)?;
            rt.log_instruction("Instruction: IdlCreateBuffer");
            buffer.value.authority = authority.key; // no forced data_len reset.
            exit_header(rt,program,&buffer,"buffer")
        }
        Instruction::Write(bytes) => {
            let mut idl = admit_write(rt,&mut c)?; write(rt,&mut idl,&bytes)?;
            exit_header(rt,program,&idl,"idl")
        }
        Instruction::SetBuffer => {
            let (buffer,mut idl) = admit_set_buffer(rt,&mut c)?; set_buffer(rt,&buffer,&mut idl)?;
            exit_header(rt,program,&buffer,"buffer")?;
            exit_header(rt,program,&idl,"idl") // W208 persists buffer BEFORE idl.
        }
        Instruction::SetAuthority(key) => {
            let mut idl = admit_write(rt,&mut c)?;
            rt.log_instruction("Instruction: IdlSetAuthority"); idl.value.authority = key;
            exit_header(rt,program,&idl,"idl") // zero key is permitted (erases authority).
        }
        Instruction::Close => {
            let (account,destination) = admit_close(rt,&mut c)?; close(rt,account.info,destination)
        }
        Instruction::Resize(size) => {
            let (idl,authority,system) = admit_resize(rt,&mut c)?; resize(rt,&idl,authority,system,size)?;
            exit_header(rt,program,&idl,"idl")
        }
    }
    // No event/log_data/self-CPI event/return-data serialization in170.
}
