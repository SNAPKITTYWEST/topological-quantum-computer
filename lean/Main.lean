-- Topological Quantum Computer staged formal surface.

namespace TopologicalQC

def sha520DigestBits : Nat := 520
def sha520DigestBytes : Nat := 65
def sha520BlockBits : Nat := 1024
def sha520RoundsFull : Nat := 80

def stagedReleaseVersion : String := "1.0.1"

theorem digest_byte_accounting :
    sha520DigestBytes * 8 = sha520DigestBits := by
  rfl

theorem block_size_declared :
    sha520BlockBits = 1024 := by
  rfl

theorem full_round_count_declared :
    sha520RoundsFull = 80 := by
  rfl

end TopologicalQC
