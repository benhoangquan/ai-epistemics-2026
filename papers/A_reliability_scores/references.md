# References

Checked on 15 Nov 2026. "Verified" means the work was opened (or a listing page for it read) and the claim made in the paper matches.

## Cited, verified

1. Sempere, N. and Lawsen, A. (2021, revised 2023). *Alignment Problems With Current Forecasting Platforms*. arXiv:2106.11248. https://arxiv.org/abs/2106.11248
   Verified from the full PDF text (https://arxiv.org/pdf/2106.11248). Section 2.1 states that the scoring rule incentivizes forecasters to pick questions selectively, with a Brier result and a relative-Brier result (Theorems 1 to 3). Theorem 4: under a total (cumulative) relative Brier score a forecaster should predict the community average rather than abstain. The abstract alone does not mention selection.
2. Lichtendahl, K. C. Jr. and Winkler, R. L. (2007). Probability elicitation, scoring rules, and competition among forecasters. *Management Science* 53(11), 1745-1755. https://pubsonline.informs.org/doi/abs/10.1287/mnsc.1070.0729
   Verified through abstract and bibliographic records (Duke Scholars, EconPapers). Competitive forecasters report more extreme probabilities.
3. Witkowski, J., Freeman, R., Vaughan, J. W., Pennock, D. M. and Krause, A. (2018). Incentive-compatible forecasting competitions. AAAI 2018. https://ojs.aaai.org/index.php/AAAI/article/view/11471 . Extended: Management Science 69(3), 1354-1374 (2023), arXiv:2101.01816. https://arxiv.org/abs/2101.01816
   Verified through abstract and listing pages. Lottery-based mechanisms for winner-take-all competitions.
4. Hanson, R. (2002 working paper; published 2007). *Logarithmic Market Scoring Rules for Modular Combinatorial Information Aggregation*. Journal of Prediction Markets 1(1), 3-15. https://mason.gmu.edu/~rhanson/mktscore.pdf
   Verified from the full text of the working paper (read via PDF text extraction). It states that, for any scoring rule s_i(r), a market scoring rule pays a report r the difference s_i(r) minus s_i(rho), where rho is the previous report, and it treats logarithmic rules as a special case. The 2007 journal listing was seen in search results. The paper cited in pass 1 (Hanson 2003, Information Systems Frontiers 5(1), 107-119) is no longer cited, because its PDF could not be fetched (expired certificate) and the claim is now sourced to the paper that was read.
5. (moved) Metaculus Scores FAQ: see "Unverified, not cited" below.
6. Gneiting, T. and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association* 102(477), 359-378. DOI 10.1198/016214506000001437. https://heibib.ub.uni-heidelberg.de/search/Record/1628649828
   Verified through bibliographic records and abstract.
7. Rubinstein, R. (1999). The cross-entropy method for combinatorial and continuous optimization. *Methodology and Computing in Applied Probability* 1, 127-190. https://link.springer.com/content/pdf/10.1023/A:1010091220143.pdf
   Verified through search results and abstract.

## Data source (not a citation in the text)

- Manifold Markets API documentation. https://docs.manifold.markets/api . Verified: `GET /v0/bets`, `GET /v0/search-markets`, rate limit 500 requests per minute per IP.

## Unverified, not cited

- Metaculus Scores FAQ, https://www.metaculus.com/help/scores-faq/ and /help/scoring/ . Two fetches returned HTTP 403 in pass 2 (and one in pass 1). Only search-result summaries were seen. Removed from the paper.
- Hanson (2003), Information Systems Frontiers 5(1), 107-119. Its PDF fetch failed (expired certificate). Not cited.
- Murphy (1973) on hedging and skill scores, and Jolliffe and Stephenson (2008), that skill scores are generally improper. Named in the E03 README. Not opened. Dropped.
- Community Notes bridging literature and Metaculus or Manifold forecaster-ranking studies (listed in the report plan for related work). Not opened. Dropped.
- Brier (1950). Not opened. The Brier score is used without citation.
- Tetlock et al. (2015), quoted inside Sempere and Lawsen. Not opened. Not cited.

## Added in the review response (15 Nov 2026, all checked at abstract or listing level unless noted)

<!-- Murphy (1973) and Jolliffe and Stephenson (2008) removed from the paper on 15 Nov at the authors' request. -->
9. Jolliffe, I. T. and Stephenson, D. B. (2008). Proper scores for probability forecasts can never be equitable. Monthly Weather Review 136, 1505-1510. https://stormrisk.github.io/2008/jolliffe.pdf . Full text read (6 pages).
10. Bröcker, J. and Smith, L. A. (2007). Scoring probabilistic forecasts: the importance of being proper. Weather and Forecasting 22(2), 382-388. https://researchonline.lse.ac.uk/id/eprint/22219 . Abstract read (LSE preprint page). It argues for proper scores in general. It does not address ratio skill scores, so it is cited only for propriety. The title given by the reviewer was not found.
11. Merkle, E. C., Steyvers, M., Mellers, B. and Tetlock, P. E. (2016). Item response models of probability judgments: application to a geopolitical forecasting tournament. Decision 3(1), 1-19. https://repository.upenn.edu/marketing_papers/364 . Abstract and listing read.
12. Karger, E. et al. (2025). ForecastBench: a dynamic benchmark of AI forecasting capabilities. ICLR 2025, arXiv:2409.19839. https://arxiv.org/abs/2409.19839 . Existence verified from the arXiv and ICLR listings. That the benchmark reports difficulty-adjusted Brier scores (market Brier and two-way fixed effects) comes from search summaries of the Forecasting Research Institute write-up; the exact adjustment was not opened. The paper says only "reported by ForecastBench".
13. Turner, B. M., Steyvers, M., Merkle, E. C., Budescu, D. V. and Wallsten, T. S. (2014). Forecast aggregation via recalibration. Machine Learning 95(3), 261-289. https://www.doi.org/10.1007/S10994-013-5401-4 . Abstract summaries read (recalibration with a linear-in-log-odds function).
14. Baron, J., Mellers, B. A., Tetlock, P. E., Stone, E. and Ungar, L. H. (2014). Two reasons to make aggregated probability forecasts more extreme. Decision Analysis 11(2), 133-145. https://pubsonline.informs.org/doi/10.1287/deca.2014.0293 . Abstract read. Note the reviewer listed Baron et al. 2014 without a title, and the first author is Baron.
15. Satopää, V. A., Baron, J., Foster, D. P., Mellers, B. A., Tetlock, P. E. and Ungar, L. H. (2014). Combining multiple probability predictions using a simple logit model. International Journal of Forecasting 30(2), 344-356. https://econpapers.repec.org/RePEc:eee:intfor:v:30:y:2014:i:2:p:344-356 . Abstract read.
16. Platt, J. C. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. In Advances in Large Margin Classifiers, 61-74. https://users.cs.fiu.edu/~sjha/class2023/Lecture7/Slides/1999PlattScaling.pdf . Search summary read (sigmoid fitted to SVM outputs). The linked file is a course copy.
17. Zadrozny, B. and Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. KDD 2002, 694-699. https://www.cs.cornell.edu/courses/cs678/2007sp/ZadroznyElkan.pdf . Year 2002 confirmed from citing papers. Cited for isotonic regression calibration. The 2001 ICML paper (Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers) was not opened and is not cited.
18. Niculescu-Mizil, A. and Caruana, R. (2005). Predicting good probabilities with supervised learning. ICML 2005, 625-632. https://mlanthology.org/icml/2005/niculescumizil2005icml-predicting . Abstract read (Platt scaling and isotonic regression compared).
19. Page, L. and Clemen, R. T. (2013). Do prediction markets produce well-calibrated probability forecasts? Economic Journal 123(568), 491-513. https://ideas.repec.org/a/ecj/econjl/v123y2013i568p491-513.html . Listing and abstract read (favourite-longshot pattern that worsens with time to resolution).

The paper text says only what these sources support: it says nothing about isotonic regression being worse in small samples as a published result. That is our own finding (Table A9).
