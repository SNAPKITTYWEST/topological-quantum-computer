-- Logical qubit encodings for Fibonacci anyon accounting.

namespace LogicalQubits

inductive TotalCharge where
  | vacuum
  | tau
  deriving Repr, DecidableEq

structure Encoding where
  name : String
  physicalAnyons : Nat
  logicalQubits : Nat
  totalCharge : TotalCharge
  deriving Repr

def threeTau : Encoding :=
  { name := "3-tau", physicalAnyons := 3, logicalQubits := 1, totalCharge := .tau }

def fourTau : Encoding :=
  { name := "4-tau", physicalAnyons := 4, logicalQubits := 1, totalCharge := .vacuum }

def physicalAnyonsForLogical (logicalQubits : Nat) (withAncilla : Bool) : Nat :=
  logicalQubits * if withAncilla then 10 else 4

theorem four_tau_uses_four_anyons :
    fourTau.physicalAnyons = 4 := by
  rfl

theorem one_logical_with_minimal_encoding :
    physicalAnyonsForLogical 1 false = 4 := by
  rfl

end LogicalQubits
