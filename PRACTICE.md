# Guía práctica / Practice guide

Ejercicios **offline** sobre un modelo de objetos en memoria. No corre
JavaScript ni se contamina nada fuera de cada ejecución. *English summary at
the end.*

## Objetivos

1. Seguir `defaultsDeep` por `baseMerge` / `baseMergeDeep` /
   `customDefaultsMerge` y ver dónde entra `constructor`.
2. Distinguir un `constructor` heredado (función `Object`) de uno propio que
   es objeto o función, y qué hace cada versión de `safeGet`.
3. Entender por qué `__proto__` ya estaba protegido y `constructor` no.
4. Escribir guardas y tests para tus propias funciones de mezcla profunda.

## Prerrequisitos

Python ≥ 3.10. Lectura: diff del PR #4336 y las funciones de lodash.js 4.17.11
citadas en el README (ver [SOURCES.md](SOURCES.md)).

## Comandos locales

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m lodash_ddeep_model fixtures/scenarios/01_ghsa_constructor_prototype.json
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Ejercicios graduados

**Nivel 1 — a mano.** Para 01 en 4.17.11, escribe la pila de llamadas hasta la
asignación en `Object.prototype`. ¿Qué devuelve `customDefaultsMerge` en cada
nivel?

**Nivel 2 — la guarda.** Repite con 4.17.12. ¿Por qué `initCloneObject` crea
un objeto nuevo y dónde termina `constructor`?

**Nivel 3 — `__proto__`.** Explica 03: ¿por qué un `"__proto__"` propio (de
`JSON.parse`) no cambia el prototipo, ni antes ni después del fix?

**Nivel 4 — función vs objeto.** Compara 04 y 06. ¿Por qué la guarda mira
`typeof === 'function'` y no solo el nombre de la clave?

**Nivel 5 — profundidad.** En 07 la clave peligrosa está un nivel abajo.
¿Qué objeto es `object` cuando se consulta `constructor`?

**Nivel 6 — código.** Añade un escenario con dos fuentes donde la primera
crea una propiedad propia y la segunda intenta contaminar la misma clave.
Deriva las expectativas a mano y añádelas a `fixtures/expected.json`.

**Nivel 7 — defensa propia.** Para una función de mezcla propia, escribe
guardas por clave (`__proto__`, `constructor`, `prototype`) y un test que
verifique con un realm nuevo que no se añadió nada a los prototipos.

## Vínculo modelo ↔ CVE

| Caso real | En el código |
|---|---|
| `safeGet` sin guarda de `constructor` | `Lodash.safe_get`, versión 4.17.11 |
| Fix PR #4336 | `Lodash.safe_get`, versión 4.17.12 |
| `Object.prototype` contaminado | `Realm.pollution()` |
| Test upstream `'a' in Object` | escenario 02 |

---

## English summary

Offline exercises on an in-memory object model. Levels: (1) trace 01 under
4.17.11; (2) the 4.17.12 guard and `initCloneObject`; (3) why an own
`"__proto__"` key is harmless here; (4) function vs object `constructor`;
(5) the nested case; (6) add a two-source scenario with hand expectations;
(7) key guards and a fresh-realm test for your own deep-merge code.
