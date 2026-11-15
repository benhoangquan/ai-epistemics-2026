# Building the papers

The LaTeX files are now the source of truth. The Markdown drafts (`paper.md`, `appendix.md`) are frozen and will not be updated.
Both papers share the layout in `apart_preamble.tex` (10 pt Latin Modern, 1 inch margins, natbib author-year, `\pending{}` and `\authorsnote{}` red markers).

## Commands (run twice for references and cross-references)

    cd papers/A_reliability_scores && pdflatex -interaction=nonstopmode paper.tex && pdflatex -interaction=nonstopmode paper.tex
    cd papers/B_ghostwriting_gap   && pdflatex -interaction=nonstopmode paper.tex && pdflatex -interaction=nonstopmode paper.tex

Bibliographies are inline `thebibliography` blocks (no BibTeX run). Only Latin Modern is installed for pdflatex here (no libertine, newpx, microtype, titlesec, enumitem), so the preamble uses only standard packages.
Page budget: the body is everything before "References" (8 pages allowed). Check where "References" starts:
`pdftotext -f 7 -l 9 paper.pdf - | grep -n References`. At the last build: A body = 8 pages (full), B body = about 7.5 pages.

## Updating paper B after the second pass

1. Headline numbers used in several places (abstract, introduction, results, discussion, conclusion) are macros at the top of `B_ghostwriting_gap/paper.tex` (`\gemDraft`, `\glmDraft`, `\gemGap`, `\gemAdmit`, `\addedFacts`, `\nScen`, ...). Edit them once there.
2. Table cells (Tables 1 to 4 in the body, A1 to A5 in the appendix) are edited in place. Most body tables have their source named in the caption.
3. Each `\pending{...}` is a red `[[PENDING: ...]]` marker. Replace it with text, or delete it. Search: `grep -n pending paper.tex`. The abstract, Methods (5 markers), Section 4 (several), Discussion and the Conclusion each have some. The "Escalation" subsection (4.4) needs rewriting if the simulation lands.
4. Figure 1: save the plot as `B_ghostwriting_gap/figures/fig1_mirror_bias.png`. The paper picks it up automatically (it shows a placeholder box until the file exists). Spec: `figures/FIGURES_TODO.md`. Add the new figures with `\includegraphics` in the same way.
5. The in-text figures quoted in the Figure 1 caption are pilot values: update them too.
6. If the body grows past 8 pages, move tables (for example Tables 1 and 4) to Appendix E, in the same pattern (`\begin{table}[!ht]` after the `\appendix` line; captions numbered A1...).
7. `\authorsnote{...}` markers (repository public, verified claims) must be removed by the authors before submission. Both papers have two.
