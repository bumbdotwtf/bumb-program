use crate::*;
use crate::generated_exit::exit_error::{self, Error as OwnedError};
// 97/98/100: checked u32 accumulator. This is a handler gate, not helper113 policy.
pub fn admit_weights(shares:&[Share])->R<()> {
 let mut sum=0u32;
 for s in shares {sum=sum.checked_add(u32::from(s.bps)).ok_or_else(overflow)?;}
 require(sum==10000,6022)
}
// Successful value contract of113 under the CALLER's already admitted sum=10000.
// Stable library sort is a natural hypothesis, not historical allocation/sort identity.
// No public arbitrary-weight helper contract is claimed.
pub(crate) fn fair_amounts(total:u64,weights:&[u16])->Result<Vec<u64>,OwnedError> {
 let mut amounts=Vec::with_capacity(weights.len());let mut remainders=Vec::with_capacity(weights.len());let mut allocated=0u64;
 for (i,&bps) in weights.iter().enumerate() {
  let product=u128::from(total)*u128::from(bps);
  let q=(product/10000) as u64;amounts.push(q);
  remainders.push((i,product%10000));
  allocated=allocated.checked_add(q).ok_or_else(exit_error::arithmetic_overflow)?;
 }
 let left=total.checked_sub(allocated).ok_or_else(exit_error::arithmetic_overflow)?;
 if left!=0 {
  // Stable decreasing remainder; equal keys retain original occurrence order.
  remainders.sort_by(|a,b|b.1.cmp(&a.1));
  for (i,_) in remainders.into_iter().take(left as usize) {
   amounts[i]=amounts[i].checked_add(1).ok_or_else(exit_error::arithmetic_overflow)?;
  }
 }
 Ok(amounts)
}
