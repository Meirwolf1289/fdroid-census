# Publish drafts

> **PROVISIONAL.** Numbers below are from day 1 (1,005 of 4,901 packages, alphabetical a..com.c, not a
> random sample). Every number is replaced when the full scan finishes. Do not post before that.

Day-1 numbers: 57% NOT_REGISTERED, 31% REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT, 11% REGISTERED.

## Show HN title (<= 80 chars; pick one after the final numbers)

1. `Show HN: I asked Google's API about every F-Droid app. XX% aren't registered`  (76)
2. `Show HN: A census of F-Droid apps against Google's developer verification`  (73)
3. `Show HN: Only XX% of F-Droid apps will install under Google's 2027 rules`  (72)

If "Show HN" is rejected for a new account, drop the prefix and submit the GitHub README as a plain link
with title 2 minus "Show HN: ". Email hn@ycombinator.com first with the link and one sentence: "new
account, this is original data, not promotion".

## First comment (post immediately under the submission)

Hi HN. From 2027 Android will refuse to install apps whose developer hasn't registered with Google
(package name + signing certificate). F-Droid builds and signs most of its apps itself, so I wondered how
many of its 4,901 apps are actually covered. Google has a public API that answers exactly that question,
one package at a time, 1,000 a day. I ran it over the whole F-Droid index.

Results (all 4,901 packages, checked DATE..DATE):

- XX% NOT_REGISTERED: nobody has registered this package name.
- XX% REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT: the developer (or someone) registered the package
  name, but with a different certificate than the one F-Droid signs with. Under the rules as published,
  the F-Droid build of these apps is not covered either.
- XX% REGISTERED: package name and F-Droid's certificate both registered. Mostly reproducible builds, which
  F-Droid ships with the developer's own signature.

The middle group is the interesting one: it includes PROVISIONAL-EXAMPLES (Immich, FluffyChat, SimpleX,
Amaze, DAVx5, Aegis, Proton VPN, Organic Maps). Those developers did register, for Play. Their F-Droid
builds still fail the check, because F-Droid re-signs.

Method, code, raw CSV and caveats are in the repo. The biggest caveat: the API tells you about
registration today, not about what Google will enforce in 2027, and the rules (hobbyist track, "advanced
flow" for power users) are still moving. I'd love corrections from anyone at F-Droid or Google.

## X thread

1/ I asked Google's own API about every one of F-Droid's 4,901 apps: is this developer registered for
Android's 2027 developer-verification rule? Thread.

2/ Background: from 2027, certified Android devices will refuse to install apps whose developer hasn't
registered with Google and declared the app's package name + signing key. F-Droid signs most apps with its
own keys. Nobody had counted what that means.

3/ Google exposes a status API (1,000 queries/day). One call per package, with the certificate F-Droid
actually ships. Five days, one API key, 100 lines of Python. Repo: LINK

4/ XX% NOT_REGISTERED. Nobody has registered the package name. For these apps nothing changes until the
developer acts.

5/ XX% REGISTERED_WITH_ANOTHER_CERTIFICATE_FINGERPRINT. The developer registered, but with their Play
key. The F-Droid build, signed by F-Droid, is a different app as far as the check is concerned. Includes
EXAMPLES.

6/ XX% REGISTERED. Package name and F-Droid's certificate match a registered developer. Mostly
reproducible builds, where F-Droid ships the developer's own signature.

7/ Caveats: registration today != enforcement in 2027; rules still changing (hobbyist track, advanced
flow); a package name registered by a fork counts as "registered with another certificate". Full list of
caveats and the raw CSV in the repo.

8/ If you maintain an F-Droid app and you're in the middle group: reproducible builds move you to the top
group without touching Google. F-Droid's docs: https://f-droid.org/docs/Reproducible_Builds/
