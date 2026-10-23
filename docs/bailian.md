# Sponsored Alibaba Cloud Bailian access

Configuration source: the course Ed announcement excerpt supplied by the user on 23 October 2026. A group key was subsequently added locally by the user and tested without including it in source or test reports. See `evaluation/live-summary.json` for actual live test results.

| Setting | Course-provided value |
| --- | --- |
| Plan | Aliyun Bailian Token Plan Team Edition |
| Shared group quota | 25,000 credits |
| Usage | Course app integration and code agents, course-related work only |
| OpenAI-compatible base URL | `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1` |
| Anthropic-compatible URL | `https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic` |
| Distribution | Email around 20 October |
| First batch expiry | 19 November 2026 |
| Local model choice | `qwen3.8-flash`, selected from announcement's listed models |

Announcement estimates per 25,000 credits: `deepseek-v4.1-flash` 100-125M tokens, `deepseek-v4-pro` 12-25M, `qwen3.8-flash` 150-250M, `qwen3.7-plus` 50-80M, `qwen3.8-max` 3.5-5M. These are the announcement's estimates, not guarantees or measurements by this app. Check actual shared usage through course guidance; the app does not query credit balance.

Keep secrets in ignored `.env`, never in source code, screenshots, commits or frontend configuration. Notify the TA group if a key leaks. Excessive concurrency may cause suspension. This adapter serializes calls, limits attempted requests per process, bounds output and does not retry automatically. Other group members and coding agents consume the same pool.

Pi setup in the announcement uses `/login` → API key → Qwen Token Plan CN → enter key → `/model`. This app instead sends OpenAI-compatible requests to `/chat/completions` with Bearer authentication and JSON-object output. Confirm model compatibility with one controlled live test before evaluation.

For live verification:

1. Configure `.env` as explained in README. Do not paste the key into this document.
2. Ask “At Main Library, cheap vegetarian lunch” at the demo lunchtime.
3. Confirm that the page reports Bailian model + fixed-data filters. Offline/hybrid mode means the complete live path has not passed.
4. Re-run the 20 cases manually in live mode and record each output, mode, outcome and reviewer notes. Check extracted context, constraints, refusal and unsupported wording. Fixed offline results remain separate.
5. Check the group credit dashboard after a small batch. Ask the TAs about issues/top-ups; do not automatically increase concurrency or retry.

Public references: [OpenAI-compatible request format](https://help.aliyun.com/en/model-studio/qwen-api-via-openai-chat-completions), [course-linked Codex guide](https://docs.bailian.console.aliyun.com/en/model-studio/codex), [Claude Code](https://docs.bailian.console.aliyun.com/en/model-studio/claude-code), [Cursor](https://docs.bailian.console.aliyun.com/en/model-studio/cursor), [Hermes](https://docs.bailian.console.aliyun.com/en/model-studio/hermes-agent). The Codex page could not be fetched successfully during this run; the course excerpt supplies the needed endpoint. These agent guides are not required to launch the demo.
