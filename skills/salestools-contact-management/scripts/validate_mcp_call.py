#!/usr/bin/env python3
"""Validate host-supplied MCP metadata, calls and results; never dispatch or retry."""
import argparse
import json
from pathlib import Path
import sys

READ_ONLY = {
    'get_company_profile', 'search_contacts', 'get_contact', 'ask_contacts',
    'get_company_research', 'get_company_research_status', 'list_company_research_versions',
    'get_company_research_evidence', 'get_company_visit', 'get_company_visit_evidence',
    'get_company_comparison', 'get_company_comparison_evidence', 'get_contact_import',
    'get_assessment_status', 'get_assessment_report',
}
ID_KEYS = {
    'entity_id': {'entity_id', 'source_id', 'target_id'},
    'organization_id': {'entity_id', 'organization_id'},
    'source_id': {'entity_id', 'source_id', 'target_id'},
    'target_id': {'entity_id', 'source_id', 'target_id'},
    'base_version_id': {'version_id'},
}
for _key in ('dossier_id', 'version_id', 'run_id', 'brief_id', 'comparison_id',
             'assessment_id', 'import_id', 'claim_id', 'relation_id', 'file_id', 'credit_code'):
    ID_KEYS[_key] = {_key}
ID_KEYS['run_id'].add('research_run_id')


class Invalid(Exception):
    def __init__(self, code, path='$'):
        self.code, self.path = code, path


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def payload(response):
    if not isinstance(response, dict) or response.get('isError') is True:
        raise Invalid('MCP_ERROR')
    data = response.get('structuredContent')
    if data is None:
        texts = [c.get('text', '') for c in response.get('content', []) if c.get('type') == 'text']
        try:
            data = json.loads(texts[0]) if len(texts) == 1 else None
        except (ValueError, TypeError):
            data = None
    if not isinstance(data, dict):
        raise Invalid('UNSTRUCTURED_RESULT')
    if data.get('error_code') or data.get('status') in ('failed', 'cancelled') or data.get('source_status') == 'failed':
        raise Invalid('BUSINESS_FAILED')
    return data


def schema_check(value, schema, path):
    from jsonschema.validators import validator_for
    if not isinstance(schema, dict):
        raise Invalid('SCHEMA_REQUIRED', path)
    # The helper is offline: allow local JSON pointers only, never resolve remote files/URLs.
    for obj in objects(schema):
        for key in ('$ref', '$dynamicRef', '$recursiveRef'):
            if key in obj and not str(obj[key]).startswith('#'):
                raise Invalid('EXTERNAL_SCHEMA_REF', path)
    try:
        cls = validator_for(schema)
        cls.check_schema(schema)
        errors = list(cls(schema, format_checker=cls.FORMAT_CHECKER).iter_errors(value))
    except Exception:
        raise Invalid('INVALID_SCHEMA', path) from None
    if errors:
        raise Invalid('SCHEMA_MISMATCH', path + ''.join('/' + str(p) for p in errors[0].absolute_path))


def history_data(packet):
    result = []
    for entry in packet.get('history', []):
        try:
            data = payload(entry['response'])
            check_binding(entry['call'], data)
            result.append((entry, data))
        except (Invalid, KeyError):
            continue
    return result


def check_binding(call, data):
    args = call['arguments']
    for key in ('run_id', 'brief_id', 'comparison_id', 'dossier_id', 'version_id', 'import_id', 'assessment_id'):
        if key in args and key in data and args[key] != data[key]:
            raise Invalid('RESULT_ID_MISMATCH', '$/response/' + key)
    if call['name'] == 'get_contact' and data.get('entity', {}).get('entity_id') != args.get('entity_id') and data.get('found') is not False:
        raise Invalid('RESULT_ID_MISMATCH', '$/response/entity/entity_id')


def request(packet):
    call = packet['call']; name = call['name']; args = call['arguments']
    tools = packet['tools']
    if isinstance(tools, dict):
        tools = tools['tools']  # tools/list result
    matches = [t for t in tools if t.get('name') == name]
    if len(matches) != 1:
        raise Invalid('TOOL_NOT_AVAILABLE')
    tool = matches[0]
    schema_check(args, tool.get('inputSchema'), '$/call/arguments')
    if packet.get('constraints', {}).get('no_save') and name not in READ_ONLY:
        raise Invalid('NO_SAVE_VIOLATION')
    data = history_data(packet)
    known = [o for _, d in data for o in objects(d)]
    for key, aliases in ID_KEYS.items():
        if key not in args:
            continue
        if not any(o.get(k) == args[key] for o in known for k in aliases):
            raise Invalid('ID_NOT_FROM_HISTORY', '$/call/arguments/' + key)
    if name == 'compare_company_opportunities':
        for index, company in enumerate(args.get('companies', [])):
            for key, value in company.items():
                if key in ID_KEYS and not any(o.get(k) == value for o in known for k in ID_KEYS[key]):
                    raise Invalid('ID_NOT_FROM_HISTORY', '$/call/arguments/companies/' + str(index) + '/' + key)
    if args.get('organization_id') and not any(o.get('entity_id') == args['organization_id'] and o.get('label') == 'Organization' for o in known):
        raise Invalid('ORGANIZATION_TYPE_NOT_VERIFIED')
    if name == 'start_company_research' and args.get('mode') == 'initial':
        if not any(o.get('credit_code') == args.get('credit_code') and o.get('legal_name') == args.get('legal_name') for o in known):
            raise Invalid('COMPANY_NAME_CODE_MISMATCH')
    if name == 'get_company_research' and 'version_id' in args and 'dossier_id' in args:
        if not any(d.get('dossier_id') == args['dossier_id'] and
                   (d.get('version_id') == args['version_id'] or any(v.get('version_id') == args['version_id'] for v in d.get('items', []))) for _, d in data):
            raise Invalid('RESEARCH_VERSION_DOSSIER_MISMATCH')
    if args.get('include_unverified') and (args.get('mode', 'keyword') != 'keyword' or not args.get('query', '').strip()):
        raise Invalid('UNVERIFIED_SEARCH_REQUIRES_KEYWORD_QUERY')
    if name == 'discover_contacts':
        if args.get('web_offset', 0) > 0 and not args.get('web_snapshot_id'):
            raise Invalid('WEB_SNAPSHOT_REQUIRED')
        if args.get('web_offset', 0) > 0:
            if args.get('source', 'web') != 'web':
                raise Invalid('WEB_PAGINATION_REQUIRES_WEB_SOURCE')
            if not any(d.get('web_page', {}).get('snapshot_id') == args['web_snapshot_id']
                       and d['web_page'].get('next_offset') == args['web_offset']
                       and e['call']['arguments'].get('query') == args.get('query')
                       and e['call']['arguments'].get('region_hint') == args.get('region_hint') for e, d in data):
                raise Invalid('WEB_PAGE_CONTEXT_MISMATCH')
        for pair in args.get('zoho_account_records', []):
            if pair not in packet.get('confirmations', {}).get('crm_accounts', []):
                raise Invalid('CRM_USER_SELECTION_REQUIRED')
            if pair['connection_id'] not in args.get('zoho_accounts', []):
                raise Invalid('CRM_CONNECTION_PAIR_MISMATCH')
            if not any(o.get('connection_id') == pair['connection_id'] and
                       (o.get('account_id') == pair['account_id'] or
                        any(c.get('account_id') == pair['account_id'] for c in o.get('candidates', []))) for o in known):
                raise Invalid('CRM_PAIR_NOT_FROM_HISTORY')
    if name == 'get_company_research_evidence' and 'claim_id' in args and 'product' in args:
        raise Invalid('CLAIM_PRODUCT_EXCLUSIVE')
    if name == 'get_company_research' and ('dossier_id' in args) == ('credit_code' in args):
        raise Invalid('RESEARCH_IDENTITY_EXCLUSIVE')
    if name == 'start_company_research' and args.get('mode') in ('continue', 'refresh'):
        latest = [d for e, d in data if e['call']['name'] == 'get_company_research'
                  and 'version_id' not in e['call']['arguments'] and d.get('dossier_id') == args.get('dossier_id')]
        if not latest or latest[-1].get('version_id') != args.get('base_version_id'):
            raise Invalid('LATEST_BASE_NOT_VERIFIED')
    for entry in packet.get('history', []):
        old = entry['call']
        if args.get('operation_id') and old.get('arguments', {}).get('operation_id') == args['operation_id'] and old != call:
            raise Invalid('OPERATION_ID_REUSED_WITH_DIFFERENT_REQUEST')
    return tool


def result(packet, tool):
    data = payload(packet['response']); name = packet['call']['name']; args = packet['call']['arguments']
    if tool.get('outputSchema') is not None:
        schema_check(data, tool['outputSchema'], '$/response/structuredContent')
    check_binding(packet['call'], data)
    if data.get('found') is False:
        return 'not_found'
    required = {
        'get_company_profile': ('candidates', 'source_status', 'basic_profile'),
        'search_contacts': ('items',), 'get_contact': ('entity',),
        'get_company_research': ('dossier_id', 'version_id', 'product_keys'),
        'get_company_research_status': ('run_id', 'status'),
        'start_company_research': ('run_id', 'dossier_id', 'status'),
        'prepare_company_visit': ('brief_id', 'status'),
        'compare_company_opportunities': ('comparison_id', 'status'),
        'get_company_visit': ('brief_id', 'status', 'result'),
        'get_company_comparison': ('comparison_id', 'status', 'result'),
        'discover_contacts': ('companies', 'warnings'), 'ask_contacts': ('status',),
    }
    if name not in required and tool.get('outputSchema') is None:
        raise Invalid('OUTPUT_CONTRACT_UNAVAILABLE')
    if any(k not in data for k in required.get(name, ())):
        raise Invalid('RESULT_FIELDS_MISSING')
    for key in ('items', 'candidates', 'companies', 'product_keys'):
        if key in data and not isinstance(data[key], list):
            raise Invalid('RESULT_COLLECTION_TYPE', '$/response/' + key)
    if name == 'search_contacts' and 'next_offset' not in data:
        total = data.get('total')
        if type(total) is not int or total < 0:
            raise Invalid('RESULT_FIELDS_MISSING', '$/response/total')
        if total > args.get('offset', 0) + len(data['items']):
            raise Invalid('PAGINATION_CURSOR_MISSING')
    for key in ('run_id', 'brief_id', 'comparison_id', 'dossier_id', 'version_id', 'status'):
        if data.get(key) is None and key not in required.get(name, ()):
            continue
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            raise Invalid('RESULT_IDENTIFIER_TYPE', '$/response/' + key)
    if data.get('status') in ('queued', 'running', 'processing', 'extracting', 'parsing', 'waiting_research', 'generating'):
        return 'waiting'
    if data.get('status') in ('needs_confirmation', 'ready_for_review', 'clarify') or data.get('zoho', {}).get('status') == 'needs_confirmation':
        return 'needs_confirmation'
    if name == 'get_company_profile':
        if not data['candidates']:
            return 'not_found'
        if len(data['candidates']) > 1:
            return 'needs_confirmation'
        if data['basic_profile'] is None:
            return 'partial'
    if name in ('get_company_visit', 'get_company_comparison') and (not isinstance(data.get('result'), dict) or not data['result']):
        raise Invalid('FINAL_RESULT_MISSING')
    pages = [(data, args.get('offset', 0)), (data.get('web_page', {}), args.get('web_offset', 0))]
    for field, arg in [('evidence', 'evidence_offset'), ('relations', 'relation_offset'), ('unverified_claims', 'claim_offset')]:
        pages.append((data.get('pagination', {}).get(field, {}), args.get(arg, 0)))
    pages.append((data.get('company_context', {}).get('reports', {}), args.get('report_offset', 0)))
    if any(p.get('next_offset') is not None and p['next_offset'] <= offset for p, offset in pages):
        raise Invalid('PAGINATION_NOT_ADVANCING')
    if any(o.get('warnings') or o.get('complete') is False or o.get('state') in ('partial', 'unavailable')
           or o.get('status') in ('partial', 'failed', 'insufficient') or o.get('next_offset') is not None for o in objects(data)):
        return 'partial'
    return 'validated'


def handoff(packet):
    expected = packet['handoff']; data = history_data(packet)
    profiles = [d for e, d in data if e['call']['name'] == 'get_company_profile' and d.get('source_status') == 'completed'
                and d.get('basic_profile') is not None and len(d.get('candidates', [])) == 1
                and d['candidates'][0]['credit_code'] == expected['credit_code']]
    details = [d for e, d in data if e['call']['name'] == 'get_contact']
    orgs = [d for d in details if d.get('entity', {}).get('entity_id') == expected['organization_id']
            and d['entity'].get('label') == 'Organization']
    people = [d for d in details if d.get('entity', {}).get('entity_id') == expected['entity_id']
              and d['entity'].get('label') == 'Person']
    if not profiles or not orgs or not people:
        raise Invalid('HANDOFF_RECORDS_MISSING')
    link = orgs[-1].get('company_context', {}).get('link', {})
    if link.get('state') != 'confirmed' or link.get('credit_code') != expected['credit_code'] or link.get('organization_id') != expected['organization_id']:
        raise Invalid('HANDOFF_COMPANY_NOT_CONFIRMED')
    person = people[-1]
    def evidenced_edge(detail, kind, source, target):
        return any(r.get('relation_type') == kind and r.get('source_id') == source and r.get('target_id') == target
                   and r.get('relation_id') and any(e.get('subject_id') == r['relation_id'] and e.get('evidence_id')
                                                   for e in detail.get('evidence', [])) for r in detail.get('relations', []))
    if expected.get('project_id'):
        projects = [d for d in details if d.get('entity', {}).get('entity_id') == expected['project_id']
                    and d['entity'].get('label') == 'Project']
        linked = projects and evidenced_edge(person, 'memberOf', expected['entity_id'], expected['project_id']) and \
            evidenced_edge(projects[-1], 'clientOrganization', expected['project_id'], expected['organization_id'])
    else:
        linked = evidenced_edge(person, 'worksFor', expected['entity_id'], expected['organization_id'])
    if not linked:
        raise Invalid('HANDOFF_RELATION_EVIDENCE_MISSING')
    # Employment and software deployment are separate claims; this only verifies the recorded path.
    return 'ready_with_limits'


def validate(mode, packet):
    try:
        if mode == 'handoff':
            decision = handoff(packet)
        else:
            tool = request(packet)
            decision = 'dispatch_allowed' if mode == 'request' else result(packet, tool)
        return {'ok': True, 'decision': decision,
                'limits': ['provided_artifacts_only', 'no_authentication_or_freshness_guarantee',
                           'not_proof_of_current_employment_or_software_deployment']}
    except Invalid as error:
        return {'ok': False, 'decision': 'needs_verification' if error.code.startswith('HANDOFF_') else 'blocked',
                'errors': [{'code': error.code, 'path': error.path}]}
    except (KeyError, TypeError, ValueError, AttributeError):
        return {'ok': False, 'decision': 'blocked', 'errors': [{'code': 'INVALID_ENVELOPE', 'path': '$'}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['request', 'result', 'handoff'])
    parser.add_argument('--file', help='JSON input file; defaults to stdin')
    args = parser.parse_args()
    try:
        packet = json.loads(Path(args.file).read_text() if args.file else sys.stdin.read())
        verdict = validate(args.mode, packet)
    except ImportError:
        verdict = {'ok': False, 'decision': 'blocked', 'errors': [{'code': 'INSTALL_JSONSCHEMA', 'path': '$'}]}
    except (OSError, ValueError, RecursionError):
        verdict = {'ok': False, 'decision': 'blocked', 'errors': [{'code': 'INPUT_UNREADABLE', 'path': '$'}]}
    print(json.dumps(verdict, ensure_ascii=False))
    return 0 if verdict['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
