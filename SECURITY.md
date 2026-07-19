# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅ Yes    |
| 0.1.x   | ❌ No — please upgrade |

Fixes are released on the latest version. If you're on `0.1.x`, upgrade with `pip install --upgrade superinvestor` before reporting.

## Reporting a vulnerability

**Please do not open a public GitHub issue for a security problem.**

Email **chunghun1@naver.com** with the details. Use a subject line starting with `[superinvestor security]` so it doesn't get lost.

## What to include

- A description of the issue and why you believe it's a security problem.
- Steps to reproduce it — ideally a minimal script or command.
- The affected version (`pip show superinvestor`) and your Python version.
- The impact as you see it: what an attacker could achieve.

## Scope

This is a client library that makes outbound HTTP requests to `dataroma.com` and parses the HTML it gets back. The things most likely to matter:

- **Parsing untrusted input.** `superinvestor` feeds remote HTML into BeautifulSoup/lxml. A crash, hang, or resource exhaustion triggered by hostile or malformed markup is in scope.
- **Vulnerable dependencies.** Issues in `requests`, `beautifulsoup4`, or `lxml` that this project's usage exposes are in scope — report them here and upstream.
- **Unsafe handling of returned data.** Anything that could lead to code execution or unintended file/network access on a user's machine.

Out of scope:

- Vulnerabilities in **dataroma.com** itself. This project is not affiliated with DataRoma; report those to DataRoma directly.
- The **accuracy of the data**. Wrong or stale numbers are a data or parsing bug — please open a normal issue for those.
- The absence of TLS certificate pinning, rate-limit tuning, or similar hardening choices that are deliberate design decisions.

## Response expectations

This is a solo-maintained project, so please calibrate accordingly:

- **Acknowledgement:** within about one week.
- **Assessment and fix:** timing depends on severity and complexity; you'll get an honest estimate once the issue is confirmed.
- **Disclosure:** coordinated. Please give the fix a chance to ship before publishing details. Credit will be given in the release notes unless you'd rather stay anonymous.
