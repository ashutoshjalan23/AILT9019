# Course timeline and actual development record

The schedule below is transcribed from the supplied proposal. Historical labels describe intended milestones, not repository activity or verified submissions. Repository work and recorded evaluations were performed on 23 October 2026. Git author/committer dates are not backdated.

| Week | Planned milestone | Current evidence / status |
| --- | --- | --- |
| W2-3 | Select campus-dining idea | Described in supplied proposal |
| W4 | Draft proposal, Fri 25 Sep | Local source PDF present; Moodle submission unverified |
| W5 | Data/walk collection, peer reviews Mon 5 Oct | Synthetic implementation data only; reviews unverified |
| W6 | LLM parser, initial tests, revised proposal Sat 10 Oct | Adapter and tests created now; revised submission unverified |
| W7 | Integrate code filters/walking, second evaluation | Implemented and evaluated now with synthetic fixtures |
| W8 | LLM ranking/reasons, proactive questions, consultation | API adapter implemented; live test and consultation pending |
| W9 | Midterm review Mon 26 Oct | Runnable demo, offline evaluation and review checklist prepared |
| W10-11 | Fix failures, refine edge cases, README, optional features | README ready; real data and live API work remain |
| W12 | Must-have code freeze and final evaluation | Future |
| W13 | Final demonstration | Future |

## Actual work on 23 October

- Reviewed supplied proposal and Ed announcement excerpt.
- Created synthetic dining fixtures and walking graph with provenance warnings.
- Built memory, parsing, filters, routes, refusal and model adapter.
- Built local browser demo and launcher.
- Ran initial offline evaluation: 18/20 overall, 9/11 normal. Failures N01/N07 were incorrect expected venue sets, which omitted eligible rice-counter options. The engine's selection was consistent with the dataset.
- Retained initial output in `evaluation/checkpoint-1-results.csv` and its summary, corrected the two expected sets and re-ran evaluation. See current results for actual outcome.
- Added regression checks and midterm documentation. See Git history for actual commit times.

Do not present synthetic fixtures, simulated model responses, or this reconstructed milestone plan as evidence of earlier work or completed administrative requirements.
