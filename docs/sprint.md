# Sprint facts

Source: <https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15> (read 2026-11-14).

- **Event:** AI x Epistemics Research Sprint, run by Apart Research. Alex Csaky co-designed the tracks. Most design sketches and readings come from Forethought.
- **Dates:** Fri 13 to Sun 15 Nov 2026, online, with local hubs.
- **Deadline:** **Sun 15 Nov, 23:59 AoE**, which is Mon 16 Nov, 11:59 UTC.
- **Mission:** build benchmarks, verification tools and products that help people and institutions decide what to believe and what to do. The risks the sprint names are concentrated decision power, dependence on systems that are hard to evaluate, and manipulation.
- **Prizes:** $2,000 in total ($1,000 / $500 / $300 / $100 / $100). Winners also get fellowship fast-tracking, mentor introductions and a path toward a publishable write-up.
- **Credits:** Adaption gives registered participants 1,250 credits and 3 months of its Builder plan.

## Judging (each scored 1–5, same rubric for every track)
1. **Impact potential & innovation.** A 4–5 requires work that is new to the field. A replication cannot score that high.
2. **Execution quality.** Sound method, implementation and findings.
3. **Presentation & clarity.** Judges may decline to score a report they cannot follow.

## Submission
- PDF report on the official template, at most 8 pages. References and appendices don't count toward the limit.
- Title, a 150–250 word abstract, and authors with affiliations.
- **Required appendix:** "Limitations and Dual-Use / Ethical Considerations".
- Suggested sections: Intro, Related Work, Method, Results, Discussion, Limitations & Dual-Use, References.
- Optional: public repo, a 3–5 minute video, slides, a project image.
- Teams of up to 5 are suggested. Each person may be on at most 2 projects.
- **Prior work must be disclosed.** Code written before the sprint must be marked as preexisting in the README and the report.
- To resubmit, use the same title before the deadline. AI tools are allowed, but fabricated results or references can disqualify a team.

## Tracks and the challenges each one lists

### Track 1: Model epistemics & decision-making evals
*Does a model know how solid its claims are, and can its confidence be elicited and checked?*
- Measure whether a model's confidence in a decision matches reality.
- Measure the gap between what a model implies and what it will defend: overselling, flip-flopping, misrepresenting evidence.
- Test whether honesty-benchmark rankings predict better decisions.
- Keep benchmarks meaningful over time, and find exploits that game them.

Example projects on the page: MisleadBench, Confidence Audit, FlipRate, an epistemic virtue eval suite in Inspect, and an Article 5 (EU AI Act) measurement protocol.

### Track 2: Trust infrastructure
*Make checking claims and tracing their origins cheap, routine and hard to manipulate, for people and AI agents.*
- Which source-reliability scoring methods are hardest to cheat and easiest to audit?
- What tamper-evident layer is missing from AI observability standards?
- Do reliability or provenance tools actually improve AI behavior and accuracy?
- What share of a domain's content can be tied to checkable evidence?

Example projects: Track-Record Ledger, Tamper-Evident Action Recorder (OTel GenAI), Citation Binder, Provenance Study.

### Track 3: Epistemic products
*Do tools improve the decisions people endorse later, not just how satisfying the advice feels?*
- Does advice people act on lead to choices they later endorse?
- Do chatbots escalate or calm disputes?
- Do decision briefings surface the considerations that matter?
- Does surfacing inconsistencies and cruxes in group beliefs change decisions?

Example projects: Dispute Escalation Benchmark, Decision-Brief Rubric, Crux Mapper.

### Track 4: Open (deployment, adoption & impact)
- A defensible unit for "decision quality improved", the field's QALY.
- The certification, budget and approval chokepoints that keep AI tools out of legislatures.
- Why institutions ignore forecasts they asked for.
- What can be measured about a live deployment using only data you can download over a weekend.

Example projects: scenario planning on tap, fast facilitation, QALY for epistemics, Procurement Gap Report, "Do their numbers match?", wish registry.

## Reading list (from the sprint page)
- **Sprint-wide:** State of the Field: AI for Epistemics and Coordination (2026). What's Important in "AI for Epistemics"? (Finnveden, 2024). AI Impacts on Epistemics: the Good, the Bad and the Ugly (Cotton-Barratt & Hadshar, 2026). Design Sketches for a More Sensible World (Forethought, 2026). Project Ideas: Epistemics (Finnveden). A Full Epistemic Stack (Sourbut & Goldhaber, 2025). Multi-Agent Risks from Advanced AI (Hammond et al., 2025).
- **Track 1:** MASK, DarkBench, SycEval, ELEPHANT. Why Language Models Hallucinate (Kalai et al., 2025). ForecastBench. Petri and Bloom. EU AI Act Article 5.
- **Track 2:** C2PA spec v2.4 and c2patool. Community Notes open data and "From Birdwatch to Community Notes" (2025). AI for AI for Epistemics (2026). AVeriTeC. OpenTelemetry GenAI conventions. Certificate Transparency (RFC 6962).
- **Track 3:** Design Sketches: Angels-on-the-Shoulder. Guardian Angels (Gwern, 2026). Sycophancy in GPT-4o (OpenAI, 2025). Sycophantic AI Decreases Prosocial Intentions and Promotes Dependence (Cheng et al., Science 2025). AI Can Help Humans Find Common Ground (Tessler et al., Science 2024).
- **Track 4:** The AI Adoption Gap (Vaintrob, 2025). AI Tools for Existential Security (2025). Community Notes roll-out study (Chuai et al., CSCW 2024). Accuracy of Forecasts in Strategic Intelligence (Mandel & Barnes, PNAS 2014). FutureSearch, Swift Centre and Sentinel write-ups.

## Talks still to come (UTC)
- Sat 14 Nov, 14:15: Jonathan Stray, "Destructive Feedback Loops between Conflict and Knowledge" (relevant to P3.2).
- Sat 14 Nov, 18:15: Joel Suro, "The Two Dogmas of AI".
- Sun 15 Nov, 15:15: S. Orestis Palermos, "Artificial Knowing".
