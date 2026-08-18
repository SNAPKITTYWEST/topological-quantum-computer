# Experimental Validation Protocol: Four Phases

## Phase 1: Classical Validation (Week 1-2)

**Objective:** Verify SHA-520-r reference implementation

### Tests
- SHA-520-4, 8, 12, 16, 80 test vectors
- Brute-force preimage (r=4, 16-bit: expect 2^16 trials)
- Birthday collision (r=4: expect 2^8 trials)

### Success Criteria
- ✓ Test vectors match the repository SHA-520-r reference implementation
- ✓ Brute-force in ~2^target_bits trials
- ✓ Collision in ~2^(target_bits/2) trials

---

## Phase 2: Quantum Simulation (Week 3-4)

**Objective:** Run Grover on reduced-round SHA-520

### Tests
- Toy SHA-520-4 (16-bit) noiseless
- Toy SHA-520-4 (16-bit) with noise
- SHA-520-4 (32-bit truncated)

### Success Criteria
- ✓ Noiseless success ≥ 80%
- ✓ Noisy success ≥ 50%
- ✓ Depth estimate ±20%

---

## Phase 3: Resource Validation (Week 5)

**Objective:** Validate Solovay-Kitaev compilation overhead

### Tests
- Compare estimated vs. actual T-gates
- Compare estimated vs. actual depth
- Check braid scaling (polynomial)

### Success Criteria
- ✓ T-gates within ±15%
- ✓ Depth within ±20%
- ✓ Max deviation < 20%

---

## Phase 4: Topological Compilation (Theory)

**Objective:** Generate braid sequences and verify scaling

### Tests
- Compile r=4,8,12,16 circuits to braids
- Verify L(ε) ∝ poly(log(1/ε))
- Generate adiabatic schedules

### Success Criteria
- ✓ Braids scale poly in log(1/ε)
- ✓ Time < 1 ms per iteration
- ✓ No physical anyons created

*Protocols frozen. Criteria locked. No ad-hoc testing.*
