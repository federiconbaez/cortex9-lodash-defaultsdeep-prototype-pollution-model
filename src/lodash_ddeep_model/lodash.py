"""lodash 4.17.11 / 4.17.12 `defaultsDeep` path, ported function by function.

Line references are to lodash.js at tag 4.17.11 (fix: PR #4336, 4.17.12).
Only the branches reachable with plain objects and primitives are ported;
the array / Buffer / typed-array / arguments branches of baseMergeDeep are
not ported (inputs cannot contain arrays).
"""
from __future__ import annotations

from .realm import UNDEF, JSObj, Realm, for_in, get, has

VERSIONS = ("4.17.11", "4.17.12")


class Lodash:
    def __init__(self, realm: Realm, version: str):
        if version not in VERSIONS:
            raise ValueError(version)
        self.r, self.version = realm, version
        self.trace: list[str] = []

    # -- predicates -------------------------------------------------------
    @staticmethod
    def is_object(v) -> bool:           # :11744 (functions are objects)
        return isinstance(v, JSObj)

    @staticmethod
    def is_function(v) -> bool:
        return isinstance(v, JSObj) and v.callable

    def is_plain_object(self, v) -> bool:   # :12037
        if not isinstance(v, JSObj) or v.callable:
            return False
        proto = v.proto
        if proto is None:
            return True
        ctor = proto.own("constructor") if proto.has_own("constructor") else False
        return ctor is self.r.Object

    def is_prototype(self, v) -> bool:       # :6384
        ctor = get(v, "constructor")
        proto = get(ctor, "prototype") if self.is_function(ctor) else UNDEF
        if not isinstance(proto, JSObj):
            proto = self.r.ObjectPrototype
        return v is proto

    @staticmethod
    def eq(a, b) -> bool:                    # SameValueZero (no NaN here)
        if isinstance(a, JSObj) or isinstance(b, JSObj):
            return a is b
        return type(a) is type(b) and a == b

    # -- the guard that changed -------------------------------------------
    def safe_get(self, obj, key: str):       # 4.17.11 :6615 / 4.17.12 :6609
        if self.version == "4.17.12" and key == "constructor" and self.is_function(get(obj, key)):
            self.trace.append(f"safeGet({obj!r}, 'constructor') -> undefined (function guard)")
            return UNDEF
        if key == "__proto__":
            return UNDEF
        return get(obj, key)

    # -- helpers ----------------------------------------------------------
    def base_assign_value(self, obj: JSObj, key: str, value) -> None:   # :2550
        # key == '__proto__' uses defineProperty: an own property either way
        obj.define(key, value)
        self.trace.append(f"assign {obj!r}.{key}")

    def assign_merge_value(self, obj: JSObj, key: str, value) -> None:  # :2454
        if (value is not UNDEF and not self.eq(get(obj, key), value)) or \
                (value is UNDEF and not has(obj, key)):
            self.base_assign_value(obj, key, value)

    def keys_in(self, obj: JSObj) -> list[str]:                         # :3508
        is_proto = self.is_prototype(obj)
        return [k for k in for_in(obj)
                if not (k == "constructor" and (is_proto or not obj.has_own(k)))]

    def init_clone_object(self, obj: JSObj) -> JSObj:                    # :6173
        if self.is_function(get(obj, "constructor")) and not self.is_prototype(obj):
            return self.r.new_object(proto=obj.proto)
        return self.r.new_object()

    # -- merge ------------------------------------------------------------
    def custom_defaults_merge(self, obj_value, src_value, key, obj, source, stack):  # :5583
        if self.is_object(obj_value) and self.is_object(src_value):
            stack[id(src_value)] = obj_value
            self.base_merge(obj_value, src_value, UNDEF, self.custom_defaults_merge, stack)
            del stack[id(src_value)]
        return obj_value

    def base_merge(self, obj: JSObj, source: JSObj, src_index, customizer, stack) -> None:  # :3602
        if obj is source:
            return
        for key in self.keys_in(source):
            src_value = get(source, key)
            if self.is_object(src_value):
                self.base_merge_deep(obj, source, key, src_index, self.base_merge, customizer, stack)
            else:
                new_value = customizer(self.safe_get(obj, key), src_value, key, obj, source, stack) \
                    if customizer else UNDEF
                if new_value is UNDEF:
                    new_value = src_value
                self.assign_merge_value(obj, key, new_value)

    def base_merge_deep(self, obj, source, key, src_index, merge_func, customizer, stack):  # :3639
        obj_value = self.safe_get(obj, key)
        src_value = self.safe_get(source, key)
        stacked = stack.get(id(src_value))
        if stacked is not None:
            self.assign_merge_value(obj, key, stacked)
            return
        new_value = customizer(obj_value, src_value, key, obj, source, stack) if customizer else UNDEF
        is_common = new_value is UNDEF
        if is_common:
            new_value = src_value
            if self.is_plain_object(src_value):
                new_value = obj_value
                if not self.is_object(obj_value) or self.is_function(obj_value):
                    new_value = self.init_clone_object(src_value)
            else:
                # functions, `undefined` (e.g. safeGet(source, '__proto__')),
                # other non-plain values. Arrays/Buffers/typed arrays/arguments
                # cannot occur: Realm.from_json rejects arrays.
                is_common = False
        if is_common:
            stack[id(src_value)] = new_value
            merge_func(new_value, src_value, src_index, customizer, stack)
            del stack[id(src_value)]
        self.assign_merge_value(obj, key, new_value)

    def defaults_deep(self, obj: JSObj, *sources: JSObj) -> JSObj:  # :12837 via mergeWith/createAssigner
        stack: dict[int, object] = {}
        for i, s in enumerate(sources):
            if s:
                self.base_merge(obj, s, i, self.custom_defaults_merge, stack)
        return obj
