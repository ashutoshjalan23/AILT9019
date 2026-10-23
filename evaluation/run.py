"""Reproducible OFFLINE fixtures, not a live-model or human usability evaluation."""
import csv
import json
from collections import defaultdict
from datetime import datetime
from app.engine import HK, ROOT, chat, is_open


def check(case):
    state, outputs, errors = {}, [], []
    for index, text in enumerate(case['turns']):
        result = chat(text, state, datetime(2026, 10, 23, 12, 30, tzinfo=HK))
        outputs.append(result)
        if 'kinds' in case and result['kind'] != case['kinds'][index]:
            errors.append(f'Turn {index + 1}: expected {case["kinds"][index]}')
        context = result['context']
        for venue in result['recommendations']:
            at = datetime.fromisoformat(result['at'])
            if not is_open(venue, at): errors.append('Closed venue returned')
            if context.get('diet') and context['diet'] not in venue['tags']: errors.append('Diet mismatch')
            if 'budget' in context and venue['price_min'] > context['budget']: errors.append('Budget mismatch')
            if context.get('cuisine') and context['cuisine'] not in venue['cuisine']: errors.append('Cuisine mismatch')
            for tag in ('quiet','spicy'):
                if tag in context and context[tag] != (tag in venue['tags']): errors.append('Tag mismatch')
            if not venue['reason'] or not venue['route'] or venue['walk_minutes'] > 15: errors.append('Missing reason/route or walk too long')
            if 'time_limit' in context and venue['walk_minutes'] * 2 + 10 > context['time_limit']: errors.append('Time constraint violated')
    result = outputs[-1]
    if result['kind'] != case['kind']: errors.append('Wrong final outcome')
    if any(result['context'].get(k) != v for k,v in case.get('context',{}).items()): errors.append('Wrong merged context')
    if 'expected_ids' in case and {v['id'] for v in result['recommendations']} != set(case['expected_ids']): errors.append('Unexpected venue selection')
    if case.get('contains','') not in result['message']: errors.append('Missing expected explanation')
    if result['kind'] == 'recommend' and not 1 <= len(result['recommendations']) <= 3: errors.append('Wrong result count')
    if result['kind'] in ('refusal','no_match','clarify') and result['recommendations']: errors.append('Unsafe recommendations')
    return outputs, errors


def main():
    cases = json.loads((ROOT / 'evaluation/cases.json').read_text())
    stats = defaultdict(lambda: [0,0])
    records = []
    for case in cases:
        outputs, errors = check(case)
        stats[case['group']][0] += not errors
        stats[case['group']][1] += 1
        records.append({'Case':case['id'], 'Group':case['group'], 'Question':' | '.join(case['turns']),
                        'System output':json.dumps(outputs, ensure_ascii=False), 'Pass/Fail':'FAIL' if errors else 'PASS',
                        'Notes':'; '.join(errors) or 'Offline synthetic fixture only; all listed assertions passed.'})
    with (ROOT / 'evaluation/results.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    summary = {'run_at':datetime.now(HK).isoformat(), 'mode':'offline', 'data':'synthetic', 'groups':dict(stats),
               'limits':'Automated fixture assertions only. No live Bailian, public-data, peer-review or manual usability validation.'}
    (ROOT / 'evaluation/summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    raise SystemExit(any(r['Pass/Fail']=='FAIL' for r in records))


if __name__ == '__main__': main()
