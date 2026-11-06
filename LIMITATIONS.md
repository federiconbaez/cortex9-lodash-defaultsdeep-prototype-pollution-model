# Limitations

- **Model, not lodash or JavaScript.** Only the `defaultsDeep` path for plain
  objects and primitives is ported. Arrays, Buffers, typed arrays,
  `arguments`, Maps/Sets, Symbols, getters/setters (other than
  `Object.prototype.__proto__`), frozen objects and `Object.create(null)`
  sources are not modelled; `Realm.from_json` rejects arrays.
- `isPlainObject` is reduced to "prototype is null or its own `constructor`
  is the realm's `Object`"; `funcToString` and `toStringTag` checks are not
  modelled. NaN handling in `eq` is not modelled (JSON inputs).
- **No gadgets, no consumers.** The model reports which shared objects got
  new properties. It does not model any code that reads them, and it makes
  no claim about impact in any application.
- **Isolation.** Every run builds its own `Realm`; nothing is shared between
  runs or touches a real JavaScript environment.
- `_.merge`, `_.mergeWith` with other customizers, `_.set`/`_.zipObjectDeep`
  and the `_.template` change in 4.17.12 are separate code paths and are not
  modelled.
- CI is defined in `.github/workflows/ci.yml` (unit tests on Python 3.10–3.13, results regeneration). Results were also
  reproduced locally on Python 3.13 and 3.10; the status of hosted runs is whatever the
  repository's Actions page shows.
