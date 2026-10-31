#!/usr/bin/env python3
"""Prints the census results: counts and percentages per state, errors, and the packages whose
F-Droid signing key differs from the key their developer registered with Google.

    python3 summary.py [--md]      (--md: GitHub-flavoured Markdown tables for the README)
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, 'data', 'results.csv')
PACKAGES = os.path.join(HERE, 'data', 'packages.json')
OTHER = 'REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT'
ORDER = ['NOT_REGISTERED', OTHER, 'REGISTERED']


def load():
    rows = {}
    with open(RESULTS, newline='') as f:
        for r in csv.DictReader(f):
            if r['http'] == '200' or r['package'] not in rows:   # keep the successful answer per package
                rows[r['package']] = r
    return rows


def main():
    md = '--md' in sys.argv
    names = {p['package']: p['name'] for p in json.load(open(PACKAGES))}
    rows = load()
    ok = [r for r in rows.values() if r['http'] == '200']
    errors = collections.Counter(r['http'] for r in rows.values() if r['http'] != '200')
    counts = collections.Counter(r['state'] for r in ok)
    total = len(ok)

    print('%d packages in F-Droid, %d answered by Google, %d errors' % (len(names), total, sum(errors.values())))
    if errors:
        print('errors by HTTP status: ' + ', '.join('%s=%d' % kv for kv in sorted(errors.items())))
    print()
    if md:
        print('| State | Packages | Share |')
        print('|---|---:|---:|')
    for state in ORDER + sorted(set(counts) - set(ORDER)):
        n = counts.get(state, 0)
        pct = 100.0 * n / total if total else 0
        print(('| %s | %d | %.1f%% |' if md else '%-48s %5d  %5.1f%%') % (state, n, pct))
    print()

    other = sorted((r for r in ok if r['state'] == OTHER), key=lambda r: r['package'])
    print('%d packages registered with a different certificate than the one F-Droid ships:' % len(other))
    if md:
        print()
        print('| Package | App name |')
        print('|---|---|')
    for r in other:
        print(('| `%s` | %s |' if md else '  %-50s %s') % (r['package'], names.get(r['package'], '')))


if __name__ == '__main__':
    main()
