"""Builds the blinded human-labelling pack from v2 drafts (condition "me" only, scenarios in v2.judge1_subset()).
Outputs in results/E04/: human_labels_template.csv, human_labels_KEY.csv (separate), human_scenarios.md."""
import csv, random
import common as C
from common import RES, read_jsonl
import v2

random.seed(2026)
scs = {s["id"]: s for s in v2.all_scenarios()}
ren = {r["id"]: r for r in read_jsonl(RES / "renderings_v2.jsonl")}
keep = v2.judge1_subset()  # so that both LLM judges rated every packed draft
drafts = [r for r in read_jsonl(RES / "drafts_v2_raw.jsonl") if r["draft"] and r["condition"] == "me" and r["id"] in keep]
sample = []
for m in v2.DRAFTERS2:
    for t in "AB":
        pool = [r for r in drafts if r["model"] == m and r["telling"] == t]
        random.shuffle(pool)
        sample += pool[:15]
random.shuffle(sample)
ids = random.sample(range(1, 1000), len(sample))
with open(RES / "human_labels_template.csv", "w", newline="") as f, open(RES / "human_labels_KEY.csv", "w", newline="") as k:
    w = csv.writer(f); kw = csv.writer(k)
    w.writerow(["row_id", "scenario_id", "recipient", "draft_text", "stance", "admits_fault"])
    kw.writerow(["row_id", "scenario_id", "model", "telling", "condition", "design"])
    for i, r in zip(ids, sample):
        s = scs[r["id"]]
        recip = s["party_b"]["name"] if r["telling"] == "A" else s["party_a"]["name"]
        rid = f"H{i:03d}"
        w.writerow([rid, r["id"], recip, r["draft"], "", ""]); kw.writerow([rid, r["id"], r["model"], r["telling"], r["condition"], s["design"]])
used = sorted({r["id"] for r in sample})
with open(RES / "human_scenarios.md", "w") as f:
    f.write("# Neutral fact sheets for the human-labelling pack\n\nOne entry per scenario_id in the CSV. Neutral telling only; the sender is whoever is NOT the `recipient` of the row.\n\n")
    for sid in used:
        s = scs[sid]
        f.write(f"## {sid}\n\n{s['party_a']['name']} ({s['party_a']['role']}) and {s['party_b']['name']} ({s['party_b']['role']}).\n\n{ren[sid]['neutral']}\n\n")
print(len(sample), "rows;", len(used), "scenarios")
