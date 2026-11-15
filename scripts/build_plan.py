#!/usr/bin/env python3
"""Build the report plan outputs from report-plan.yaml.

Usage:
    python3 scripts/build_plan.py                     # docs/report-plan.md and mindmap/plan.html
    python3 scripts/build_plan.py --artifact OUT.html # also write the bare page fragment for a claude.ai artifact

Reuses the node and panel helpers from build.py, so the plan map looks and behaves like the idea map.
"""
import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import GEN, ROOT, clean, esc, kicker, mm_id, mm_label, node, ref, standalone, to_json  # noqa: E402

COLOR_NAMES = {"pick": "decision", "t2": "paper A", "t3": "paper B", "t1": "rubric", "theme": "shared", "t4": "timeline", "rl": "risks"}


def load():
    plan = yaml.safe_load((ROOT / "report-plan.yaml").read_text(encoding="utf-8"))
    errors = []

    def walk(items, depth, path, color, trail):
        for i, it in enumerate(items, start=1):
            key = "n" + ".".join(path + [str(i)])
            it["key"], it["depth"], it["trail"] = key, depth, list(trail)
            if depth == 1:
                color = it.get("c")
                if color not in COLOR_NAMES:
                    errors.append(f"{it.get('n')!r}: branch color {color!r} not one of {list(COLOR_NAMES)}")
            it["color"] = color
            if not it.get("n"):
                errors.append(f"{key}: missing n")
            if not it.get("d"):
                errors.append(f"{key} {it.get('n')!r}: missing d")
            it.setdefault("k", [])
            walk(it["k"], depth + 1, path + [str(i)], color, trail + [it])

    walk(plan["tree"], 1, [], None, [])
    if errors:
        sys.exit("report-plan.yaml failed validation:\n  " + "\n  ".join(errors))
    return plan


def flat(items):
    for it in items:
        yield it
        yield from flat(it["k"])


def to_tree(it):
    label = esc(it["n"])
    if it["depth"] == 1:
        label = f'<span class="m-branch">{label}</span>'
    return node(label, it["color"], it["key"], [to_tree(c) for c in it["k"]])


def paragraphs(text):
    return "".join(f"<p>{esc(p)}</p>" for p in str(text).split("\n\n"))


def build_details(plan):
    d = {}
    branches = plan["tree"]
    d["root"] = (
        kicker("Overview") + f"<h2>{esc(plan['title'])}</h2>"
        + f"<p>{esc(plan['subtitle'])}</p><p class=\"p-small\">{esc(plan['written'])}</p>"
        + "<p>Click a label to read its detail here, or a branch below.</p>"
        + '<ul class="p-list">'
        + "".join(f'<li>{ref(b["key"], esc(b["n"]))}<span class="p-small">{esc(clean(b["d"]))[:150]}…</span></li>' for b in branches)
        + "</ul>"
    )
    parents = {}
    for b in branches:
        for it in flat([b]):
            for c in it["k"]:
                parents[c["key"]] = it
    for it in flat(branches):
        crumbs = " › ".join(esc(t["n"]) for t in it["trail"]) or COLOR_NAMES[it["color"]]
        body = kicker(crumbs, "") + f"<h2>{esc(it['n'])}</h2>" + paragraphs(it["d"])
        if it["k"]:
            body += "<h3>Contains</h3><ul class=\"p-list\">" + "".join(
                f'<li>{ref(c["key"], esc(c["n"]))}</li>' for c in it["k"]
            ) + "</ul>"
        if it["key"] in parents:
            p = parents[it["key"]]
            body += f'<p>{ref(p["key"], "Up to " + esc(p["n"]))}</p>'
        d[it["key"]] = body
    return d


def build_page(plan):
    tree = node(
        f'<span class="m-root">{esc(plan["title"])}</span>', "root", "root", [to_tree(b) for b in plan["tree"]]
    )
    n_nodes = sum(1 for _ in flat(plan["tree"]))
    stats = f"{len(plan['tree'])} branches and {n_nodes} nodes. {plan['written']}."
    template = (ROOT / "scripts" / "plan_page.html").read_text(encoding="utf-8")
    from html import escape

    return (
        template.replace("__TREE__", to_json(tree))
        .replace("__DETAILS__", to_json(build_details(plan)))
        .replace("__STATS__", escape(stats, quote=False))
    )


def build_markdown(plan):
    lines = [GEN.replace("brainstorm.yaml", "report-plan.yaml").replace("build.py", "build_plan.py"), "",
             f"# {plan['title']}", "", f"*{plan['subtitle']}.* {plan['written']}.", "",
             "Interactive mind map: [`mindmap/plan.html`](../mindmap/plan.html). Hours are estimates, not measurements.", "",
             "```mermaid", "mindmap", f"  root(({mm_label(plan['title'])}))"]
    for b in plan["tree"]:
        lines.append(f"    {mm_id('b' + b['key'])}[{mm_label(b['n'], 40)}]")
        for c in b["k"]:
            lines.append(f"      {mm_id('i' + c['key'])}({mm_label(c['n'], 44)})")
    lines += ["```", ""]

    def bullets(items, indent):
        for it in items:
            pad = "  " * indent
            lines.append(f"{pad}- **{it['n']}.** {clean(it['d'])}")
            bullets(it["k"], indent + 1)

    for b in plan["tree"]:
        lines += [f"## {b['n']}", "", clean(b["d"]), ""]
        for it in b["k"]:
            lines += [f"### {it['n']}", "", clean(it["d"]), ""]
            if it["k"]:
                bullets(it["k"], 0)
                lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", type=Path)
    args = ap.parse_args()
    plan = load()
    (ROOT / "docs" / "report-plan.md").write_text(build_markdown(plan), encoding="utf-8")
    fragment = build_page(plan)
    (ROOT / "mindmap" / "plan.html").write_text(standalone(fragment), encoding="utf-8")
    if args.artifact:
        args.artifact.write_text(fragment, encoding="utf-8")
    n = sum(1 for _ in flat(plan["tree"]))
    print(f"ok: {len(plan['tree'])} branches, {n} nodes -> docs/report-plan.md, mindmap/plan.html")


if __name__ == "__main__":
    main()
