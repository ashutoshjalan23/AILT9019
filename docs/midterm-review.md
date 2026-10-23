# Midterm review preparation · 26 October 2026

## Current scope

Local end-to-end campus dining demonstration with synthetic data, session preferences, proactive questions, deterministic eligibility rules, walking graph, optional model adapter and offline fallback. See `requirements.md` for every proposal item and what is still pending.

## Five-minute demo

1. Launch with `start-demo.bat`, leave demo clock at Friday 12:30 Hong Kong time. Point out the synthetic-data notice and offline/live mode.
2. Leave starting building empty. Send “I want something cheap”. Show the location question.
3. Send “I'm at Main Library”. Show up to three matching venues, starting prices and walk estimates.
4. Send “Only vegetarian”, then “Make it cheaper”. Show retained building and updated diet/budget.
5. Send “Anything open at 11 pm”. Show no-match rather than closed canteens.
6. Send “Deliver food to my dorm”, then “I have a peanut allergy”. Show service boundaries and ingredient-safety refusal.
7. Use New chat to clear preferences. Show the evaluation CSV and explain what automated checks establish and what they do not.

## Before formal acceptance

- [ ] Replace synthetic canteens/hours/prices/tags with publicly sourced HKU data, record source URLs and checked dates per field, and validate on site where necessary. Do not invent source attribution.
- [ ] Replace synthetic links with verified building-to-building routes and useful directions; check travel times, stairs and accessibility limitations.
- [ ] Put the actual key in local `.env`; verify a complete parse-and-rank live call using the course Token Plan endpoint and model.
- [ ] Run the 20 questions manually in live mode. Independently judge extraction, context merging, reasons, routes and failure handling. Test wording beyond the offline parser's vocabulary.
- [ ] Confirm at least 90% normal passes, all refusal cases correct and multi-turn proactive questions working in the human/live review.
- [ ] Ask another team member to complete first-use steps and keyboard/mobile checks; record actual observations.
- [ ] Confirm peer-review submission, revised-proposal submission, and consultation. Attach actual records or feedback; do not mark completed based on the code.
- [ ] Check any separate Moodle/Ed midterm rubric, which was not supplied here.

## Human evaluation worksheet

Keep the automated CSV unchanged as offline evidence. Copy this table into a separate live-review record with the actual date and reviewer.

| Case ID / question | Mode / model | System output | Pass/Fail | Notes and reviewer |
| --- | --- | --- | --- | --- |
| N01-N11 (one row each) | Pending | Pending | Not run | Check constraints, context, useful reasons and directions |
| R01-R03 (one row each) | Pending | Pending | Not run | No unsafe/out-of-scope recommendation |
| E01-E03 (one row each) | Pending | Pending | Not run | Clarify ambiguity or give supported general choices |
| M01-M03 (one row per conversation) | Pending | Pending | Not run | Inspect every turn and preference update |

## Known limitations

Synthetic venues are not real dining recommendations. Walking sequences are illustrative, not surveyed wayfinding. Offline parsing only handles selected English patterns and can miss unsupported intent. It does not assess allergy safety, medical nutrition, queue lengths, menu availability or live opening changes. Model reasons can hallucinate and are separately labelled; check them against the fixed fields. Localhost server is for demonstration, not a deployed multi-user service. No live API performance, credit use or public-data correctness has been measured.
