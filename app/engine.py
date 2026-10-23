"""Fixed-data recommendation pipeline. The model cannot bypass eligibility rules."""
import heapq
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/canteens.json').read_text())
VENUES = DATA['canteens']
EDGES = json.loads((ROOT / 'data/walks.json').read_text())['edges']
BUILDINGS = sorted({v for a, b, _ in EDGES for v in (a, b)})
HK = timezone(timedelta(hours=8))
ALIASES = {'Main Library': ['main library', 'library'], 'Main Building': ['main building'],
           'Union Building': ['union building', 'union'], 'Centennial Campus': ['centennial campus', 'centennial'],
           'Chong Yuet Ming': ['chong yuet ming', 'cym']}
CUISINES = {'rice', 'noodles', 'coffee', 'salad', 'western', 'chinese', 'sandwich'}
TAGS = {'spicy', 'quiet'}


def minute(value):
    h, m = map(int, value.split(':'))
    return h * 60 + m


def is_open(venue, at):
    now = at.hour * 60 + at.minute
    key = 'weekday' if at.weekday() < 5 else 'weekend'
    previous = at - timedelta(days=1)
    prev_key = 'weekday' if previous.weekday() < 5 else 'weekend'
    for start, end in venue['hours'][key]:
        a, b = minute(start), minute(end)
        if a < b and a <= now < b or a > b and now >= a:
            return True
    return any(minute(a) > minute(b) and now < minute(b) for a, b in venue['hours'][prev_key])


def walk(origin, destination):
    pending = [(0, origin, [origin])]
    visited = set()
    while pending:
        cost, current, path = heapq.heappop(pending)
        if current == destination:
            return cost, path
        if current in visited:
            continue
        visited.add(current)
        for a, b, minutes in EDGES:
            nxt = b if a == current else a if b == current else None
            if nxt and nxt not in visited:
                heapq.heappush(pending, (cost + minutes, nxt, path + [nxt]))
    return None, []


def fallback_parse(text, context):
    t = text.lower()
    out = {}
    for building, aliases in ALIASES.items():
        if any(alias in t for alias in aliases):
            out['building'] = building
            break
    if re.search(r"\b(i(?:'m| am)|at|from)\s+(?:the\s+)?(?:[a-z]+\s+)?(?:building|hall|tower)\b", t) and 'building' not in out:
        out['building'] = None
    if 'vegan' in t:
        out['diet'] = 'vegan'
    elif re.search(r'\b(vegetarian|veggie|veg)\b', t):
        out['diet'] = 'vegetarian'
    if re.search(r'(not vegetarian|no diet restriction|any diet|remove diet)', t):
        out['diet'] = None
    for cuisine in sorted(CUISINES):
        if re.search(r'\b' + cuisine + r'\b', t):
            out['cuisine'] = cuisine
    if 'any cuisine' in t:
        out['cuisine'] = None
    for tag in TAGS:
        if tag in t:
            out[tag] = not bool(re.search(r'(?:not|no|without)\s+(?:too\s+)?' + tag, t))
    budget = re.search(r'(?:under|below|budget(?: of)?|up to|maximum|max)\s*(?:hk\$|\$|hkd\s*)?(\d+)', t)
    if budget:
        out['budget'] = int(budget[1])
    elif 'cheaper' in t:
        out['budget'] = max(0, context.get('budget', 40) - 10)
    elif 'cheap' in t or 'not too expensive' in t:
        out['budget'] = 35
    if 'any budget' in t or 'remove budget' in t:
        out['budget'] = None
    duration = re.search(r'(\d+)\s*(?:minutes|mins|min)\b', t)
    if duration:
        out['time_limit'] = int(duration[1])
    if 'no time limit' in t:
        out['time_limit'] = None
    clock = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', t)
    if clock and 1 <= int(clock[1]) <= 12 and int(clock[2] or 0) < 60:
        hour = int(clock[1]) % 12 + (12 if clock[3] == 'pm' else 0)
        out['clock'] = f'{hour:02}:{int(clock[2] or 0):02}'
    if 'now' in t:
        out['clock'] = None
    return out


def validate_patch(patch):
    if not isinstance(patch, dict):
        raise ValueError('Bad filters')
    valid = {}
    for key, value in patch.items():
        if key not in {'building', 'diet', 'cuisine', 'budget', 'time_limit', 'spicy', 'quiet', 'clock'}:
            continue
        ok = value is None
        if key == 'building': ok |= value in BUILDINGS if isinstance(value, str) else False
        elif key == 'diet': ok |= value in ('vegetarian', 'vegan')
        elif key == 'cuisine': ok |= isinstance(value, str) and value in CUISINES
        elif key in ('budget', 'time_limit'): ok |= type(value) is int and 0 <= value <= 10000
        elif key in ('spicy', 'quiet'): ok |= type(value) is bool
        elif key == 'clock': ok |= isinstance(value, str) and bool(re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value))
        if not ok:
            raise ValueError('Invalid filter value')
        valid[key] = value
    return valid


def blocked(text):
    t = text.lower()
    if re.search(r'\b(allerg\w*|medical|diabet\w*|anaphyl\w*|celiac|coeliac)\b', t):
        return 'I cannot assess allergies or medical dietary needs. Please check ingredients and cross-contact directly with the vendor.'
    if re.search(r'\b(deliver\w*|book\w*|reserv\w*)\b|off[- ]campus|outside campus', t):
        return 'I can only suggest on-campus demo canteens and building walking estimates. Delivery, booking and off-campus dining are outside this project.'
    return None


def chat(text, state, at=None, llm=None):
    at = at or datetime.now(HK)
    context = dict(state.get('context', {}))
    result = {'context': context, 'recommendations': [], 'mode': 'offline', 'at': at.isoformat(), 'synthetic': True}
    refusal = blocked(text)
    if refusal:
        return dict(result, kind='refusal', message=refusal)
    if 'high-end' in text.lower() and ('cheap' in text.lower() or 'very' in text.lower()):
        return dict(result, kind='clarify', message='Should I prioritize a low price or high-end dining? The demo dataset only covers casual campus meals.')
    if re.search(r'lobster|fine dining|high.end', text, re.I):
        return dict(result, kind='no_match', message='No matching high-end or lobster venue exists in this fixed demo dataset. Try a campus meal or change the cuisine.')
    patch = fallback_parse(text, context)
    if llm:
        try:
            parsed = llm.complete(
                'Extract only explicitly requested filter changes as a JSON object. Omit unchanged fields; null clears a field. '
                'Keys: building (one of supplied buildings), diet (vegetarian/vegan/null), cuisine (one of supplied cuisines/null), '
                'budget (maximum HKD integer), time_limit (total minutes integer), spicy/quiet (boolean), clock (HH:MM/null). '
                'Cheap means budget 35. Cheaper means reduce prior budget (default 40) by 10. Do not invent a location.',
                {'message': text, 'context': context, 'buildings': BUILDINGS, 'cuisines': sorted(CUISINES)})
            patch = {**validate_patch(parsed), **patch}
            result['mode'] = 'bailian'
        except Exception:
            result['notice'] = 'Model unavailable or response invalid; using the offline parser.'
    patch = validate_patch(patch)
    for key, value in patch.items():
        if value is None:
            context.pop(key, None)
        else:
            context[key] = value
    state['context'] = context
    result['context'] = context
    if context.get('clock'):
        h, m = map(int, context['clock'].split(':'))
        at = at.replace(hour=h, minute=m)
        result['at'] = at.isoformat()
    if not context.get('building'):
        state['location_prompts'] = state.get('location_prompts', 0) + 1
        if state['location_prompts'] <= 2:
            return dict(result, kind='clarify', message='Which building are you starting from? Choose Main Library, Main Building, Union Building, Chong Yuet Ming or Centennial Campus.')
        return dict(result, kind='clarify', message='I need a supported starting building to estimate your walk. Choose one above, or start a new chat.')
    if 'healthy' in text.lower() and not context.get('diet'):
        return dict(result, kind='clarify', message='By healthy, do you mean vegetarian or a particular cuisine? I can match menu tags, but cannot give medical or nutrition advice.')
    candidates = []
    for venue in VENUES:
        minutes, path = walk(context['building'], venue['building'])
        if not is_open(venue, at) or minutes is None:
            continue
        if context.get('diet') and context['diet'] not in venue['tags']:
            continue
        if context.get('cuisine') and context['cuisine'] not in venue['cuisine']:
            continue
        if any(context.get(tag) is True and tag not in venue['tags'] or context.get(tag) is False and tag in venue['tags'] for tag in TAGS):
            continue
        if 'budget' in context and venue['price_min'] > context['budget']:
            continue
        # Conservative two-way walk plus a fixed 10-minute meal allowance.
        if minutes > 15 or 'time_limit' in context and minutes * 2 + 10 > context['time_limit']:
            continue
        reason = f"From HK${venue['price_min']}; {minutes} min walk."
        if context.get('diet'):
            reason += f" {context['diet'].capitalize()} menu tag."
        candidates.append(dict(venue, walk_minutes=minutes, route=' → '.join(path), reason=reason))
    candidates.sort(key=lambda v: (v['price_min'], v['walk_minutes']))
    if not candidates:
        return dict(result, kind='no_match', message='No canteen matches the current demo hours and filters. Try a different time, budget or cuisine; I will not silently relax your restrictions.')
    if result['mode'] == 'bailian':
        try:
            ranked = llm.complete(
                'Rank only supplied eligible candidate IDs by user preferences. Return {"ids": [id,...], "reasons": {id: short reason}}. '
                'Reasons must use only supplied prices, walk minutes and menu tags. Never claim allergy safety or current real-world accuracy.',
                {'context': context, 'candidates': [{k: v[k] for k in ('id', 'price_min', 'walk_minutes', 'tags', 'cuisine')} for v in candidates]})
            ids, reasons = ranked.get('ids'), ranked.get('reasons', {})
            eligible = {v['id']: v for v in candidates}
            if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in eligible for i in ids) or len(set(ids)) != len(ids):
                raise ValueError('Invalid ranked IDs')
            if not isinstance(reasons, dict) or any(not isinstance(reasons.get(i), str) or not 1 <= len(reasons[i]) <= 240 for i in ids):
                raise ValueError('Invalid reasons')
            ordered = [eligible[i] for i in ids] + [v for v in candidates if v['id'] not in ids]
            for venue in ordered:
                if venue['id'] in reasons:
                    venue['model_reason'] = reasons[venue['id']]
            candidates = ordered
        except Exception:
            result['mode'] = 'hybrid'
            result['notice'] = 'Model ranking unavailable or invalid; using price and walk-time ordering.'
    return dict(result, kind='recommend', message=f"Found {min(3, len(candidates))} matching demo option(s). Prices are starting prices; not every dish fits the budget.", recommendations=candidates[:3])
