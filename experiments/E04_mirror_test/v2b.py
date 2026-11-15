"""E04 v2b (post hoc): strip restated-scenario text from the pilot's search-transfer drafts, re-judge them.

Pilot transfer drafts (results/E04/transfer_drafts.jsonl) came from the `third_person` system prompt, so nearly every one
opens with a restatement / outside-observer assessment before the message. The pilot judge saw all of it.
We extract only the message, re-judge (deepseek-v4-flash and gemma-4-31b-it), and recompute the transfer contrast.
Output: results/E04/transfer_stripped_v2.jsonl
"""
import re, json
import common as C
from common import RES, log, read_jsonl, write_jsonl
import run as R
import v2


def extract_message(d: str):
    heads = list(re.finditer(r"^\*\*[^\n*]{0,80}(?:message|draft)[^\n*]{0,60}\*\*:?[ \t]*$", d, re.I | re.M))
    if heads:
        body = d[heads[-1].end():].strip()
        parts = re.split(r"\n-{3,}\s*\n", body)
        if len(parts[0].split()) >= 40:
            return parts[0].strip(), "header"
        return body, "header_whole"
    parts = [p.strip() for p in re.split(r"\n-{3,}\s*\n", d) if p.strip()]
    if len(parts) > 1 and len(parts[-1].split()) >= 40:
        return parts[-1], "last_hr"
    return None, "unextracted"


if __name__ == "__main__":
    scs = {s["id"]: s for s in v2.all_scenarios()}
    ren = {r["id"]: r for r in read_jsonl(RES / "renderings.jsonl")}  # transfer drafts were made from the PILOT tellings
    tr = read_jsonl(RES / "transfer_drafts.jsonl")
    items = []
    for r in tr:
        m, how = extract_message(r["draft"])
        items.append((r, m, how))
    log(f"v2b: extraction {dict(__import__('collections').Counter(h for _,_,h in items))}")
    out = []
    for judge in ("deepseek-v4-flash", "gemma-4-31b-it"):
        jobs, idx = [], []
        for i, (r, m, how) in enumerate(items):
            if m is None: continue
            s = scs[r["id"]]; a, b = s["party_a"]["name"], s["party_b"]["name"]
            sender, rec = (a, b) if r["telling"] == "A" else (b, a)
            jobs.append(dict(prompt=R.draft_judge_prompt(s, ren[r["id"]]["neutral"], sender, rec, m), model=judge,
                             max_tokens=3000 if judge.startswith("deepseek") else 800)); idx.append(i)
        res = C.run_jobs(jobs, f"v2b-{judge}")
        for i, rr in zip(idx, res):
            obj = None if isinstance(rr, Exception) else C.parse_json(rr.text)
            r, m, how = items[i]
            out.append({"id": r["id"], "telling": r["telling"], "judge": judge, "extract": how, "message": m,
                        "rating": obj if isinstance(obj, dict) else None})
    write_jsonl(RES / "transfer_stripped_v2.jsonl", out)
    # baseline glm drafts on the same held-out ambiguous scenarios, judged by gemma too (deepseek ratings already in drafts.jsonl)
    tr_ids = {r["id"] for r in tr}
    base = [r for r in read_jsonl(RES / "drafts.jsonl") if r["model"] == "glm-5.3-flash" and r["id"] in tr_ids and r.get("draft")]
    jobs = []
    for r in base:
        s = scs[r["id"]]; a, b = s["party_a"]["name"], s["party_b"]["name"]
        sender, rec = (a, b) if r["telling"] == "A" else (b, a)
        jobs.append(dict(prompt=R.draft_judge_prompt(s, ren[r["id"]]["neutral"], sender, rec, r["draft"]), model="gemma-4-31b-it", max_tokens=800))
    res = C.run_jobs(jobs, "v2b-baseline-gemma")
    rows = []
    for r, rr in zip(base, res):
        obj = None if isinstance(rr, Exception) else C.parse_json(rr.text)
        rows.append({"id": r["id"], "telling": r["telling"], "judge": "gemma-4-31b-it", "rating": obj if isinstance(obj, dict) else None})
    write_jsonl(RES / "transfer_baseline_gemma_v2.jsonl", rows)
