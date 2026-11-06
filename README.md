# cortex9-lodash-defaultsdeep-prototype-pollution-model

[Español](README.es.md) · [Practice guide](PRACTICE.md)

A Python model of lodash's `_.defaultsDeep` merge path in 4.17.11 and
4.17.12, used to study CVE-2019-10744 (GHSA-jf85-cpcp-j695, CWE-1321).

**This is a model, not lodash and not a reproduction.** No JavaScript engine
runs. Objects, prototypes and functions are Python objects inside a `Realm`
that is created fresh for every run; "pollution" means a property added to
that realm's `Object.prototype`, `Object` or a modelled function's
`prototype`, and it disappears with the run. There are no gadgets: nothing
reads the polluted properties. See [LIMITATIONS.md](LIMITATIONS.md).

## What is ported, and from where (lodash.js at 4.17.11)

| lodash function | Model |
|---|---|
| `safeGet` (:6615) — 4.17.11 guards only `__proto__`; **4.17.12 (PR #4336)** also returns `undefined` when `key === 'constructor' && typeof object[key] === 'function'` | `Lodash.safe_get` |
| `defaultsDeep` (:12837) → `mergeWith`/`createAssigner` → `baseMerge` (:3602) → `baseMergeDeep` (:3639) with `customDefaultsMerge` (:5583) | `defaults_deep`, `base_merge`, `base_merge_deep`, `custom_defaults_merge` |
| `assignMergeValue` (:2454), `baseAssignValue` (:2550), `baseKeysIn` (:3508), `initCloneObject` (:6173), `isPrototype` (:6384), `isPlainObject` (:12037), `isObject` (:11744) | same names in `lodash.py` |
| JS semantics needed: prototype chain `[[Get]]`, `in`, `for…in` with enumerability, functions as objects, `Object.prototype.__proto__` accessor, own `"__proto__"` keys from `JSON.parse` | `realm.py` |

The only change between 4.17.11 and 4.17.12 on this path is `safeGet`; a test
disables the new guard and gets 4.17.11's results for every scenario.
4.17.12 also changes `baseClone`, `_.template` option lookups, `round` and
`debounce`; none of those are on the modelled path.

## Run

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m lodash_ddeep_model fixtures/scenarios/01_ghsa_constructor_prototype.json
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Results (from `results/scenarios.csv`)

| Scenario | 4.17.11 | 4.17.12 |
|---|---|---|
| 01 `{constructor: {prototype: {polluted}}}` (GHSA text) | `Object.prototype.polluted` added | none; target gets own `constructor` object |
| 02 `{constructor: {a: 1}}` (PR #4336 test) | `Object.a` added | none |
| 03 own `"__proto__"` key | none (already guarded) | none |
| 04 target's own `constructor` is a plain object | merged into it | merged into it (guard is for functions only) |
| 05 docs example | `{a: {b: 2, c: 3}}` | same |
| 06 target's own `constructor` is a function `F` | `F.prototype.p` added | own `constructor` replaced by a plain object |
| 07 constructor path one level down | `Object.prototype.q` added | none |

All match expectations derived by hand (`fixtures/expected.json`).

Licence: Apache-2.0.
