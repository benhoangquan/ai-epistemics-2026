"""Offline tests for epi.llm (mock backend, temporary state dir)."""
import importlib
import time


def load(monkeypatch, tmp_path, **env):
    monkeypatch.setenv("EPI_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("EPI_BACKEND", "mock")
    for k, v in env.items():
        monkeypatch.setenv(k, str(v))
    import epi.llm as llm
    return importlib.reload(llm)


def test_cache_and_mock(monkeypatch, tmp_path):
    llm = load(monkeypatch, tmp_path)
    a = llm.complete("hi", model="gemma-4-26b-a4b-it", tag="T")
    b = llm.complete("hi", model="gemma-4-26b-a4b-it", tag="T")
    c = llm.complete("hi", model="gemma-4-26b-a4b-it", tag="T", sample=1)
    assert a.text.startswith("MOCK") and not a.cached and b.cached and b.text == a.text and not c.cached


def test_reasoning_auto(monkeypatch, tmp_path):
    llm = load(monkeypatch, tmp_path)
    r = llm.complete("hi", model="qwen3.8-27b", tag="T")
    g = llm.complete("hi", model="gemma-4-31b-it", tag="T")
    assert r.text != g.text  # different bodies: reasoning effort is only sent to qwen


def test_caps(monkeypatch, tmp_path):
    llm = load(monkeypatch, tmp_path, EPI_TAG_CAP_USD=1, EPI_SPEND_CAP_USD=2)
    llm._record("A", "m", 0, 0, 1.5)
    try:
        llm._check_caps("A")
        raise AssertionError("tag cap not enforced")
    except llm.SpendCapReached:
        pass
    llm._check_caps("B")
    llm._record("B", "m", 0, 0, 0.6)
    try:
        llm._check_caps("C")
        raise AssertionError("global cap not enforced")
    except llm.SpendCapReached:
        pass


def test_rate_limiter(monkeypatch, tmp_path):
    llm = load(monkeypatch, tmp_path, EPI_RPM=3)
    t = time.time()
    for _ in range(3):
        llm._acquire_slot()
    assert time.time() - t < 1
    con = llm._db()
    con.execute("UPDATE calls SET ts = ts - 59.5")  # pretend the three calls were almost a minute ago
    t = time.time()
    llm._acquire_slot()
    assert 0.3 < time.time() - t < 3


def test_parse_json():
    from epi.llm import parse_json
    assert parse_json('sure ```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('answer: {"x": [1, 2]} done') == {"x": [1, 2]}
    assert parse_json("[1, 2]") == [1, 2]
    assert parse_json("nothing") is None
