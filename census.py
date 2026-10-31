#!/usr/bin/env python3
"""Asks Google's Android Developer ID Status API about every F-Droid package, one call per package.

    ANDROID_STATUS_API_KEY=... python3 census.py [--limit N]

Reads data/packages.json (from index-v2.json), writes/extends data/results.csv and stops cleanly at the
1,000-requests-per-day quota (HTTP 429). Re-run tomorrow: packages already in results.csv are skipped.
Each call sends the package name AND F-Droid's preferred signing fingerprint, so one call yields all
three states: REGISTERED, NOT_REGISTERED, REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT.
Docs: https://developer.android.com/developer-verification/guides/check-registration-status
"""
import csv
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGES = os.path.join(HERE, 'data', 'packages.json')
RESULTS = os.path.join(HERE, 'data', 'results.csv')
ENDPOINT = 'https://androiddeveloperidstatus.googleapis.com/v1/packages/%s/packageRegistrationStatus:check'
FIELDS = ['package', 'fingerprint', 'state', 'http', 'checked_at']


def check(key, package, fingerprint):
    url = ENDPOINT % urllib.parse.quote(package, safe='')
    if fingerprint:
        url += '?certificateFingerprint=' + urllib.parse.quote(fingerprint, safe='')
    req = urllib.request.Request(url, headers={'X-Goog-Api-Key': key, 'Accept': 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, json.load(r).get('state', '')
        except urllib.error.HTTPError as e:
            if e.code in (500, 503) and attempt < 3:      # docs: retryable with exponential backoff
                time.sleep(2 ** attempt)
                continue
            return e.code, e.read().decode('utf-8', 'replace')[:200]
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return 0, 'network: %s' % e


def main():
    key = os.environ.get('ANDROID_STATUS_API_KEY')
    if not key:
        sys.exit('Set ANDROID_STATUS_API_KEY (Google Cloud > APIs & Services > Credentials).')
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None

    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS, newline='') as f:
            done = {row['package'] for row in csv.DictReader(f) if row['http'] == '200'}
    todo = [p for p in json.load(open(PACKAGES)) if p['package'] not in done]
    print('%d done, %d to go' % (len(done), len(todo)))

    new = os.path.getsize(RESULTS) == 0 if os.path.exists(RESULTS) else True
    with open(RESULTS, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for i, p in enumerate(todo[:limit]):
            fp = p['preferredSigner'] or (p['signers'][0] if p['signers'] else '')
            http, state = check(key, p['package'], fp)
            w.writerow({'package': p['package'], 'fingerprint': fp, 'state': state, 'http': http,
                        'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')})
            f.flush()
            print('%4d %-50s %s' % (i + 1, p['package'][:50], state if http == 200 else 'HTTP %s %s' % (http, state)))
            if http == 429:
                print('Quota reached. Run again tomorrow; progress is saved.')
                break
            if http in (400, 401, 403):
                print('The key was refused. Check the API is enabled on the project.')
                break
            time.sleep(0.3)   # polite; the quota is daily, not per second


if __name__ == '__main__':
    main()
