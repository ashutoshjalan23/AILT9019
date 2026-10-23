# Proposal requirements and midterm readiness

Source: `AILT9019_Project_Proposal_Template (1).docx.pdf`, Team 34. Reviewed 23 October 2026. No separate rubric, peer feedback or consultation record was provided. The table covers every acceptance item and the timeline's non-code deliverables.

| Proposal item | Current status | Evidence / next action |
| --- | --- | --- |
| Fixed curated canteen data: name, building, floor, hours, price, cuisine/diet tags, last updated | Prototype only | Seven synthetic entries in `data/canteens.json`; metadata gives update date. Replace with sourced public HKU information and verify each field before claiming this must-have complete. |
| Multi-turn session context | Implemented, offline tested | `app/engine.py`, HTTP session isolation and reset tests; no persistent profiles. |
| LLM request parsing and context merge | Adapter implemented, live verification pending | `app/llm.py`, validated patch merge and simulated model tests. Needs actual group key and a live evaluation. |
| Proactive questions, especially missing building | Implemented, offline tested | Two explicit location prompts, then explains that a supported building is required. M01 and M03. |
| Code filters for hours, diet, budget | Implemented, offline tested | Opening boundaries, weekends, overnight intervals and eligibility assertions. Cuisine/spice/quiet/time also checked. |
| LLM ranking and short reasons | Adapter implemented, live verification pending | Candidate-ID validation, labelled model explanation, deterministic fallback. Fake-model tests are not evidence of provider compatibility. |
| Top 2-3 results | Implemented when enough qualify | Up to three; returns one if only one qualifies, with explicit count. Never fills missing slots with mismatches. |
| Building-to-building walks and directions | Prototype only | Synthetic graph in `data/walks.json`; shortest-path building sequence and minutes. Replace with surveyed/public routes and usable text directions. Not indoor GPS. |
| Safe refusal and no-match | Implemented for supported English patterns | Refuses delivery, booking, off-campus and allergy/medical questions. Impossible hours/budget/cuisine return no match. Broader phrasing requires human/live-model review. |
| 18-20 questions and recorded result table | Implemented | 20 fixed cases and actual per-turn outputs in `evaluation/results.csv`; first run retained separately. |
| Normal >=90%, refusals 100%, proactive multi-turn at midterm | Offline target checked; formal acceptance pending | See `evaluation/summary.json`. Synthetic deterministic fixtures only. Manual and live-model evaluation still needed; do not report this as completed full course validation. |
| Browser app and simple first-use instructions | Implemented | `web/`, Windows launcher, three-step README guide. Python must already be installed. |
| API setup documented | Implemented from supplied Ed excerpt | `.env.example`, README and `docs/bailian.md`. Group key missing, no paid calls performed. |
| Offline fallback | Implemented (should-have) | Demo runs without API credentials; API exceptions and bad model responses fall back. |
| Snapshot and diet limitations on screen | Implemented | Visible synthetic-data notice, starting-price qualification and no allergy guarantees. |
| No delivery/booking/off-campus/medical advice | Implemented within documented parser coverage | Refusal tests plus frontend notice. Does not guarantee understanding of arbitrary English or other languages. |
| Session-only privacy | Implemented | Memory only, 1h inactivity timeout, New chat, no message logging, no key sent to browser. |
| Voice input | Deferred should-have | Outside midterm minimum. |
| Map view | Deferred should-have | Text building sequence only; graph is not real navigational evidence. |
| Centennial coverage | Prototype only (should-have) | Synthetic Centennial building and venues; actual venue/route validation outstanding. |
| Other-agent skill packaging | Deferred should-have | Core engine is importable Python; no agent skill claimed. |
| W2-3 topic choice and W4 proposal | Source document exists | Proposal identifies original team idea. Submission date/status cannot be verified from a local PDF. |
| W5 public data and walk collection | Pending | Synthetic fixtures substitute for implementation; real collection not done. |
| W5 peer reviews, due Mon 5 Oct | Unverified | Team must provide or complete actual reviews; repository cannot establish submission. |
| W6 proposal revision, due Sat 10 Oct | Unverified | Peer feedback and revised submission not supplied. |
| W6 initial evaluation and W7 second run | Runs performed now, not historically | Two actual local runs on 23 Oct, first 18/20 then corrected fixture expectations. No claims of past-week runs. |
| W8 LLM pipeline and consultation | Partly implemented / consultation unverified | Model adapter awaits live run; team must confirm actual consultation. |
| W9 midterm, Mon 26 Oct | Prototype prepared; acceptance pending | Follow `docs/midterm-review.md` and close missing data/API/manual/course tasks. |
| W10-11 refinement and README | README prepared early; refinement ongoing | Prioritize real data, live evaluation and supported-language gaps before optional features. |
| W12 code freeze and final result table | Future | Re-run after live model and real-data integration; record failures honestly. |
| W13 final demo | Future | Include four random normal and two refusal cases, single and multi-turn. |

No evidence of peer-review submission, revised-proposal submission or consultation has been fabricated. This is a midterm-oriented implementation, not certification that every course obligation has been met.
