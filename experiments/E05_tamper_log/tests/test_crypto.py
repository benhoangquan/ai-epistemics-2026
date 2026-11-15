"""Unit tests for the RFC 6962 / RFC 9162 Merkle code, Ed25519 and the witness."""
import itertools

import pytest

import tlog
from tlog import (Signer, Witness, consistency_proof, inclusion_proof, leaf_hash, mth, node_hash, verify_consistency,
                  verify_inclusion)


def leaves(n):
    return [leaf_hash(f"entry {i}".encode()) for i in range(n)]


def naive_root(ls):
    """Independent MTH: split at the largest power of two below n, as in RFC 6962 §2.1."""
    if not ls:
        return tlog.sha256(b"")
    if len(ls) == 1:
        return ls[0]
    k = 1
    while k * 2 < len(ls):
        k *= 2
    return node_hash(naive_root(ls[:k]), naive_root(ls[k:]))


def test_domain_separation_prefixes():
    assert leaf_hash(b"x") == tlog.sha256(b"\x00x")
    assert node_hash(b"a", b"b") == tlog.sha256(b"\x01ab")
    assert mth([]) == tlog.sha256(b"")


def test_known_rfc6962_empty_and_single():
    # SHA-256("") and SHA-256(0x00) are the CT test vectors for the empty tree and the empty leaf
    assert mth([]).hex() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert leaf_hash(b"").hex() == "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d"


@pytest.mark.parametrize("n", range(1, 18))
def test_root_matches_naive(n):
    assert mth(leaves(n)) == naive_root(leaves(n))


def test_inclusion_all_positions():
    for n in range(1, 18):
        ls = leaves(n)
        root = mth(ls)
        for m in range(n):
            p = inclusion_proof(m, ls)
            assert verify_inclusion(m, n, ls[m], p, root)
            assert not verify_inclusion(m, n, leaf_hash(b"forged"), p, root)
            if p:
                bad = list(p)
                bad[0] = tlog.sha256(b"x")
                assert not verify_inclusion(m, n, ls[m], bad, root)
            assert not verify_inclusion(m, n, ls[m], p, tlog.sha256(b"other root"))


def test_consistency_all_pairs():
    for n in range(1, 18):
        ls = leaves(n)
        for m in range(1, n + 1):
            p = consistency_proof(m, ls)
            assert verify_consistency(m, n, mth(ls[:m]), mth(ls), p), (m, n)
            # a rewritten history of the first m entries must not verify
            forged = [leaf_hash(b"rewritten")] + ls[1:]
            if m < n:
                assert not verify_consistency(m, n, mth(forged[:m]), mth(ls), p)
                assert not verify_consistency(m, n, mth(ls[:m]), mth(forged), p)


def test_consistency_rejects_shrinking():
    ls = leaves(8)
    assert not verify_consistency(8, 4, mth(ls), mth(ls[:4]), [])


RFC8032 = [  # (secret, public, message, signature) from RFC 8032 §7.1, TEST 1 and TEST 2
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
     "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
     "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
]

BACKENDS = ["pure-python"] + (["cryptography"] if tlog.BACKEND == "cryptography" else [])


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("sk,pk,msg,sig", RFC8032)
def test_ed25519_rfc8032_vectors(backend, sk, pk, msg, sig):
    s = Signer(bytes.fromhex(sk), backend=backend)
    assert s.public.hex() == pk
    assert s.sign(bytes.fromhex(msg)).hex() == sig
    assert tlog.verify_sig(bytes.fromhex(pk), bytes.fromhex(msg), bytes.fromhex(sig), backend=backend)
    assert not tlog.verify_sig(bytes.fromhex(pk), bytes.fromhex(msg) + b"!", bytes.fromhex(sig), backend=backend)


def _grow(witness, signer, origin, ls, sizes, closed_last=True):
    last = 0
    for j, s in enumerate(sizes):
        cp = tlog.make_checkpoint(signer, origin, s, mth(ls[:s]), closed=closed_last and j == len(sizes) - 1)
        proof = consistency_proof(last, ls[:s]) if 0 < last < s else []
        assert witness.submit(cp, proof)
        last = s


def test_witness_accepts_growth_and_flags_equivocation():
    w, log = Witness(Signer.from_name("w")), Signer.from_name("log")
    w.register("o", log.public)
    ls = leaves(12)
    _grow(w, log, "o", ls, [4, 8], closed_last=False)
    forged = ls[:2] + [leaf_hash(b"evil")] + ls[3:]
    cp = tlog.make_checkpoint(log, "o", 12, mth(forged), False)
    assert not w.submit(cp, consistency_proof(8, forged))
    assert w.evidence and w.evidence[-1]["kind"] == "inconsistent"
    # a checkpoint signed by someone else is rejected too
    other = Signer.from_name("mallory")
    assert not w.submit(tlog.make_checkpoint(other, "o", 12, mth(ls), False), consistency_proof(8, ls))


def test_witness_rejects_rollback_and_append_after_close():
    w, log = Witness(Signer.from_name("w")), Signer.from_name("log")
    w.register("o", log.public)
    ls = leaves(9)
    _grow(w, log, "o", ls, [4, 8], closed_last=True)
    assert not w.submit(tlog.make_checkpoint(log, "o", 4, mth(ls[:4]), False), [])
    assert not w.submit(tlog.make_checkpoint(log, "o", 9, mth(ls), True), consistency_proof(8, ls))
    kinds = {e["kind"] for e in w.evidence}
    assert "append_after_close" in kinds
