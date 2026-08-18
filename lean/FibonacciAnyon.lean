-- Fibonacci anyon category surface for the staged repository.

namespace FibonacciAnyon

inductive Charge where
  | one
  | tau
  deriving Repr, DecidableEq

def fusion : Charge -> Charge -> List Charge
  | .one, .one => [.one]
  | .one, .tau => [.tau]
  | .tau, .one => [.tau]
  | .tau, .tau => [.one, .tau]

def fib : Nat -> Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n

def fusionDimVacuum (n : Nat) : Nat := fib (n - 1)

def fusionDimTau (n : Nat) : Nat := fib n

theorem tau_tau_fusion :
    fusion Charge.tau Charge.tau = [Charge.one, Charge.tau] := by
  rfl

theorem four_tau_vacuum_dim :
    fusionDimVacuum 4 = 2 := by
  rfl

end FibonacciAnyon
