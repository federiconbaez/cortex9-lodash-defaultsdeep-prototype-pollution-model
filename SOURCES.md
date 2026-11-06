# Sources

Local copies under `security-research-45/sources/next/` (not in this repo), read with `gh api` (read-only):

| Source | Used for | SHA-256 of copy |
|---|---|---|
| lodash/lodash PR #4336 diff ("fix: prototype pollution in _.defaultsDeep", merged 2019-06-24, merge commit 1f8ea0774696) | the `safeGet` change and its test (scenario 02) | 50cefc1190120e8052588b0ebf35984682ec348634cee0737a79ad2a99d52a9d |
| lodash.js at tag 4.17.11 | every ported function and line reference | bd2f49d95621bf001f876ce79cb76485e9853c4a71e98a19121131a813d3e72b |
| lodash.js at tag 4.17.12 | confirms the `safeGet` change and lists other changes (none on this path) | b67661fd19ae0bd4dcf3e3c84dc10ccd6927f7729d57fde1aa90169ccd7fcd3c |
| GHSA-jf85-cpcp-j695 (CVE-2019-10744) | description (scenario 01), affected packages and ranges | ebd209670ff95b5ab2c2514a79190a71a79897ca0ada03767f959262f2fa3ba9 |

Affected ranges per the GHSA record: lodash < 4.17.12, lodash-es < 4.17.14,
lodash-amd < 4.17.13, lodash.defaultsdeep < 4.6.1, lodash-rails < 4.17.12.
Only lodash.js 4.17.11/4.17.12 was read; the other packages were not.
