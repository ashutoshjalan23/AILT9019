# Live API test review · 23 October 2026

The user's locally configured group key successfully authenticated against the course Token Plan endpoint using `qwen3.8-flash`. A small JSON connectivity request passed. The key was not displayed, added to source or included in test reports.

## Results

- Offline regression suite: 13/13 test methods pass.
- Offline proposal scenarios: 20/20 pass.
- Initial full live run: 13/20 pass, with 41 attempted model calls. Normal 8/11, refusal 3/3, edge 1/3, multi-turn 1/3. Nine requests timed out at the original 15-second limit. All three deterministic safety-refusal scenarios passed.
- Failed-case retest with 45-second timeout: 4/7 pass, with 21 attempted calls. All three normal-case retests passed, one of two edge cases passed, and neither multi-turn retest passed strict live checks. Recorded errors included TimeoutError, URLError and RemoteDisconnected.
- A final focused E02 run with the shorter ranking prompt passed in 22.4 seconds, using two calls without API errors. Do not combine runs into a claim that a complete live suite passed in one run. M01 and M02 still have unresolved live failures in their latest recorded tests.

The engine's fallback kept providing usable responses in the presence of model failures. These tests deliberately count model failures and recommendation fallback as live integration failures, even when the deterministic result itself is correct. This distinction prevents a successful offline fallback from hiding unreliable live access.

## Changes made

The network timeout is now 45 seconds per model request, without automatic retries. Ranking now requests at most three candidates with reasons of at most 12 words each, matching the number displayed. This reduces unnecessary output for broad requests. The normal app process retains its 30-attempt cap; the explicit live evaluation has its own 50-attempt cap. `--failed` preserves initial results, while `--case E02` writes a separate focused report.

No automatic retry loop or increased concurrency was introduced. Provider/network reliability and independent human quality review remain open. Actual shared credit balance was not measured.

The user's persistent `BAILIAN_ENABLED=false` setting was left unchanged. Live evaluation explicitly enables its own client in-process; enable the local setting and restart the server to use the key in the browser app. The previously running browser server retains its startup configuration until restarted.

Evidence: `evaluation/live-results.csv`, `evaluation/live-summary.json`, `evaluation/live-retest-results.csv`, `evaluation/live-retest-summary.json`, and the focused report. All data remains synthetic.
