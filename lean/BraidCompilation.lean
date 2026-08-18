-- Braid-word surfaces used by the resource backend.

namespace BraidCompilation

structure BraidOp where
  sigma : Nat
  forward : Bool
  deriving Repr, DecidableEq

def op (sigma : Nat) : BraidOp := { sigma := sigma, forward := true }

def H : List BraidOp := [op 0, op 1, op 0, op 1, op 0]

def X : List BraidOp := [op 0, op 0]

def S : List BraidOp := [op 0, op 0]

def CNOT : List BraidOp := [op 2, op 1, op 0, op 1, op 2]

def CCX : List BraidOp :=
  [op 4, op 5, op 4, op 5, op 4,
   op 2, op 3, op 4, op 2, op 3, op 4,
   op 4, op 5, op 4, op 5, op 4]

def invertOp (b : BraidOp) : BraidOp := { b with forward := !b.forward }

def invertWord (word : List BraidOp) : List BraidOp :=
  word.reverse.map invertOp

theorem cnot_braid_length : CNOT.length = 5 := by
  rfl

theorem ccx_braid_length : CCX.length = 16 := by
  rfl

end BraidCompilation
