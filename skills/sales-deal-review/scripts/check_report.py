#!/usr/bin/env python3
"""Check a client-side deal review report for structure and mechanical quality rules without network access."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

DIMENSIONS = ('M', 'E', 'DC', 'DP', 'P', 'I', 'CH', 'CO')
HEALTH = {'green', 'yellow', 'red', 'insufficient'}
MOMENTUM = {'accelerating', 'steady', 'stalled', 'unknown'}
STATUS = {'supported', 'uncertain', 'missing', 'negative'}
STRENGTH = ('none', 'weak', 'medium', 'strong')
TREND = {'strengthening', 'stable', 'weakening', 'unknown'}
KINDS = {'fact', 'inference', 'question', 'action'}
HEDGES = re.compile(r'似乎|可能|大概|估计|也许|或许|\b(seems?|probably|likely|maybe)\b', re.I)
PLACEHOLDERS = re.compile(r'^\s*(待定|TBD|N/?A)\s*$', re.I)
MAX_TEXT = 80


class Invalid(Exception):
    def __init__(self, path):
        self.path = path


def text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise Invalid(path)
    return value


def items(value, path):
    if not isinstance(value, list):
        raise Invalid(path)
    return value


def claim(value, path, kinds=KINDS):
    if not isinstance(value, dict) or value.get('kind') not in kinds:
        raise Invalid(path)
    text(value.get('text'), path + '/text')
    if not all(isinstance(i, str) and i for i in items(value.get('evidenceIds'), path + '/evidenceIds')):
        raise Invalid(path + '/evidenceIds')
    return value


def check(packet):
    errors = []
    def add(code, path):
        errors.append({'code': code, 'path': path})
    try:
        report = packet['report']
        known = packet.get('evidenceIds')
        if known is not None and not all(isinstance(i, str) for i in items(known, '$/evidenceIds')):
            raise Invalid('$/evidenceIds')
        overview = report['overview']
        if overview.get('health') not in HEALTH:
            raise Invalid('$/report/overview/health')
        if overview.get('momentum') not in MOMENTUM:
            raise Invalid('$/report/overview/momentum')
        claims = [(claim(c, f'$/report/overview/claims/{n}'), f'$/report/overview/claims/{n}')
                  for n, c in enumerate(items(overview.get('claims'), '$/report/overview/claims'))]
        dims, where = {}, {}
        for n, d in enumerate(items(report.get('dimensions'), '$/report/dimensions')):
            path = f'$/report/dimensions/{n}'
            if not isinstance(d, dict) or d.get('status') not in STATUS or d.get('strength') not in STRENGTH \
                    or d.get('trend') not in TREND:
                raise Invalid(path)
            if d.get('key') not in DIMENSIONS or d['key'] in dims:
                add('DIMENSION_COVERAGE', path + '/key')
                continue
            dims[d['key']], where[d['key']] = d, path
            claims += [(claim(c, f'{path}/claims/{i}'), f'{path}/claims/{i}')
                       for i, c in enumerate(items(d.get('claims'), path + '/claims'))]
            for i, gap in enumerate(items(d.get('gaps', []), path + '/gaps')):
                if PLACEHOLDERS.match(text(gap, f'{path}/gaps/{i}')):
                    add('PLACEHOLDER_TEXT', f'{path}/gaps/{i}')
            if (d['status'] == 'missing') != (d['strength'] == 'none'):
                add('STRENGTH_STATUS_MISMATCH', path)
        if set(dims) != set(DIMENSIONS):
            add('DIMENSION_COVERAGE', '$/report/dimensions')
        notes = []
        risks = items(report.get('risks'), '$/report/risks')
        if len(risks) > 3:
            add('RISK_LIMIT', '$/report/risks')
        for n, r in enumerate(risks):
            path = f'$/report/risks/{n}'
            claims.append((claim(r, path), path))
            if not all(isinstance(r.get(k), str) and r[k].strip() for k in ('impact', 'watchFor', 'mitigation')):
                add('RISK_INCOMPLETE', path)
            notes += [(r[k], f'{path}/{k}') for k in ('impact', 'watchFor', 'mitigation') if isinstance(r.get(k), str)]
        coaching = items(report.get('coaching'), '$/report/coaching')
        if not 4 <= len(coaching) <= 5:
            add('COACHING_COUNT', '$/report/coaching')
        claims += [(claim(c, f'$/report/coaching/{n}', {'question'}), f'$/report/coaching/{n}')
                   for n, c in enumerate(coaching)]
        actions = items(report.get('actions'), '$/report/actions')
        if len(actions) != 3:
            add('ACTION_COUNT', '$/report/actions')
        gaps = set()
        for n, a in enumerate(actions):
            path = f'$/report/actions/{n}'
            if not isinstance(a, dict):
                raise Invalid(path)
            claims.append((claim(a.get('claim'), path + '/claim', {'action'}), path + '/claim'))
            try:
                due = date.fromisoformat(a.get('dueDate')) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', a['dueDate'])
            except (TypeError, ValueError):
                due = None
            if not due or a.get('gap') not in DIMENSIONS or not all(
                    isinstance(a.get(k), str) and a[k].strip() for k in ('owner', 'deliverable')):
                add('ACTION_INCOMPLETE', path)
            else:
                gaps.add(a['gap'])
            if isinstance(a.get('deliverable'), str):
                notes.append((a['deliverable'], path + '/deliverable'))
        stage = overview.get('stageAlignment')
        if not isinstance(stage, dict) or not all(isinstance(stage.get(k), str) and stage[k].strip()
                                                  for k in ('crmStage', 'supportedStage')) \
                or not isinstance(stage.get('unmetCriteria'), list):
            add('STAGE_ALIGNMENT_MISSING', '$/report/overview/stageAlignment')
            stage = None
    except Invalid as error:
        return {'ok': False, 'errors': [{'code': 'REPORT_INVALID', 'path': error.path}]}
    except (KeyError, TypeError, AttributeError):
        return {'ok': False, 'errors': [{'code': 'REPORT_INVALID', 'path': '$'}]}

    for c, path in claims:
        if c['kind'] == 'fact':
            if not c['evidenceIds']:
                add('FACT_WITHOUT_EVIDENCE', path)
            if HEDGES.search(c['text']):
                add('HEDGE_IN_FACT', path + '/text')
        if PLACEHOLDERS.match(c['text']):
            add('PLACEHOLDER_TEXT', path + '/text')
        if known is not None and set(c['evidenceIds']) - set(known):
            add('UNKNOWN_EVIDENCE_ID', path + '/evidenceIds')
    for value, path in [(c['text'], p + '/text') for c, p in claims] + notes:
        if len(value.strip()) > MAX_TEXT:
            add('TEXT_TOO_LONG', path)
    for key, d in dims.items():
        cited = {i for c in d['claims'] if c['kind'] == 'fact' for i in c['evidenceIds']}
        if d['strength'] == 'strong' and len(cited) < 2:
            add('STRENGTH_UNSUPPORTED', where[key])
    if set(dims) == set(DIMENSIONS):
        weakest = {k for k, d in dims.items() if d['status'] in ('missing', 'negative')}
        if not weakest:
            pending = {k: STRENGTH.index(d['strength']) for k, d in dims.items() if d['status'] == 'uncertain'}
            weakest = {k for k, v in pending.items() if v == min(pending.values(), default=None)}
        if weakest and gaps and not weakest & gaps:
            add('WEAKEST_NOT_ADDRESSED', '$/report/actions')
        solid = [k for k, d in dims.items() if d['status'] == 'supported' and STRENGTH.index(d['strength']) >= 2]
        has_fact = any(c['kind'] == 'fact' and c['evidenceIds'] for c, _ in claims)
        if overview['health'] == 'green' and (
                len(solid) < 5 or any(dims[k]['status'] in ('missing', 'negative') for k in ('E', 'CH'))
                or (stage and stage['unmetCriteria'])) or (overview['health'] != 'insufficient' and not has_fact):
            add('HEALTH_UNSUPPORTED', '$/report/overview/health')
    return {'ok': not errors, 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.file.read_text(encoding='utf-8') if args.file else sys.stdin.read())
        verdict = check(packet) if isinstance(packet, dict) else {
            'ok': False, 'errors': [{'code': 'REPORT_INVALID', 'path': '$'}]}
    except (OSError, ValueError, RecursionError):
        verdict = {'ok': False, 'errors': [{'code': 'INPUT_UNREADABLE', 'path': '$'}]}
    print(json.dumps(verdict, ensure_ascii=False))
    sys.exit(0 if verdict['ok'] else 1)
