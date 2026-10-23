"""Explicit opt-in paid evaluation: python -m evaluation.live.

Separate evidence from the fixed offline run. Never print credentials or raw errors.
"""
import argparse
import csv
import json
import time
from collections import defaultdict
from datetime import datetime
from urllib.error import HTTPError

from app.engine import HK, ROOT
from app.llm import Bailian, load_env
from evaluation.run import check


class ObservedBailian(Bailian):
    def __init__(self):
        super().__init__()
        # Invoking this module explicitly opts into a bounded live evaluation.
        self.enabled = True
        self.limit = 50
        self.failures = []

    def complete(self, instruction, payload):
        try:
            return super().complete(instruction, payload)
        except Exception as exc:
            failure = {'type': type(exc).__name__}
            if isinstance(exc, HTTPError):
                failure['http_status'] = exc.code
            self.failures.append(failure)
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--failed', action='store_true', help='Retest only failed cases from live-results.csv; preserve the initial run')
    parser.add_argument('--case', dest='case_ids', action='append', help='Run a selected case ID; repeat for multiple cases')
    args = parser.parse_args()
    load_env()
    model = ObservedBailian()
    if not model.key:
        raise SystemExit('No local API key configured. No live tests run.')
    cases = json.loads((ROOT / 'evaluation/cases.json').read_text())
    prefix = 'live'
    if args.failed:
        with (ROOT / 'evaluation/live-results.csv').open(newline='', encoding='utf-8') as f:
            failed = {row['Case'] for row in csv.DictReader(f) if row['Pass/Fail'] == 'FAIL'}
        cases = [case for case in cases if case['id'] in failed]
        prefix = 'live-retest'
    if args.case_ids:
        cases = [case for case in cases if case['id'] in args.case_ids]
        prefix = 'live-focused'
    if not cases:
        raise SystemExit('No failed cases to retest.')
    stats = defaultdict(lambda: [0, 0])
    records = []
    for case in cases:
        started = time.monotonic()
        outputs, errors = check(case, model)
        for turn in outputs:
            # Safety gates intentionally run before any model call. Other turns
            # must actually use Bailian; a usable fallback is not a live pass.
            if turn.get('notice') or turn['mode'] == 'hybrid':
                errors.append('Live model unavailable or response rejected')
            if turn['kind'] == 'recommend' and turn['mode'] != 'bailian':
                errors.append('Recommendation used fallback')
        stats[case['group']][0] += not errors
        stats[case['group']][1] += 1
        records.append({'Case': case['id'], 'Group': case['group'],
                        'Question': ' | '.join(case['turns']),
                        'System output': json.dumps(outputs, ensure_ascii=False),
                        'Pass/Fail': 'FAIL' if errors else 'PASS',
                        'Notes': '; '.join(errors) or 'Live automated assertions passed; human quality review still required.'})
        print(f"{case['id']}: {'FAIL: ' + '; '.join(errors) if errors else 'PASS'} ({time.monotonic() - started:.1f}s)", flush=True)
    with (ROOT / f'evaluation/{prefix}-results.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    summary = {'run_at': datetime.now(HK).isoformat(), 'mode': 'live', 'model': model.model,
               'data': 'synthetic', 'groups': dict(stats), 'attempted_calls': model.calls,
               'call_limit': model.limit, 'api_failures': model.failures, 'case_ids': [case['id'] for case in cases],
               'limits': 'Automated assertions with live parsing/ranking; synthetic data. No independent human quality review or shared-credit balance measurement. Safety refusals bypass the model by design.'}
    (ROOT / f'evaluation/{prefix}-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)
    raise SystemExit(any(row['Pass/Fail'] == 'FAIL' for row in records))


if __name__ == '__main__':
    main()
