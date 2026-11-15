"""Recorder side of E05: OTel GenAI-shaped spans for a tool-using agent run, the hash-chained
transparency-log recorder, and the counterparties (cosigning tool servers, the LLM provider's usage
records).

A *trace* (from gen_traces.py) is a dict:
    {id, domain, agent_name, model, system, user, final, markers, benign,
     steps: [{tool, server, args (dict), result (str), forbidden (bool)}]}
`server` is "local" (a tool on the agent's own host, no counterparty) or a host name of a cooperating
tool server that cosigns its responses and keeps a call log.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field

import tlog
from tlog import Signer, Witness, canon, leaf_hash, sha256

K_DEFAULT = 4
PROVIDER = "adaption"  # gen_ai.provider.name value used in the synthetic traces
RECEIPT_ATTR = "tamperlog.receipt"  # our extension attribute; the GenAI semconv has no integrity attributes

# ----------------------------------------------------------------------------- token accounting


def ntok(text: str) -> int:
    """Stand-in tokenizer: whitespace word count. Provider and auditor use the same function."""
    return len(str(text).split())


def render_call(name: str, args) -> str:
    return f"{name} {json.dumps(args, sort_keys=True)}"


def args_of(v):
    """gen_ai.tool.call.arguments is stored as a JSON string; accept dicts from tamperers too."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


# ----------------------------------------------------------------------------- span construction


def _hex(seed: str, n: int) -> str:
    return sha256(seed.encode()).hex()[:n]


def build_spans(trace: dict) -> list[dict]:
    """Deterministic OTel GenAI spans in export order (a span is exported when it ends, so the root
    `invoke_agent` span comes last). Token counts follow ntok()."""
    tid = _hex("trace:" + trace["id"], 32)
    root_id = _hex(f"span:{trace['id']}:root", 16)
    conv = f"conv_{trace['id']}"
    model = trace.get("model", "gemma-4-26b-a4b-it")
    t0 = 1_763_100_000_000_000_000  # 2025-11-14T05:20Z in ns; only differences matter
    sec = 1_000_000_000
    spans: list[dict] = []
    ctx_tokens = ntok(trace["system"]) + ntok(trace["user"])
    t = t0 + sec
    for i, st in enumerate(trace["steps"] + [None]):
        rid = f"resp_{trace['id']}_{i}"
        if st is None:
            out = [{"role": "assistant", "parts": [{"type": "text", "content": trace["final"]}]}]
            out_tok, finish = ntok(trace["final"]), ["stop"]
        else:
            call_id = f"call_{trace['id']}_{i}"
            out = [{"role": "assistant", "parts": [{"type": "tool_call", "id": call_id, "name": st["tool"],
                                                    "arguments": st["args"]}]}]
            out_tok, finish = ntok(render_call(st["tool"], st["args"])), ["tool_call"]
        spans.append({
            "trace_id": tid, "span_id": _hex(f"span:{trace['id']}:chat{i}", 16), "parent_span_id": root_id,
            "name": f"chat {model}", "kind": "CLIENT", "start_time": t, "end_time": t + 2 * sec,
            "attributes": {
                "gen_ai.operation.name": "chat", "gen_ai.provider.name": PROVIDER,
                "gen_ai.request.model": model, "gen_ai.response.model": model, "gen_ai.response.id": rid,
                "gen_ai.conversation.id": conv, "gen_ai.usage.input_tokens": ctx_tokens,
                "gen_ai.usage.output_tokens": out_tok, "gen_ai.response.finish_reasons": finish,
                "gen_ai.output.messages": out,
            },
        })
        t += 3 * sec
        if st is None:
            break
        ctx_tokens += out_tok
        spans.append({
            "trace_id": tid, "span_id": _hex(f"span:{trace['id']}:tool{i}", 16), "parent_span_id": root_id,
            "name": f"execute_tool {st['tool']}", "kind": "INTERNAL", "start_time": t, "end_time": t + sec,
            "attributes": {
                "gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": st["tool"],
                "gen_ai.tool.call.id": call_id, "gen_ai.tool.type": "function",
                "gen_ai.tool.call.arguments": json.dumps(st["args"], sort_keys=True),
                "gen_ai.tool.call.result": st["result"], "gen_ai.conversation.id": conv,
                "server.address": st["server"],
            },
        })
        ctx_tokens += ntok(st["result"])
        t += 2 * sec
    spans.append({
        "trace_id": tid, "span_id": root_id, "parent_span_id": None, "name": f"invoke_agent {trace['agent_name']}",
        "kind": "INTERNAL", "start_time": t0, "end_time": t,
        "attributes": {
            "gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": trace["agent_name"],
            "gen_ai.conversation.id": conv, "gen_ai.provider.name": PROVIDER, "gen_ai.request.model": model,
            "gen_ai.system_instructions": [{"type": "text", "content": trace["system"]}],
            "gen_ai.input.messages": [{"role": "user", "parts": [{"type": "text", "content": trace["user"]}]}],
        },
    })
    return spans


def forbidden_span_indices(trace: dict) -> tuple[int, int]:
    """(chat span index, execute_tool span index) of the forbidden step in build_spans order."""
    s = next(i for i, st in enumerate(trace["steps"]) if st["forbidden"])
    return 2 * s, 2 * s + 1


# ----------------------------------------------------------------------------- counterparties


@dataclass
class ToolServer:
    """A cooperating tool server (e.g. an MCP server): it signs a receipt over each response and keeps
    its own call log. The agent cannot forge receipts or edit this log."""

    address: str
    signer: Signer
    log: list = field(default_factory=list)
    seq: dict = field(default_factory=dict)

    def call(self, session: str, call_id: str, tool: str, args_json: str, result: str) -> dict:
        n = self.seq.get(session, 0)
        self.seq[session] = n + 1
        body = {"server": self.address, "session": session, "server_seq": n, "call_id": call_id, "tool": tool,
                "args_sha256": sha256(args_json.encode()).hex(), "result_sha256": sha256(result.encode()).hex()}
        receipt = dict(body, sig=tlog.b64(self.signer.sign(canon(body))))
        self.log.append(body)
        return receipt


def receipt_valid(receipt: dict, public: bytes) -> bool:
    body = {k: v for k, v in receipt.items() if k != "sig"}
    try:
        return tlog.verify_sig(public, canon(body), tlog.unb64(receipt["sig"]))
    except Exception:
        return False


@dataclass
class World:
    """Everything outside the agent's control for one session: tool servers, the provider's usage
    records, the witness and the public keys an auditor knows."""

    session: str
    servers: dict  # address -> ToolServer
    provider: list = field(default_factory=list)  # [{response_id, model, input_tokens, output_tokens}]
    witness: Witness = None
    log_signer: Signer = None  # held by the agent's recorder (so the agent can re-sign)

    @property
    def origin(self) -> str:
        return f"tamperlog/{self.session}"


def make_world(trace: dict, cooperating: set[str]) -> World:
    session = trace["id"]
    servers = {a: ToolServer(a, Signer.from_name("server:" + a)) for a in sorted(cooperating)}
    w = World(session, servers, [], Witness(Signer.from_name("witness")), Signer.from_name("log:" + session))
    w.witness.register(w.origin, w.log_signer.public)
    return w


def execute_true_events(trace: dict, spans: list[dict], world: World) -> list[dict]:
    """Play the *true* run against the counterparties: every chat call is billed by the provider and
    every call to a cooperating server is logged and cosigned there, whatever the agent later logs.
    Returns the honest spans with receipts attached."""
    spans = copy.deepcopy(spans)
    for sp in spans:
        a = sp["attributes"]
        if a["gen_ai.operation.name"] == "chat":
            world.provider.append({"response_id": a["gen_ai.response.id"], "model": a["gen_ai.response.model"],
                                   "input_tokens": a["gen_ai.usage.input_tokens"],
                                   "output_tokens": a["gen_ai.usage.output_tokens"]})
        elif a["gen_ai.operation.name"] == "execute_tool" and a["server.address"] in world.servers:
            srv = world.servers[a["server.address"]]
            a[RECEIPT_ATTR] = srv.call(world.session, a["gen_ai.tool.call.id"], a["gen_ai.tool.name"],
                                       a["gen_ai.tool.call.arguments"], a["gen_ai.tool.call.result"])
    return spans


# ----------------------------------------------------------------------------- the recorder


class Recorder:
    """Tamper-evident span exporter core: hash-chains every emitted span (RFC 6962 leaf hashes) and
    publishes a signed Merkle checkpoint to the witness every k spans and when the session closes.
    `on_emit` lets a caller observe each emission (used to simulate live tampering)."""

    def __init__(self, world: World, k: int = K_DEFAULT):
        self.world, self.k = world, k
        self.entries: list[dict] = []
        self.leaves: list[bytes] = []
        self.published: list[dict] = []

    def emit(self, span: dict) -> None:
        prev = self.leaves[-1].hex() if self.leaves else "00" * 32
        entry = {"seq": len(self.entries), "prev": prev, "span": span}
        self.entries.append(entry)
        self.leaves.append(leaf_hash(canon(entry)))
        if self.k and len(self.entries) % self.k == 0:
            self.checkpoint()

    def checkpoint(self, closed: bool = False) -> None:
        n = len(self.entries)
        cp = tlog.make_checkpoint(self.world.log_signer, self.world.origin, n, tlog.mth(self.leaves), closed)
        last = self.published[-1]["size"] if self.published else 0
        proof = tlog.consistency_proof(last, self.leaves) if 0 < last < n else []
        self.world.witness.submit(cp, proof)
        self.published.append(cp)

    def close(self) -> None:
        self.checkpoint(closed=True)


def chain_entries(spans: list[dict]) -> list[dict]:
    """Recompute seq/prev for a list of spans (what a tamperer does when it 'rehashes')."""
    out, prev = [], "00" * 32
    for i, sp in enumerate(spans):
        e = {"seq": i, "prev": prev, "span": sp}
        out.append(e)
        prev = leaf_hash(canon(e)).hex()
    return out


def record(world: World, spans: list[dict], k: int = K_DEFAULT) -> dict:
    """Record a span stream honestly and return the agent's presented bundle."""
    rec = Recorder(world, k)
    for sp in spans:
        rec.emit(sp)
    rec.close()
    return {"entries": rec.entries, "agent_checkpoints": rec.published}


def honest_session(trace: dict, cooperating: set[str], k: int = K_DEFAULT):
    """Run the true session. Returns (world, true_spans_with_receipts, presented_bundle)."""
    world = make_world(trace, cooperating)
    true_spans = execute_true_events(trace, build_spans(trace), world)
    return world, true_spans, record(world, true_spans, k)


def committed_prefix(n_emitted: int, k: int) -> int:
    """How many spans are already covered by a published checkpoint right after n_emitted spans were
    recorded (publication is synchronous on every k-th span)."""
    return (n_emitted // k) * k if k else 0
