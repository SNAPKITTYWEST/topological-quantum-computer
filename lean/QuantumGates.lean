-- Gate names and resource costs mirrored by the Python topological backend.

namespace QuantumGates

inductive QIRGate where
  | X
  | H
  | S
  | T
  | CX
  | CCX
  | ROTR
  | SHR
  deriving Repr, DecidableEq

def braidCost : QIRGate -> Nat
  | .X => 2
  | .H => 5
  | .S => 2
  | .T => 300
  | .CX => 5
  | .CCX => 16
  | .ROTR => 0
  | .SHR => 0

theorem rotr_is_wire_accounting :
    braidCost QIRGate.ROTR = 0 := by
  rfl

theorem ccx_cost_is_declared :
    braidCost QIRGate.CCX = 16 := by
  rfl

end QuantumGates
