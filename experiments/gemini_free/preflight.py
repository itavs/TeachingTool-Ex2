"""Read-only Gemini model inventory. Does not generate content or enable billing.

Model listing alone cannot verify the project's billing tier or free quota.
Secrets are read locally, sent in an HTTPS header, and never logged.
"""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
KEY_FILE = ROOT / '.ai-lab' / 'secrets' / 'gemini-api-key.txt'
REPORT = ROOT / '.ai-lab' / 'gemini' / 'preflight.json'


def read_key():
    value = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not value and KEY_FILE.is_file():
        value = KEY_FILE.read_text(encoding='utf-8-sig').strip()
    return value


def main():
    result = {'utc_checked': dt.datetime.now(dt.timezone.utc).isoformat(),
              'generation_requests_sent': 0, 'account_free_tier_verified': False,
              'account_quotas_verified': False}
    key = read_key()
    if not key:
        result['status'] = 'blocked_missing_local_api_key'
    else:
        models, page = [], None
        try:
            while True:
                query = {'pageSize': 100}
                if page:
                    query['pageToken'] = page
                url = 'https://generativelanguage.googleapis.com/v1beta/models?' + urllib.parse.urlencode(query)
                request = urllib.request.Request(url, headers={'x-goog-api-key': key})
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = json.load(response)
                for model in body.get('models', []):
                    models.append({field: model.get(field) for field in
                        ['name', 'version', 'displayName', 'inputTokenLimit',
                         'outputTokenLimit', 'supportedGenerationMethods']})
                page = body.get('nextPageToken')
                if not page:
                    break
            result.update(status='metadata_listed_not_quota_or_billing_proof', models=models)
        except urllib.error.HTTPError as error:
            # Do not dump server bodies or request headers, which could expose a key.
            result.update(status='http_error', http_status=error.code)
        except Exception:
            result['status'] = 'connection_or_response_error_details_not_logged'
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'generation_requests_sent': 0,
                      'account_free_tier_verified': False,
                      'listed_model_count': len(result.get('models', []))}))


if __name__ == '__main__':
    main()
