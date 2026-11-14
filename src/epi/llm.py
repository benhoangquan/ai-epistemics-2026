"""Shared LLM client for every experiment: the Adaption Labs Responses API, with a disk cache,
a cross-process rate limiter and a global spend cap.

All processes on this machine share one SQLite file (.epi/llm.sqlite by default), so the
experiments running in parallel stay together under the API's per-user rate limit (about 50
requests a minute, measured 2026-11-14; a 429 says "retry after 60 seconds") and under the
spend caps set in .env.

    from epi.llm import complete, complete_many, parse_json
    c = complete("Is the sky green? Answer yes or no.", model="gemma-4-26b-a4b-it", tag="E02")
    c.text, c.cost, c.cached

Set EPI_BACKEND=mock to run without the API (deterministic fake text, nothing is spent).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://api.prod.adaptionlabs.ai/api/v1/responses"

# Models served by the key on 2026-11-14. Small, cheap models are good subjects; the two large
# ones cost roughly 100x more per token and suit judging.
SUBJECTS = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.8-27b", "deepseek-v4-flash", "glm-5.3-flash"]
JUDGES = ["glm-5.2", "qwen3.5-397b"]
REASONING_PREFIXES = ("qwen", "deepseek", "glm")  # these think before answering; "low" effort keeps that short


def _load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()

STATE_DIR = Path(os.environ.get("EPI_STATE_DIR", ROOT / ".epi"))
RPM = int(os.environ.get("EPI_RPM", "45"))
SPEND_CAP = float(os.environ.get("EPI_SPEND_CAP_USD", "50"))
TAG_CAP = float(os.environ.get("EPI_TAG_CAP_USD", "8"))
BACKEND = os.environ.get("EPI_BACKEND", "adaption")


class SpendCapReached(RuntimeError):
    """The global or per-tag spend cap is used up. Stop the run; do not retry."""


@dataclass
class Completion:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float  # USD charged for this call; 0.0 when served from cache
    cached: bool
    truncated: bool  # hit max_output_tokens; with reasoning models the text may be empty


_local = threading.local()


def _db() -> sqlite3.Connection:
    con = getattr(_local, "con", None)
    if con is None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(STATE_DIR / "llm.sqlite", timeout=60, isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=60000")
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, response TEXT, ts REAL);
            CREATE TABLE IF NOT EXISTS calls (ts REAL);
            CREATE INDEX IF NOT EXISTS calls_ts ON calls(ts);
            CREATE TABLE IF NOT EXISTS spend (ts REAL, tag TEXT, model TEXT, input INTEGER, output INTEGER,
                                              cost REAL, error TEXT);
            CREATE TABLE IF NOT EXISTS block (id INTEGER PRIMARY KEY CHECK (id = 1), until REAL);
            """
        )
        _local.con = con
    return con


def _acquire_slot() -> None:
    """Block until this process may send one request without exceeding RPM across all processes."""
    con = _db()
    while True:
        now = time.time()
        con.execute("BEGIN IMMEDIATE")
        try:
            row = con.execute("SELECT until FROM block WHERE id = 1").fetchone()
            if row and row[0] > now:
                wait = row[0] - now
            else:
                con.execute("DELETE FROM calls WHERE ts < ?", (now - 120,))
                n, oldest = con.execute("SELECT COUNT(*), MIN(ts) FROM calls WHERE ts > ?", (now - 60,)).fetchone()
                if n < RPM:
                    con.execute("INSERT INTO calls VALUES (?)", (now,))
                    con.execute("COMMIT")
                    return
                wait = oldest + 60 - now + 0.05
            con.execute("COMMIT")
        except BaseException:
            con.execute("ROLLBACK")
            raise
        time.sleep(min(max(wait, 0.05), 5.0) + random.random() * 0.25)


def _block_all(seconds: float) -> None:
    con = _db()
    until = time.time() + seconds
    con.execute(
        "INSERT INTO block (id, until) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET until = MAX(until, excluded.until)",
        (until,),
    )


def _record(tag: str, model: str, inp: int, out: int, cost: float, error: str | None = None) -> None:
    _db().execute("INSERT INTO spend VALUES (?, ?, ?, ?, ?, ?, ?)", (time.time(), tag, model, inp, out, cost, error))


def spent(tag: str | None = None) -> float:
    con = _db()
    if tag is None:
        return con.execute("SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]
    return con.execute("SELECT COALESCE(SUM(cost), 0) FROM spend WHERE tag = ?", (tag,)).fetchone()[0]


def _check_caps(tag: str) -> None:
    total, mine = spent(), spent(tag)
    if total >= SPEND_CAP:
        raise SpendCapReached(f"global spend cap reached: ${total:.2f} of ${SPEND_CAP:.2f}")
    if mine >= TAG_CAP:
        raise SpendCapReached(f"tag {tag} reached its cap: ${mine:.2f} of ${TAG_CAP:.2f}")


def _extract_text(out: dict) -> str:
    return "".join(
        c.get("text", "")
        for item in out.get("output", [])
        if item.get("type") == "message"
        for c in item.get("content", [])
        if c.get("type") == "output_text"
    )


def _post(body: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {os.environ['ADAPTION_API_KEY']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _mock(body: dict) -> dict:
    h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
    return {"output": [{"type": "message", "content": [{"type": "output_text", "text": f"MOCK {h}"}]}],
            "usage": {"input_tokens": 10, "output_tokens": 3, "cost": 0.0}}


def complete(
    prompt: str | None = None,
    *,
    model: str,
    tag: str,
    system: str = "",
    messages: list[dict] | None = None,
    max_tokens: int | None = None,
    reasoning: str | None = "auto",
    temperature: float | None = None,
    sample: int = 0,
    cache: bool = True,
    timeout: float = 180,
) -> Completion:
    """One model call. `tag` names the experiment (e.g. "E02") for spend accounting and caps.

    Pass either `prompt` (one user turn) or `messages` (a list of {"role", "content"} turns; roles
    "user" and "assistant"). Identical requests are served from the cache for free; use a different
    `sample` index to draw independent samples of the same request. reasoning="auto" sends
    effort "low" to reasoning models (qwen, deepseek, glm) and nothing to the others.
    """
    if messages is None:
        if prompt is None:
            raise ValueError("pass prompt or messages")
        messages = [{"role": "user", "content": prompt}]
    if reasoning == "auto":
        reasoning = "low" if model.startswith(REASONING_PREFIXES) else None
    if max_tokens is None:
        max_tokens = 1500 if reasoning else 600
    body: dict = {"model": model, "instructions": system, "input": messages, "max_output_tokens": max_tokens}
    if reasoning:
        body["reasoning"] = {"effort": reasoning}
    if temperature is not None:
        body["temperature"] = temperature
    key = hashlib.sha256(json.dumps({"body": body, "sample": sample}, sort_keys=True).encode()).hexdigest()

    con = _db()
    if cache:
        row = con.execute("SELECT response FROM cache WHERE key = ?", (key,)).fetchone()
        if row:
            out = json.loads(row[0])
            u = out.get("usage") or {}
            return Completion(_extract_text(out), model, u.get("input_tokens") or 0, u.get("output_tokens") or 0,
                              0.0, True, (u.get("output_tokens") or 0) >= max_tokens)

    if BACKEND == "mock":
        out = _mock(body)
    else:
        _check_caps(tag)
        out = None
        for attempt in range(8):
            _acquire_slot()
            try:
                out = _post(body, timeout)
                break
            except urllib.error.HTTPError as e:
                detail = e.read()[:300].decode(errors="replace")
                if e.code == 429:
                    retry = e.headers.get("Retry-After") if e.headers else None
                    _block_all(float(retry) if retry and retry.isdigit() else 60.0)
                    _record(tag, model, 0, 0, 0.0, "429")
                    continue
                if e.code in (408, 409) or e.code >= 500:
                    _record(tag, model, 0, 0, 0.0, str(e.code))
                    time.sleep(min(2 ** (attempt + 1), 60) + random.random())
                    continue
                raise RuntimeError(f"Adaption API {e.code}: {detail}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError) as e:
                _record(tag, model, 0, 0, 0.0, type(e).__name__)
                time.sleep(min(2 ** (attempt + 1), 60) + random.random())
        if out is None:
            raise RuntimeError(f"Adaption API: gave up after 8 attempts ({model})")

    u = out.get("usage") or {}
    cost = float(u.get("cost") or 0.0)
    _record(tag, model, u.get("input_tokens") or 0, u.get("output_tokens") or 0, cost)
    if cache:
        con.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)", (key, json.dumps(out), time.time()))
    return Completion(_extract_text(out), model, u.get("input_tokens") or 0, u.get("output_tokens") or 0,
                      cost, False, (u.get("output_tokens") or 0) >= max_tokens)


def complete_many(jobs: list[dict], workers: int = 6, progress: str | None = None) -> list:
    """Run many `complete(**job)` calls in threads. Returns results in order; a failed job's slot
    holds its exception instead of a Completion. Stops early (remaining slots get the exception)
    once a spend cap is reached. `progress` is a label for a line on stderr every 50 jobs."""
    results: list = [None] * len(jobs)
    stop = threading.Event()
    done = [0]
    lock = threading.Lock()

    def run(i: int) -> None:
        if stop.is_set():
            results[i] = SpendCapReached("stopped after a spend cap was reached")
            return
        try:
            results[i] = complete(**jobs[i])
        except SpendCapReached as e:
            stop.set()
            results[i] = e
        except Exception as e:  # keep going; the caller decides what a failed item means
            results[i] = e
        with lock:
            done[0] += 1
            if progress and done[0] % 50 == 0:
                print(f"[{progress}] {done[0]}/{len(jobs)} done, spent ${spent():.3f} total", file=sys.stderr, flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run, range(len(jobs))))
    return results


def parse_json(text: str):
    """Pull the first JSON object or array out of model text (handles ```json fences). None if absent."""
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    candidates.append(text)
    for cand in candidates:
        for opener, closer in (("{", "}"), ("[", "]")):
            start = cand.find(opener)
            end = cand.rfind(closer)
            if start != -1 and end > start:
                try:
                    return json.loads(cand[start : end + 1])
                except json.JSONDecodeError:
                    continue
    return None


def report() -> str:
    con = _db()
    lines = [f"total ${spent():.4f} of ${SPEND_CAP:.2f} cap (per-experiment cap ${TAG_CAP:.2f})"]
    for tag, n, cost, errs in con.execute(
        "SELECT tag, COUNT(*), SUM(cost), SUM(error IS NOT NULL) FROM spend GROUP BY tag ORDER BY tag"
    ):
        lines.append(f"  {tag:10s} calls={n:6d} errors={errs:4d} ${cost:.4f}")
    for model, n, cost in con.execute("SELECT model, COUNT(*), SUM(cost) FROM spend GROUP BY model ORDER BY 3 DESC"):
        lines.append(f"  {model:20s} calls={n:6d} ${cost:.4f}")
    recent = con.execute("SELECT COUNT(*) FROM calls WHERE ts > ?", (time.time() - 60,)).fetchone()[0]
    cached = con.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
    lines.append(f"requests in the last 60 s: {recent} (limit {RPM}); cached responses: {cached}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
