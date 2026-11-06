import ast
import json
import unittest
from pathlib import Path

from lodash_ddeep_model.lodash import VERSIONS, Lodash
from lodash_ddeep_model.realm import UNDEF, Realm, get, has, to_py
from lodash_ddeep_model.scenario import load, run_all, run_one

ROOT = Path(__file__).resolve().parent.parent
SC = sorted((ROOT / "fixtures/scenarios").glob("*.json"))
EXP = json.loads((ROOT / "fixtures/expected.json").read_text())


class Fixtures(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(SC), 7)

    def test_hand_expectations(self):
        for p in SC:
            sc = load(p)
            r = run_all(sc)
            for v in VERSIONS:
                self.assertEqual([r[v]["pollution"], r[v]["result"]], EXP[sc["name"]][v], f"{sc['name']} {v}")

    def test_fixed_version_never_pollutes(self):
        for p in SC:
            self.assertEqual(run_one(load(p), "4.17.12")["pollution"], [], p.name)

    def test_cli(self):
        import contextlib
        import io
        from lodash_ddeep_model.cli import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main([str(SC[0]), "--version", "4.17.11"]), 0)
        self.assertEqual(json.loads(buf.getvalue())["pollution"], ["Object.prototype.polluted='yes'"])


class SafeGetGuards(unittest.TestCase):
    def setUp(self):
        self.r = Realm()

    def sg(self, version, obj, key):
        return Lodash(self.r, version).safe_get(obj, key)

    def test_inherited_constructor_function(self):
        o = self.r.new_object()
        self.assertIs(self.sg("4.17.11", o, "constructor"), self.r.Object)
        self.assertIs(self.sg("4.17.12", o, "constructor"), UNDEF)

    def test_own_constructor_object_is_not_guarded(self):
        o = self.r.from_json({"constructor": {"x": 1}})
        for v in VERSIONS:
            self.assertEqual(to_py(self.sg(v, o, "constructor")), {"x": 1}, v)

    def test_own_constructor_function_is_guarded(self):
        o = self.r.new_object()
        o.define("constructor", self.r.new_function("F"))
        self.assertIs(self.sg("4.17.12", o, "constructor"), UNDEF)
        self.assertEqual(self.sg("4.17.11", o, "constructor").label, "F")

    def test_proto_key_guarded_in_both(self):
        o = self.r.from_json({"__proto__": {"x": 1}})
        for v in VERSIONS:
            self.assertIs(self.sg(v, o, "__proto__"), UNDEF)
        self.assertTrue(o.has_own("__proto__"), "own data property, prototype unchanged")
        self.assertIs(o.proto, self.r.ObjectPrototype)

    def test_proto_accessor_semantics(self):
        o = self.r.new_object()
        self.assertTrue(has(o, "__proto__"))
        self.assertIs(get(o, "__proto__"), self.r.ObjectPrototype)


class OnlySafeGetDiffers(unittest.TestCase):
    def test_disabling_the_guard_gives_4_17_11(self):
        class NoGuard(Lodash):
            def safe_get(self, obj, key):
                if key == "__proto__":
                    return UNDEF
                return get(obj, key)
        import lodash_ddeep_model.scenario as scn
        for p in SC:
            sc = load(p)
            real = scn.Lodash
            scn.Lodash = lambda r, v: NoGuard(r, v)
            try:
                patched = run_one(sc, "4.17.12")
            finally:
                scn.Lodash = real
            old = run_one(sc, "4.17.11")
            self.assertEqual((patched["pollution"], patched["result"]), (old["pollution"], old["result"]), p.name)


class Isolation(unittest.TestCase):
    def test_each_run_has_a_fresh_realm(self):
        run_one(load(SC[0]), "4.17.11")
        r = Realm()
        self.assertEqual(r.pollution(), [])
        self.assertFalse(has(r.new_object(), "polluted"))

    def test_no_process_or_js_engine(self):
        for f in (ROOT / "src/lodash_ddeep_model").glob("*.py"):
            for n in ast.walk(ast.parse(f.read_text())):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""]
                    for m in mods:
                        self.assertNotIn(m.split(".")[0], {"os", "subprocess", "ctypes", "js2py", "execjs"}, f.name)


if __name__ == "__main__":
    unittest.main()
