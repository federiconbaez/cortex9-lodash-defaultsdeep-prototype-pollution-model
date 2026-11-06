# cortex9-lodash-defaultsdeep-prototype-pollution-model

[English](README.md) · [Guía práctica](PRACTICE.md)

Modelo en Python del camino de mezcla de `_.defaultsDeep` de lodash 4.17.11 y
4.17.12, para estudiar CVE-2019-10744.

**Es un modelo, no lodash ni una reproducción.** No corre ningún motor de
JavaScript. Objetos, prototipos y funciones son objetos Python dentro de un
`Realm` nuevo en cada ejecución; "contaminación" significa una propiedad
añadida al `Object.prototype`, a `Object` o al `prototype` de una función de
ese realm, y desaparece con la ejecución. No hay gadgets: nada lee las
propiedades contaminadas.

- Portado: `safeGet`, `baseMerge`, `baseMergeDeep`, `customDefaultsMerge`,
  `assignMergeValue`, `baseKeysIn`, `initCloneObject`, `isPlainObject`.
- 4.17.12 (PR #4336) solo cambia `safeGet` en este camino: devuelve
  `undefined` para `constructor` **cuando es una función**. Un `constructor`
  propio que es un objeto plano se sigue mezclando (escenario 04).

Resultados: 01, 02, 06 y 07 contaminan en 4.17.11 y no en 4.17.12; 03, 04 y
05 son iguales en ambas versiones.

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

Ver [SOURCES.md](SOURCES.md), [LIMITATIONS.md](LIMITATIONS.md). Licencia Apache-2.0.
