//! Uncompiled natural source proposal. Runtime and diagnostic boundaries explicit.
pub mod model; pub mod codec; pub mod runtime; pub mod arithmetic; pub mod handlers;
pub mod mint_policy; pub mod generated_exit; pub mod dispatch; pub mod dispatch_interfaces;
pub mod admission; pub mod frames;
pub mod idl; pub mod idl_runtime; pub mod solana_runtime; pub mod error_report;
#[cfg(not(target_os = "solana"))]
compile_error!("Relay proposal requires a real SBF loader/syscall target; host success stubs are disabled");
#[cfg(target_os = "solana")]
pub mod entrypoint;
pub use model::*;
#[derive(Debug)]
pub enum Error { Code(u32), IncorrectProgramId, Incomplete(&'static str), Program(solana_program::program_error::ProgramError), Owned(generated_exit::exit_error::Error) }
pub type R<T> = Result<T, Error>;
pub fn require(ok:bool,code:u32)->R<()> {if ok {Ok(())} else {Err(Error::Code(code))}}
pub fn overflow()->Error {Error::Code(6008)}
