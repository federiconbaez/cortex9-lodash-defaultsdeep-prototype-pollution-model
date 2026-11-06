"""A minimal JavaScript object model, enough for lodash's merge path.

- `JSObj`: own properties (insertion ordered, with an enumerable bit), a
  [[Prototype]] link and a `callable` flag (functions are objects).
- `Realm`: a fresh `Object.prototype`, `Function.prototype` and the `Object`
  constructor for every run, so a "polluted" prototype exists only inside
  that run. Baselines let the run report exactly what was added.
- `UNDEF` is JavaScript `undefined`; `None` is `null`.
Accessors, Symbols, arrays, typed arrays, Buffers and `arguments` are not
modelled; `from_json` rejects arrays.
"""
from __future__ import annotations


class _Undef:
    def __repr__(self) -> str:
        return "undefined"


UNDEF = _Undef()


class JSObj:
    __slots__ = ("label", "props", "proto", "callable")

    def __init__(self, label: str, proto: "JSObj | None", callable_: bool = False):
        self.label = label
        self.props: dict[str, tuple[object, bool]] = {}
        self.proto = proto
        self.callable = callable_

    def __repr__(self) -> str:
        return f"<{self.label}>"

    # [[DefineOwnProperty]] (data property)
    def define(self, key: str, value, enumerable: bool = True) -> None:
        self.props[key] = (value, enumerable)

    def has_own(self, key: str) -> bool:
        return key in self.props

    def own(self, key: str):
        return self.props[key][0]


class ProtoAccessor:
    """Object.prototype.__proto__ (an accessor in JS): `'__proto__' in o` is
    true for ordinary objects and [[Get]] returns the prototype."""

    def __repr__(self) -> str:
        return "[accessor __proto__]"


PROTO_ACCESSOR = ProtoAccessor()


class Realm:
    def __init__(self):
        self.ObjectPrototype = JSObj("Object.prototype", None)
        self.FunctionPrototype = JSObj("Function.prototype", self.ObjectPrototype, True)
        self.Object = JSObj("Object", self.FunctionPrototype, True)
        self.Object.define("prototype", self.ObjectPrototype, enumerable=False)
        self.ObjectPrototype.define("constructor", self.Object, enumerable=False)
        self.ObjectPrototype.define("__proto__", PROTO_ACCESSOR, enumerable=False)
        self.FunctionPrototype.define("constructor", JSObj("Function", self.FunctionPrototype, True), False)
        self._n = 0
        self.watched: list[JSObj] = [self.ObjectPrototype, self.Object, self.FunctionPrototype]
        self.baseline = {id(o): set(o.props) for o in self.watched}

    def new_object(self, label: str | None = None, proto: JSObj | None | str = "default") -> JSObj:
        self._n += 1
        p = self.ObjectPrototype if proto == "default" else proto
        return JSObj(label or f"obj#{self._n}", p)

    def new_function(self, label: str) -> JSObj:
        """A function with its own `prototype` object, like `function F(){}`."""
        f = JSObj(label, self.FunctionPrototype, True)
        fp = JSObj(f"{label}.prototype", self.ObjectPrototype)
        fp.define("constructor", f, enumerable=False)
        f.define("prototype", fp, enumerable=False)
        self.watch(f)
        self.watch(fp)
        return f

    def watch(self, o: JSObj) -> None:
        self.watched.append(o)
        self.baseline[id(o)] = set(o.props)

    def pollution(self) -> list[str]:
        """Properties added to shared objects (prototypes, constructors)."""
        out = []
        for o in self.watched:
            for k in o.props:
                if k not in self.baseline[id(o)]:
                    out.append(f"{o.label}.{k}={to_py(o.props[k][0])!r}")
        return out

    # -- JSON-like conversion ---------------------------------------------
    def from_json(self, v, label: str = "src"):
        if isinstance(v, dict):
            o = self.new_object(label)
            for k, x in v.items():
                # JSON.parse creates an own data property even for "__proto__".
                o.define(k, self.from_json(x, f"{label}.{k}"))
            return o
        if isinstance(v, list):
            raise ValueError("arrays are not modelled")
        return v


def get(o, key: str):
    """[[Get]] through the prototype chain (data properties only)."""
    if not isinstance(o, JSObj):
        return UNDEF
    cur = o
    while cur is not None:
        if key in cur.props:
            v = cur.props[key][0]
            if v is PROTO_ACCESSOR:
                return o.proto
            return v
        cur = cur.proto
    return UNDEF


def has(o: JSObj, key: str) -> bool:
    """`key in o`."""
    cur = o
    while cur is not None:
        if key in cur.props:
            return True
        cur = cur.proto
    return False


def for_in(o: JSObj) -> list[str]:
    """for (key in o): enumerable keys along the chain, own first, no repeats."""
    seen, out = set(), []
    cur = o
    while cur is not None:
        for k, (_, en) in cur.props.items():
            if k in seen:
                continue
            seen.add(k)
            if en:
                out.append(k)
        cur = cur.proto
    return out


def to_py(v, depth: int = 0):
    """Snapshot own enumerable data (for reports); functions by label."""
    if isinstance(v, JSObj):
        if v.callable:
            return f"[Function {v.label}]"
        if depth > 8:
            return "..."
        return {k: to_py(x, depth + 1) for k, (x, en) in v.props.items() if en}
    if v is UNDEF:
        return "undefined"
    return v
