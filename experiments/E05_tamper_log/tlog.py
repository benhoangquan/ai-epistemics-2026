"""Cryptographic core for E05: RFC 6962 Merkle tree hashing, inclusion and consistency proofs
(proofs per RFC 6962 §2.1, verification per RFC 9162 §2.1.3.2 and §2.1.4.2), Ed25519 signatures,
signed checkpoints and an external witness.

Ed25519 comes from `cryptography` when it is importable (`uv run --with cryptography ...`).
Otherwise the pure-Python reference implementation from RFC 8032 §6 is used, which is slow but
exact. The tests check both backends against the RFC 8032 test vectors.
"""
from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field

# ----------------------------------------------------------------------------- canonical bytes


def canon(obj) -> bytes:
    """Canonical JSON (sorted keys, no whitespace, UTF-8). Stand-in for RFC 8785 JCS."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def leaf_hash(data: bytes) -> bytes:
    """RFC 6962: MTH({d}) = SHA-256(0x00 || d)."""
    return sha256(b"\x00" + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 6962: interior node = SHA-256(0x01 || left || right)."""
    return sha256(b"\x01" + left + right)


EMPTY_ROOT = sha256(b"")

# ----------------------------------------------------------------------------- Merkle tree (RFC 6962 §2.1)


def _split(n: int) -> int:
    """Largest power of two strictly less than n (n >= 2)."""
    k = 1
    while k << 1 < n:
        k <<= 1
    return k


def mth(leaves: list[bytes]) -> bytes:
    """Merkle Tree Hash over already-hashed leaves (each leaf is leaf_hash(entry))."""
    n = len(leaves)
    if n == 0:
        return EMPTY_ROOT
    if n == 1:
        return leaves[0]
    k = _split(n)
    return node_hash(mth(leaves[:k]), mth(leaves[k:]))


def inclusion_proof(m: int, leaves: list[bytes]) -> list[bytes]:
    """PATH(m, D[n]) from RFC 6962 §2.1.1."""
    n = len(leaves)
    if not 0 <= m < n:
        raise ValueError("leaf index out of range")
    if n == 1:
        return []
    k = _split(n)
    if m < k:
        return inclusion_proof(m, leaves[:k]) + [mth(leaves[k:])]
    return inclusion_proof(m - k, leaves[k:]) + [mth(leaves[:k])]


def consistency_proof(m: int, leaves: list[bytes]) -> list[bytes]:
    """PROOF(m, D[n]) from RFC 6962 §2.1.2, for 0 < m <= n."""
    n = len(leaves)
    if not 0 < m <= n:
        raise ValueError("bad consistency range")
    return _subproof(m, leaves, True)


def _subproof(m: int, leaves: list[bytes], b: bool) -> list[bytes]:
    n = len(leaves)
    if m == n:
        return [] if b else [mth(leaves)]
    k = _split(n)
    if m <= k:
        return _subproof(m, leaves[:k], b) + [mth(leaves[k:])]
    return _subproof(m - k, leaves[k:], False) + [mth(leaves[:k])]


def verify_inclusion(index: int, size: int, leaf: bytes, proof: list[bytes], root: bytes) -> bool:
    """RFC 9162 §2.1.3.2."""
    if index >= size or index < 0:
        return False
    fn, sn, r = index, size - 1, leaf
    for p in proof:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            r = node_hash(p, r)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            r = node_hash(r, p)
        fn >>= 1
        sn >>= 1
    return sn == 0 and r == root


def verify_consistency(first: int, second: int, first_root: bytes, second_root: bytes, proof: list[bytes]) -> bool:
    """RFC 9162 §2.1.4.2 (with the trivial cases first == 0 and first == second)."""
    if first > second or first < 0:
        return False
    if first == 0:
        return not proof
    if first == second:
        return not proof and first_root == second_root
    if not proof:
        return False
    path = list(proof)
    if first & (first - 1) == 0:  # exact power of two
        path = [first_root] + path
    fn, sn = first - 1, second - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    fr = sr = path[0]
    for c in path[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr = node_hash(c, fr)
            sr = node_hash(c, sr)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            sr = node_hash(sr, c)
        fn >>= 1
        sn >>= 1
    return fr == first_root and sr == second_root and sn == 0


# ----------------------------------------------------------------------------- Ed25519

try:  # fast path
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature

    BACKEND = "cryptography"
except ImportError:  # pragma: no cover - exercised by the plain `uv run --group dev pytest`
    BACKEND = "pure-python"


class _Ref:
    """RFC 8032 §6 reference implementation of Ed25519 (pure Python)."""

    p = 2**255 - 19
    d = -121665 * pow(121666, p - 2, p) % p
    q = 2**252 + 27742317777372353535851937790883648493
    sqrt_m1 = pow(2, (p - 1) // 4, p)

    @classmethod
    def add(cls, P, Q):
        p, d = cls.p, cls.d
        A, B = (P[1] - P[0]) * (Q[1] - Q[0]) % p, (P[1] + P[0]) * (Q[1] + Q[0]) % p
        C, D = 2 * P[3] * Q[3] * d % p, 2 * P[2] * Q[2] % p
        E, F, G, H = B - A, D - C, D + C, B + A
        return (E * F, G * H, F * G, E * H)

    @classmethod
    def mul(cls, s, P):
        Q = (0, 1, 1, 0)
        while s > 0:
            if s & 1:
                Q = cls.add(Q, P)
            P = cls.add(P, P)
            s >>= 1
        return Q

    @classmethod
    def equal(cls, P, Q):
        p = cls.p
        return (P[0] * Q[2] - Q[0] * P[2]) % p == 0 and (P[1] * Q[2] - Q[1] * P[2]) % p == 0

    @classmethod
    def recover_x(cls, y, sign):
        p, d = cls.p, cls.d
        if y >= p:
            return None
        x2 = (y * y - 1) * pow(d * y * y + 1, p - 2, p)
        if x2 == 0:
            return None if sign else 0
        x = pow(x2, (p + 3) // 8, p)
        if (x * x - x2) % p != 0:
            x = x * cls.sqrt_m1 % p
        if (x * x - x2) % p != 0:
            return None
        if (x & 1) != sign:
            x = p - x
        return x

    @classmethod
    def G(cls):
        p = cls.p
        gy = 4 * pow(5, p - 2, p) % p
        gx = cls.recover_x(gy, 0)
        return (gx, gy, 1, gx * gy % p)

    @classmethod
    def compress(cls, P):
        p = cls.p
        zinv = pow(P[2], p - 2, p)
        x, y = P[0] * zinv % p, P[1] * zinv % p
        return int.to_bytes(y | ((x & 1) << 255), 32, "little")

    @classmethod
    def decompress(cls, s):
        if len(s) != 32:
            return None
        y = int.from_bytes(s, "little")
        sign = y >> 255
        y &= (1 << 255) - 1
        x = cls.recover_x(y, sign)
        return None if x is None else (x, y, 1, x * y % cls.p)

    @staticmethod
    def expand(secret):
        h = hashlib.sha512(secret).digest()
        a = int.from_bytes(h[:32], "little")
        a &= (1 << 254) - 8
        a |= 1 << 254
        return a, h[32:]

    @classmethod
    def public(cls, secret):
        a, _ = cls.expand(secret)
        return cls.compress(cls.mul(a, cls.G()))

    @classmethod
    def sign(cls, secret, msg):
        a, prefix = cls.expand(secret)
        G = cls.G()
        A = cls.compress(cls.mul(a, G))
        r = int.from_bytes(hashlib.sha512(prefix + msg).digest(), "little") % cls.q
        Rs = cls.compress(cls.mul(r, G))
        h = int.from_bytes(hashlib.sha512(Rs + A + msg).digest(), "little") % cls.q
        s = (r + h * a) % cls.q
        return Rs + int.to_bytes(s, 32, "little")

    @classmethod
    def verify(cls, public, msg, sig):
        if len(public) != 32 or len(sig) != 64:
            return False
        A = cls.decompress(public)
        R = cls.decompress(sig[:32])
        if not A or not R:
            return False
        s = int.from_bytes(sig[32:], "little")
        if s >= cls.q:
            return False
        h = int.from_bytes(hashlib.sha512(sig[:32] + public + msg).digest(), "little") % cls.q
        G = cls.G()
        return cls.equal(cls.mul(s, G), cls.add(R, cls.mul(h, A)))


_VERIFY_CACHE: dict[tuple, bool] = {}


class Signer:
    """An Ed25519 key. `seed` is the 32-byte RFC 8032 secret; derive it from a name for reproducibility."""

    def __init__(self, seed: bytes, backend: str | None = None):
        assert len(seed) == 32
        self.seed = seed
        self.backend = backend or BACKEND
        if self.backend == "cryptography":
            self._sk = Ed25519PrivateKey.from_private_bytes(seed)
            self.public = self._sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        else:
            self.public = _Ref.public(seed)

    @classmethod
    def from_name(cls, name: str, backend: str | None = None) -> "Signer":
        return cls(sha256(b"E05-key:" + name.encode()), backend)

    def sign(self, msg: bytes) -> bytes:
        if self.backend == "cryptography":
            return self._sk.sign(msg)
        return _Ref.sign(self.seed, msg)


def verify_sig(public: bytes, msg: bytes, sig: bytes, backend: str | None = None) -> bool:
    backend = backend or BACKEND
    key = (public, msg, sig, backend)
    if key in _VERIFY_CACHE:
        return _VERIFY_CACHE[key]
    if backend == "cryptography":
        try:
            Ed25519PublicKey.from_public_bytes(public).verify(sig, msg)
            ok = True
        except (InvalidSignature, ValueError):
            ok = False
    else:
        ok = _Ref.verify(public, msg, sig)
    _VERIFY_CACHE[key] = ok
    return ok


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def unb64(s: str) -> bytes:
    return base64.b64decode(s)


# ----------------------------------------------------------------------------- checkpoints and witness


def checkpoint_note(origin: str, size: int, root: bytes, closed: bool) -> bytes:
    """Signed-note body in the style of C2SP tlog-checkpoint, plus a session-closed flag."""
    return f"{origin}\n{size}\n{b64(root)}\n{'closed' if closed else 'open'}\n".encode()


def make_checkpoint(signer: Signer, origin: str, size: int, root: bytes, closed: bool = False) -> dict:
    note = checkpoint_note(origin, size, root, closed)
    return {"origin": origin, "size": size, "root": root.hex(), "closed": closed, "sig": b64(signer.sign(note))}


def checkpoint_valid(cp: dict, public: bytes) -> bool:
    note = checkpoint_note(cp["origin"], cp["size"], bytes.fromhex(cp["root"]), cp["closed"])
    return verify_sig(public, note, unb64(cp["sig"]))


@dataclass
class Witness:
    """External witness: accepts a checkpoint only if it is signed by the registered log key and is
    consistent with the last checkpoint it accepted for that origin. Cosigns what it accepts and keeps
    any conflicting checkpoint as equivocation evidence. The agent cannot rewrite its history."""

    signer: Signer
    keys: dict = field(default_factory=dict)  # origin -> log public key
    history: dict = field(default_factory=dict)  # origin -> [ {checkpoint, proof_from_prev, cosig} ]
    evidence: list = field(default_factory=list)

    def register(self, origin: str, public: bytes) -> None:
        self.keys[origin] = public

    def submit(self, cp: dict, proof: list[bytes]) -> bool:
        origin = cp["origin"]
        if origin not in self.keys or not checkpoint_valid(cp, self.keys[origin]):
            self.evidence.append({"kind": "bad_signature", "checkpoint": cp})
            return False
        hist = self.history.setdefault(origin, [])
        if hist:
            prev = hist[-1]["checkpoint"]
            root, proot = bytes.fromhex(cp["root"]), bytes.fromhex(prev["root"])
            if prev["closed"] and (cp["size"] != prev["size"] or cp["root"] != prev["root"]):
                self.evidence.append({"kind": "append_after_close", "checkpoint": cp, "previous": prev})
                return False
            if cp["size"] < prev["size"]:
                self.evidence.append({"kind": "rollback", "checkpoint": cp, "previous": prev})
                return False
            if not verify_consistency(prev["size"], cp["size"], proot, root, proof):
                self.evidence.append({"kind": "inconsistent", "checkpoint": cp, "previous": prev})
                return False
        cosig = b64(self.signer.sign(canon(cp)))
        hist.append({"checkpoint": cp, "proof": [p.hex() for p in proof], "cosig": cosig})
        return True

    def view(self, origin: str) -> dict:
        """What an auditor fetches from the witness for one log."""
        return {
            "checkpoints": [dict(h) for h in self.history.get(origin, [])],
            "evidence": [e for e in self.evidence if e["checkpoint"]["origin"] == origin],
            "public": self.signer.public,
        }
