#!/usr/bin/env python3
"""Validate MCP metadata and recorded deal review calls without network access."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

SHARED = Path(__file__).resolve().parents[2] / 'salestools-contact-management/scripts/validate_mcp_call.py'
spec = importlib.util.spec_from_file_location('salestools_shared_validation', SHARED)
shared = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(shared)
except FileNotFoundError:
    shared = None

TOOLS = {
    'connect_zoho', 'disconnect_zoho', 'search_deals', 'get_deal_review_context',
    'get_deal_review_evidence', 'open_deal_review_upload', 'upload_deal_attachment',
    'prepare_deal_review_writeback',
}
WRITEBACK_FIELDS = {'Stage', 'Amount', 'Probability', 'Closing_Date'}
AUTH_ERROR_DECISIONS = {
    'ZOHO_PERSONAL_AUTH_REQUIRED': 'reconnect_zoho',
    'ZOHO_AUTH_UNAVAILABLE': 'retry_later',
    'ZOHO_PERMISSION_DENIED': 'permission_denied',
    'ZOHO_PERSONAL_CONFIG_REQUIRED': 'contact_admin',
    'ZOHO_PERSONAL_CONFIG_INVALID': 'contact_admin',
}
class Invalid(Exception):
    def __init__(self, code):
        self.code = code


def require(condition, code):
    if not condition:
        raise Invalid(code)


def payload(response):
    try:
        return shared.payload(response)
    except shared.Invalid:
        raise Invalid('MCP_RESULT_UNVERIFIED') from None


def secure_url(value):
    if not isinstance(value, str):
        return False
    url = urlsplit(value)
    return url.scheme == 'https' and bool(url.hostname) and url.username is None and url.password is None


def result(name, args, data):
    if name == 'connect_zoho':
        status = data.get('status')
        if status == 'connected':
            return 'connected'
        require(status == 'needs_authorization' and secure_url(data.get('url')), 'RESULT_UNVERIFIED')
        return 'needs_authorization'
    if name == 'disconnect_zoho':
        require(data.get('status') == 'disconnected', 'RESULT_UNVERIFIED')
        return 'disconnected'
    if name == 'search_deals':
        items = data.get('items')
        require(isinstance(items, list) and all(item['ref']['dealId'] for item in items) and
                type(data.get('complete')) is bool and 'nextCursor' in data, 'RESULT_UNVERIFIED')
        if data.get('nextCursor'):
            require(data['nextCursor'] != args.get('cursor') and not data['complete'], 'CURSOR_UNVERIFIED')
            return 'partial'
        if not data['complete']:
            return 'partial'
        return 'candidates' if items else 'no_matches_on_page'
    if name == 'get_deal_review_context':
        require(data.get('reviewId') and data['deal']['ref']['dealId'] == args['dealId'], 'RESULT_ID_MISMATCH')
    if name in ('get_deal_review_context', 'get_deal_review_evidence'):
        require(all(isinstance(data.get(key), list) for key in ('evidence', 'attachments', 'coverage')), 'RESULT_UNVERIFIED')
        require(all(isinstance(e.get('id'), str) and e['id'] for e in data['evidence']), 'RESULT_UNVERIFIED')
        if name == 'get_deal_review_evidence' and args.get('query', {}).get('mode') == 'ids':
            require({e['id'] for e in data['evidence']} == set(args['query']['evidenceIds']), 'RESULT_ID_MISMATCH')
        if any(row.get('state') != 'complete' or row.get('nextCursor') for row in data['coverage']):
            cursor = args.get('query', {}).get('cursor')
            require(not cursor or all(row.get('nextCursor') != cursor for row in data['coverage']), 'CURSOR_UNVERIFIED')
            return 'partial'
        return 'validated'
    if name == 'open_deal_review_upload':
        require(secure_url(data.get('url')), 'RESULT_UNVERIFIED')
        return 'awaiting_original'
    if name == 'upload_deal_attachment':
        if data.get('errorCode') == 'ZOHO_UPLOAD_AUTH_REQUIRED':
            require(secure_url(data.get('authorizationUrl')), 'RESULT_UNVERIFIED')
            return 'needs_authorization'
        state = data.get('state')
        if state == 'succeeded':
            require(isinstance(data.get('attachmentId'), str) and data['attachmentId'].isdigit(), 'RESULT_UNVERIFIED')
            return 'attachment_uploaded'
        require(state in ('sending', 'failed', 'unknown') and not data.get('attachmentId'), 'RESULT_UNVERIFIED')
        return {'sending':'waiting', 'failed':'upload_failed', 'unknown':'needs_verification'}[state]
    require(name == 'prepare_deal_review_writeback', 'TOOL_NOT_SUPPORTED')
    preview = data['preview']
    require(preview.get('id') and secure_url(data.get('url')), 'RESULT_UNVERIFIED')
    if args['mode'] == 'new':
        require(preview.get('reviewId') == args['reviewId'], 'RESULT_ID_MISMATCH')
    else:
        require(preview.get('retryOperationId') == args.get('operationId'), 'RESULT_ID_MISMATCH')
    return 'needs_confirmation'


def history(packet):
    for entry in packet.get('history', []):
        try:
            call = entry['call']
            name, args = call['name'], call['arguments']
            data = payload(entry['response'])
            if name in TOOLS:
                result(name, args, data)
                yield name, args, data
        except (Invalid, KeyError, TypeError, AttributeError, ValueError):
            continue


def request(packet):
    call = packet['call']
    name, args = call['name'], call['arguments']
    tools = packet['tools']
    if isinstance(tools, dict):
        tools = tools['tools']
    matches = [tool for tool in tools if tool.get('name') == name]
    require(len(matches) == 1, 'TOOL_NOT_AVAILABLE')
    require(name in TOOLS, 'TOOL_NOT_SUPPORTED')
    tool = matches[0]
    shared.schema_check(args, tool.get('inputSchema'), '$/call/arguments')
    constraints = packet.get('constraints', {})
    confirmations = packet.get('confirmations', {})
    if constraints.get('no_save'):
        require(name not in {'open_deal_review_upload', 'upload_deal_attachment',
                             'prepare_deal_review_writeback', 'disconnect_zoho'}, 'NO_SAVE_VIOLATION')
    if name in ('open_deal_review_upload', 'upload_deal_attachment'):
        require(constraints.get('allow_attachment_upload') is True and not constraints.get('no_crm_write'), 'UPLOAD_NOT_REQUESTED')
    if name == 'connect_zoho':
        if args.get('attachmentUpload'):
            require(constraints.get('allow_attachment_upload') is True and not constraints.get('no_crm_write'), 'UPLOAD_NOT_REQUESTED')
        if args.get('writeback'):
            require(constraints.get('allow_writeback') is True and not constraints.get('no_crm_write'), 'WRITEBACK_NOT_REQUESTED')
    if name == 'prepare_deal_review_writeback':
        require(constraints.get('allow_writeback_preview') is True, 'PREVIEW_NOT_REQUESTED')
    if name == 'disconnect_zoho':
        require(constraints.get('allow_disconnect') is True, 'DISCONNECT_NOT_REQUESTED')

    past = list(history(packet))
    contexts = [data for kind, _, data in past if kind == 'get_deal_review_context']
    search_query = next((args['query'] for kind, args, _ in reversed(past) if kind == 'search_deals'), None)
    searches = [data for kind, search, data in past if kind == 'search_deals' and search['query'] == search_query]
    deal_id = args.get('dealId')
    review_id = args.get('reviewId')
    recorded = [data for data in contexts if data['reviewId'] == review_id]
    pages = recorded + [data for kind, previous, data in past
                        if kind == 'get_deal_review_evidence' and previous.get('reviewId') == review_id]
    if name == 'get_deal_review_context':
        known = {item['ref']['dealId'] for data in searches for item in data['items']}
        verified = any(data['deal']['ref']['dealId'] == deal_id for data in contexts)
        explicit = bool(deal_id) and confirmations.get('explicitDealId') == deal_id
        require(verified or deal_id in known or explicit, 'DEAL_NOT_FROM_HISTORY')
        if not verified and not explicit and (len(known) != 1 or not searches[-1]['complete']):
            require(confirmations.get('dealId') == deal_id, 'DEAL_SELECTION_REQUIRED')
    if name in ('get_deal_review_evidence', 'open_deal_review_upload'):
        require(bool(recorded), 'REVIEW_NOT_FROM_HISTORY')
    if name == 'search_deals' and args.get('cursor'):
        require(any(kind==name and previous['query']==args['query'] and data.get('nextCursor')==args['cursor']
                    for kind,previous,data in past), 'CURSOR_NOT_FROM_HISTORY')
    known_ids = {item['id'] for page in pages for item in page['evidence']}
    if name == 'get_deal_review_evidence':
        query = args['query']
        if query['mode']=='cursor':
            require(any(coverage.get('nextCursor')==query['cursor'] for page in pages for coverage in page['coverage']),
                    'CURSOR_NOT_FROM_HISTORY')
        if query['mode']=='ids':
            require(set(query['evidenceIds']) <= known_ids, 'EVIDENCE_NOT_FROM_HISTORY')
    if name == 'upload_deal_attachment':
        receipt = confirmations.get('originalReceipt', {})
        require(receipt.get('materialId')==args['materialId'] and any(
            kind=='open_deal_review_upload' and previous.get('reviewId')==receipt.get('reviewId')
            for kind,previous,_ in past), 'ORIGINAL_NOT_FROM_BROWSER')
        for entry in packet.get('history', []):
            call = entry.get('call', {})
            previous = call.get('arguments', {})
            if call.get('name') != name or previous.get('materialId') != args['materialId']:
                continue
            require(previous.get('operationId')==args['operationId'], 'UPLOAD_RETRY_BLOCKED')
            try:
                status = result(name, previous, payload(entry.get('response')))
            except (Invalid, KeyError, TypeError, ValueError):
                raise Invalid('UPLOAD_RETRY_BLOCKED') from None
            require(status in ('waiting','upload_failed','needs_authorization'), 'UPLOAD_RETRY_BLOCKED')
    if name == 'prepare_deal_review_writeback':
        if 'managerNote' in args:
            require(confirmations.get('managerNote') == args['managerNote'], 'MANAGER_NOTE_NOT_PROVIDED')
        mode = args['mode']
        if mode == 'new':
            require(set(args) <= {'mode','reviewId','changes','noteClaims','managerNote'}, 'UNEXPECTED_PREVIEW_INPUT')
            require(bool(recorded), 'REVIEW_NOT_FROM_HISTORY')
            changed_fields = {change['field'] for change in args.get('changes', [])}
            require(changed_fields <= WRITEBACK_FIELDS, 'FIELD_NOT_SUPPORTED_FOR_WRITEBACK')
            if changed_fields:
                visible = recorded[-1]['deal'].get('visibleFields')
                require(isinstance(visible, list) and changed_fields.issubset(visible), 'FIELD_NOT_VISIBLE_IN_DEAL')
        else:
            require(mode == 'retry_note' and set(args) <= {'mode','operationId','noteClaims','managerNote'}, 'UNEXPECTED_PREVIEW_INPUT')
            receipt = confirmations.get('writebackReceipt', {})
            require(receipt.get('id') == args['operationId'] and receipt.get('noteState') == 'failed' and
                    receipt.get('fieldState') in ('succeeded','not_needed') and
                    receipt.get('errorCode') != 'REVIEW_WRITEBACK_SUPERSEDED', 'OPERATION_NOT_FROM_BROWSER')
            recorded = [data for data in contexts if data['reviewId'] == receipt.get('reviewId')]
            retry_pages = recorded + [data for kind, previous, data in past
                                      if kind == 'get_deal_review_evidence' and
                                      previous.get('reviewId') == receipt.get('reviewId')]
            known_ids = {item['id'] for page in retry_pages for item in page['evidence']}
        claims = args.get('noteClaims', []) + [change['reason'] for change in args.get('changes', [])]
        require(all(set(claim.get('evidenceIds', [])) <= known_ids for claim in claims), 'EVIDENCE_NOT_FROM_HISTORY')
    return tool


def validate(mode, packet):
    try:
        require(shared is not None, 'INSTALL_SIBLING_SKILL')
        if mode=='handoff':
            preview_id = packet['handoff']['previewId']
            require(any(name=='prepare_deal_review_writeback' and data['preview']['id']==preview_id
                        for name,_,data in history(packet)), 'PREVIEW_NOT_FROM_HISTORY')
            decision = 'needs_confirmation'
        elif mode in ('request','result'):
            tool = request(packet)
            decision = 'dispatch_allowed'
            if mode=='result':
                response = packet['response']
                items = response.get('content')
                if response.get('isError') is True and isinstance(items, list) and len(items) == 1:
                    item = items[0]
                    code = item.get('text') if item.get('type') == 'text' else None
                    if code in AUTH_ERROR_DECISIONS:
                        return {'ok':True,'decision':AUTH_ERROR_DECISIONS[code],'errors':[{'code':code,'path':'$/response'}]}
                data = payload(response)
                if 'outputSchema' in tool:
                    shared.schema_check(data,tool['outputSchema'],'$/response')
                call = packet['call']
                decision = result(call['name'],call['arguments'],data)
        else:
            raise Invalid('UNKNOWN_MODE')
        return {'ok':True,'decision':decision,'errors':[]}
    except Invalid as error:
        code = error.code
    except ImportError:
        code = 'INSTALL_JSONSCHEMA'
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError):
        code = 'INVALID_ENVELOPE'
    except shared.Invalid as error:
        return {'ok':False,'decision':'blocked','errors':[{'code':error.code,'path':error.path}]}
    return {'ok':False,'decision':'blocked','errors':[{'code':code,'path':'$'}]}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['request','result','handoff'])
    parser.add_argument('--file',type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.file.read_text(encoding='utf-8') if args.file else sys.stdin.read())
        verdict = validate(args.mode,packet)
    except (OSError, ValueError, RecursionError):
        verdict = {'ok':False,'decision':'blocked','errors':[{'code':'INPUT_UNREADABLE','path':'$'}]}
    print(json.dumps(verdict,ensure_ascii=False))
    sys.exit(0 if verdict['ok'] else 1)
