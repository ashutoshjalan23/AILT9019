# HKU Dining Assistant · Team 34

AILT9019 midterm prototype: a small conversational campus dining assistant based on the supplied project proposal. Python standard library backend and plain HTML/CSS/JavaScript frontend. No package installation or build step is needed to run it.

**All venues, menus, prices, opening hours and walking routes are synthetic.** This is a course demonstration, not a source of real HKU dining information. The offline prototype is working; the separate live evaluation records provider integration results. Public-data collection and human acceptance remain pending.

## Open the demo

Requires Python 3.10 or later. On Windows, double-click `start-demo.bat`. Alternatively, from this folder run:

```powershell
python -m app.server
```

1. Open http://127.0.0.1:8000 in your browser.
2. Choose a starting building and set your preferences in the chat. The clock initially shows **23 October 2026, 12:30 Hong Kong time**, explicitly for demonstration. Choose **Use now** to check the current time.
3. View options and refine them with “Only vegetarian”, “Make it cheaper”, “Any budget”, or “Any cuisine”. **New chat** clears session preferences.

Example: select Main Library, send “Spicy, cheap and open now”, then “Only vegetarian”. Ask “Deliver food to my dorm” to demonstrate refusal. A supported location is required for walking directions; it is never guessed.

## Enable the sponsored Bailian model

The Ed announcement provided in this chat specifies the **Aliyun Bailian Token Plan Team Edition**, not a generic pay-as-you-go DashScope endpoint.

1. Copy `.env.example` to `.env` and put the group key in `BAILIAN_API_KEY` locally.
2. Set `BAILIAN_ENABLED=true`. The supplied configuration uses the course OpenAI-style endpoint `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1` and `qwen3.8-flash`.
3. Restart the server and make one request. The page reports model, hybrid or offline mode for each turn. Missing keys, timeouts, invalid responses and the local call limit fall back to rules.

The key remains on the server, never in browser assets or Git. The first batch of course keys expires **19 November 2026**, according to the supplied announcement. The group shares **25,000 credits**, for course work only. Keep `.env` private and contact the TAs to rotate any exposed key.

Calls are sequential, with no automatic retries and at most two calls per recommendation turn (parse and rank). Each response is capped at 500 output tokens, each message at 1,000 characters, with a default **30 attempted calls per server process**. Failed calls count too. Restarting resets this local cap; it does not track shared credits or other tools' use. Initial development was offline; subsequent live test attempts are recorded separately in `evaluation/live-summary.json`.

Course references: [Bailian Codex guide](https://docs.bailian.console.aliyun.com/en/model-studio/codex) and [Alibaba's OpenAI-compatible API reference](https://help.aliyun.com/en/model-studio/qwen-api-via-openai-chat-completions). The course endpoint and model configuration come from the Ed excerpt, which takes precedence over generic endpoint examples.

## How it works

Browser request → session preferences → optional LLM filter extraction → validated preference merge → code filters for hours, price, cuisine, menu tags and walking range → optional LLM ordering and explanation → up to three eligible venues.

- Requests retain preferences during a session. Explicit updates replace or clear individual filters.
- Code, rather than the model, decides eligibility. Model output is treated as untrusted JSON. Ranking may use only eligible venue IDs; invalid output falls back to deterministic ordering.
- The offline parser handles the proposal's English example vocabulary; it is not a general language model. Unrecognized language can be missed. LLM explanations are labelled separately and can still be wrong; displayed prices, locations and walks always come from the dataset.
- “Cheap” means starting price up to HK$35. “Cheaper” reduces the current budget by HK$10 (default starting budget HK$40). Budget compares the cheapest listed option, not every dish.
- Opening hours use Hong Kong time, weekday/weekend intervals and an exclusive closing boundary. No holidays or live opening checks are modelled.
- Walking uses shortest paths through a synthetic building graph. Default maximum is 15 minutes one way. A stated break must cover a return walk plus a fixed 10-minute meal allowance. Queues, accessibility, lifts and indoor wayfinding are not modelled.
- When fewer than two venues qualify, the app returns only those available. It does not invent options or relax dietary restrictions.
- Context lives in server memory for up to one hour. There is no persistent conversation log or user profile. Cookies identify a session; browsers sharing the same cookie jar share that session. Requests and credentials are not logged. The server is bound to localhost for local demonstration.

## Verify

```powershell
python -m unittest discover -v
python -m evaluation.run
```

The evaluation command writes `evaluation/results.csv` (Question → System output → Pass/Fail → Notes) and `evaluation/summary.json`. It is deliberately offline and reproducible, using Friday lunchtime and synthetic data. The 20 cases include 11 normal, 3 refusal, 3 edge and 3 multi-turn conversations. Automated fixture results do **not** establish live-model quality or human usefulness. A human review worksheet and presentation checklist are in `docs/midterm-review.md`.

To explicitly test the real provider using your local key, run `python -m evaluation.live`. This spends course quota, makes sequential calls with a 50-attempt cap for the evaluation process, and writes separate `evaluation/live-results.csv` and `evaluation/live-summary.json` files. It tests all 20 conversations and counts rejected model responses or recommendation fallbacks as failures. Safety refusals intentionally run in code without model calls. It does not change the app's `BAILIAN_ENABLED` setting or replace independent human review.

Use `python -m evaluation.live --failed` to retest only failures from that full live run. Retests go to separate `live-retest-results.csv` and `live-retest-summary.json` files, preserving the initial failures. Live testing exposed provider responses exceeding the original 15-second request timeout; the adapter now allows 45 seconds per call without automatic retries.

## Project files

- `app/`: server, deterministic engine and opt-in Bailian adapter.
- `web/`: accessible, responsive chat and recommendations.
- `data/`: synthetic canteen and building-walk datasets.
- `tests/`, `evaluation/`: regression tests, fixed test set and actual recorded outputs.
- `docs/requirements.md`: proposal requirements, evidence and outstanding tasks.
- `docs/midterm-review.md`: demo script, manual review and limitations.
- `docs/timeline.md`: proposed course timeline with honest current status.

The original proposal PDF is retained at the repository root. Commits record actual work dates. The course timeline is a plan, not evidence that work occurred in earlier weeks.
