# How many F-Droid apps are registered with Google?

<!-- RESULTS: filled in when the scan of all 4,901 packages is complete -->

## Background

From 2027 (no exact date yet) Android will refuse to install apps whose developer has not
registered with Google's Android developer verification programme and declared the app's
package name and signing certificate. F-Droid hosts thousands of apps, most of them built
and signed by F-Droid's own build server with F-Droid's keys, by volunteers who may never
register. Nobody had measured how many of them are already registered. This repository does.

## Method (reproducible with one API key)

Google exposes a public, server-to-server
[Android Developer ID Status API](https://developer.android.com/developer-verification/guides/check-registration-status).
For a package name and a SHA-256 certificate fingerprint it answers one of:

| State | Meaning |
|---|---|
| `REGISTERED` | this package name **and** this signing certificate are registered |
| `NOT_REGISTERED` | the pair is not registered (and the package name is not registered with any certificate) |
| `REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT` | the package name is registered, but with a different certificate than the one F-Droid ships |

1. `data/index-v2.json` is F-Droid's own index (`https://f-droid.org/repo/index-v2.json`, downloaded 2026-10-30).
2. `data/packages.json` is extracted from it: every package name with the SHA-256 fingerprint of the
   certificate F-Droid uses to sign it (the index's `preferredSigner`; 18 packages list more than one signer).
3. `census.py` asks the API once per package, sending both the package name and the fingerprint, and
   appends the answer to `data/results.csv`. It stops at the daily quota (HTTP 429) and continues where it left
   off on the next run.
4. `summary.py` prints the counts, the percentages and the list of packages in the third state.

To reproduce: create a Google Cloud project, enable "Android Developer ID Status API", create an API key, then

```bash
export ANDROID_STATUS_API_KEY=...
python3 census.py          # ~1,000 packages per day per project
python3 summary.py --md
```

The quota is 1,000 requests per project per day, so the full index takes five days with one project.
Google's API terms forbid circumventing documented quotas, so this census used a single project.

## Caveats

- **What the API measures.** "Registered" means the developer completed Google's verification and declared
  this package name. It says nothing about whether an app will keep working: Google has announced that
  installs from unregistered developers will be blocked on certified Android devices from 2027, but the
  enforcement date, the exemptions (there is a separate "hobbyist" track and an "advanced flow" for power
  users) and the exact behaviour are still changing.
- **F-Droid signs most apps itself.** F-Droid's build server compiles apps from source and signs them with
  F-Droid's keys. The developer may have registered the package name with the certificate they use on Google
  Play or GitHub. That shows up here as `REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT`: the developer is
  registered, the F-Droid build is not. Only apps with
  [reproducible builds](https://f-droid.org/docs/Reproducible_Builds/), which F-Droid publishes with the
  developer's own signature, can be `REGISTERED` without the developer registering an F-Droid-specific key.
- **One fingerprint per package.** For the 18 packages signed by more than one key, only F-Droid's
  preferred signer was checked.
- **Point in time.** Results are from the dates in the `checked_at` column; developers register every day.
- **The API answers for the whole world, not for F-Droid.** A package name registered by somebody else
  (for example a fork that kept the original package name) also reads as "registered with another
  certificate". The list below should be read as "someone registered this package name", not as
  "this developer registered".

## Files

- `census.py`, `summary.py`: the scanner and the report.
- `data/packages.json`: 4,901 package names and fingerprints from F-Droid's index.
- `data/results.csv`: one row per package: package, fingerprint, state, HTTP status, timestamp.
