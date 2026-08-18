import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from classical.sha520_ref import SHA520
from qlambda.arrays import SHA520_DIGEST_BYTES, SHA520_IV_520, SHA520_K_80, sha520_array_manifest
from qlambda.compiler import compile_source
from qlambda.license_policy import select_license
from qlambda.programs import SHA520_MESSAGE_SCHEDULE_WORD, SHA520_SIGMA0_AND_CH
from topological.braid_backend import TopologicalBraidBackend
from topological.resource_estimates import estimate_sha520_r_topological


def test_sha520_arrays_are_explicit():
    manifest = sha520_array_manifest()
    assert manifest["SHA520_IV_520"].length == 9
    assert manifest["SHA520_K_80"].length == 80
    assert len(SHA520_IV_520) == 9
    assert len(SHA520_K_80) == 80


def test_sha520_digest_is_520_bits():
    digest = SHA520(rounds=4).digest(b"abc")
    assert len(digest) == SHA520_DIGEST_BYTES


def test_qlambda_compiles_sigma_ch_and_schedule_add_shift():
    sigma_qir = compile_source(SHA520_SIGMA0_AND_CH)
    schedule_qir = compile_source(SHA520_MESSAGE_SCHEDULE_WORD)
    gates = {inst.gate for inst in sigma_qir + schedule_qir}
    assert "CX" in gates
    assert "CCX" in gates
    assert len(schedule_qir) > len(sigma_qir)


def test_topological_backend_and_resource_flags():
    qir = compile_source(SHA520_SIGMA0_AND_CH)
    braids = TopologicalBraidBackend().compile(qir[:10])
    assert len(braids) > 0
    estimate = estimate_sha520_r_topological(rounds=4, target_bits=16)
    assert estimate.physical_anyons == estimate.logical_qubits * 4
    assert "oracle_dominates" in estimate.falsification_flags


def test_license_policy_is_python_array_backed():
    assert select_license("saas_wrapper") == "agpl_3_0"
