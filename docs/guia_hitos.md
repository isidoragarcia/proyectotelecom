# Guía por hito — qué parte del código cubre cada requisito

## Hito 1 (02 de octubre) — POO, UML y repositorio

| Requisito de la pauta | Dónde está |
|---|---|
| Clases Transmisor, CanalFisico, Receptor, Enrutador | `telecom/*.py` |
| Herencia justificada | Las 4 heredan de `ComponenteEnlace` (id, estado de servicio y el método polimórfico `procesar`) |
| Polimorfismo | `procesar()`: Paquete→Senal (Tx), Senal→Senal (canal), Senal→Resultado (Rx), Paquete→siguiente salto (enrutador) |
| Encapsulamiento de ancho de banda, fs y potencia | Atributos `__privados` + `obtener_*` / `ajustar_*` con validación (Nyquist, rangos físicos) |
| La señal no salta al receptor | `EnlaceTelecom.__transmitir_capa_fisica` siempre pasa por `CanalFisico.procesar`, que usa los métodos privados `__aplicar_atenuacion` y `__aplicar_ruido_termico` |
| Composición | `EnlaceTelecom` *tiene* Tx, canal, Rx, enrutadores y registro (no hereda de ellos) |
| UML | `docs/uml_clases.png` (fuente editable: `docs/uml_clases.mmd`, se abre en https://mermaid.live) |

Subir el repositorio:

```bash
git init
git add .
git commit -m "Hito 1: arquitectura POO del enlace y diagrama UML"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

## Hito 2 (13 de noviembre) — Hash, búsqueda binaria, Big-O y ramas

| Requisito | Dónde está |
|---|---|
| Tabla MAC/IP con diccionarios | `Enrutador.__tabla_ip`, `Enrutador.__tabla_mac` |
| Búsqueda binaria recursiva/iterativa | `RegistroPaquetes.buscar_binaria_recursiva` / `buscar_binaria_iterativa` |
| Evidencia empírica | `python -m benchmarks.complejidad` → `resultados/complejidad_*.pdf` |

**Ramas:** la pauta evalúa un flujo real con branch + merge. El trabajo del
Hito 2 (informe Big-O, ajustes al ruteo, más escenarios) háganlo en una rama:

```bash
git checkout -b feature/enrutamiento
# ... cambios ...
git commit -am "Enrutamiento: análisis Big-O y escenarios de prueba"
git push -u origin feature/enrutamiento
# En GitHub: abrir Pull Request -> Merge a main
```

### Borrador del análisis Big-O (para el informe)

**Ruteo con Hash, O(1) vs O(n).** El `dict` calcula `h = hash(red)` y va
directo a la casilla `h mod m` de un arreglo. Con factor de carga α = n/m
acotado (Python redimensiona la tabla al superar 2/3), el número esperado de
sondeos es constante: T(n) = O(1) promedio. Una lista de rutas exige comparar
la clave con cada elemento hasta encontrarla; en el peor caso (ruta al final
o inexistente) hace n comparaciones: T(n) = O(n). Medición: con 10⁶ redes,
el dict tarda ~1 µs y la lista ~26 ms (≈ 26 000 veces más).

**Búsqueda binaria, O(log n).** Cada llamada descarta la mitad del intervalo:
T(n) = T(n/2) + c. Desarrollando, T(n) = T(n/2^k) + k·c; el caso base se
alcanza cuando n/2^k = 1, es decir k = log₂ n, entonces T(n) = c·log₂ n + T(1)
= O(log n). Para 10⁶ paquetes son ≤ 20 comparaciones; para 10⁹ serían ≤ 30.
La secuencial necesita hasta n comparaciones (10⁶ o 10⁹). La versión
recursiva además usa O(log n) de memoria en la pila; la iterativa, O(1).

**Por qué no hay que ordenar:** los ids se registran en orden creciente y
`registrar` rechaza ids menores, así que la lista está ordenada por
construcción: insertar cuesta O(1) amortizado y nunca se paga el
O(n log n) de ordenar.

## Hito 3 (26–27 de noviembre) — NumPy, FFT, IEEE, PEP8

| Requisito | Dónde está |
|---|---|
| Señal como arreglo 1D de NumPy | `Transmisor.generar_senal` (broadcasting tonos × tiempo, sin for) |
| Ruido y atenuación sin for | `CanalFisico.__aplicar_atenuacion` / `__aplicar_ruido_termico` |
| Vectorización extra | `CanalFisico.procesar_barrido`: D distancias a la vez en una matriz (D × N) |
| FFT con `numpy.fft` | `Receptor.calcular_espectro` (`rfft` + `rfftfreq`) |
| Gráfico IEEE del espectro | `resultados/espectro_recibido.pdf` |
| PEP8 | `flake8 .` sin errores |
| Ejecución en vivo | `python main.py` (≈ 3 s) |

## Defensa oral (recordatorio de la pauta)

Prohibido mostrar código. Para explicar la lógica usen:

- el UML de `docs/`,
- un diagrama de flujo de `EnlaceTelecom.enviar_paquete`
  (entrar a R1 → consultar tabla → ¿TTL 0? → ¿LOCAL? → Tx → Canal → Rx → registrar),
- los gráficos de `resultados/`.
