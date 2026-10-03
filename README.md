# Simulador de un Enlace de Telecomunicaciones con Enrutamiento

Proyecto semestral del curso **EL4203 Programación Avanzada**, Departamento de Ingeniería Eléctrica, Universidad de Chile (Primavera 2026).

Simulador en Python, orientado a objetos, que modela el envío de una señal desde un **transmisor** hasta un **receptor**, pasando por **canales** que la atenúan y por **enrutadores** que deciden el siguiente salto a partir de tablas de rutas construidas de forma distribuida.

> **Estado:** Hito 1 (arquitectura). La implementación de los métodos está en desarrollo, así que algunos archivos de la estructura de abajo todavía no existen.

---

## Componentes

| Clase | Rol |
|---|---|
| `ComponenteEnlace` | Clase abstracta base. Guarda el identificador único de cada componente. |
| `Senal` | Lleva los datos y la IP de destino, junto con su potencia y su frecuencia de muestreo. |
| `Transmisor` | Genera la señal y la envía por su canal. |
| `Canal` | Une dos componentes y atenúa la señal según su coeficiente de amortiguación. |
| `Enrutador` | Mantiene una tabla de rutas y reenvía la señal al siguiente salto. |
| `Receptor` | Acepta la señal si supera el umbral de detección y si su frecuencia de muestreo coincide con la propia. |

Las tablas de rutas se construyen con una variante de **Bellman–Ford distribuido** (vector de caminos). La métrica es el número de saltos, y se descartan los caminos que formarían bucles.

## Estructura del repositorio

Estructura objetivo del proyecto:

```
proyectotelecom/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── componente_enlace.py
│   ├── senal.py
│   ├── transmisor.py
│   ├── canal.py
│   ├── enrutador.py
│   ├── receptor.py
│   └── main.py            # escenario de simulación de ejemplo
├── tests/                 # pruebas unitarias (pytest)
└── docs/                  # diagramas UML y de flujo, informes de cada hito
```

## Requisitos

- Python 3.10 o superior
- Conda (recomendado) o `venv`

## Instalación

```bash
git clone https://github.com/isidoragarcia/proyectotelecom.git
cd proyectotelecom

conda create -n progra_avanzada python=3.10 -y
conda activate progra_avanzada
pip install -r requirements.txt
```

## Uso

```bash
python src/main.py     # ejecuta el escenario de simulación
pytest                 # ejecuta las pruebas
```

## Flujo de trabajo con Git

- `main` contiene siempre una versión estable.
- Cada funcionalidad se desarrolla en su propia rama (`feature/enrutador`, `feature/receptor`, …).
- Los cambios entran a `main` mediante *pull requests* revisados por el otro integrante.
- El código sigue PEP8 e incluye *docstrings* y anotaciones de tipo, indicando las unidades físicas.

## Hitos

- [x] **Hito 1 – Arquitectura:** diagrama de clases, diagramas de flujo y repositorio.
- [ ] **Hito 2 – Algoritmia:** implementación, ruido en el canal, buffer FIFO y análisis de complejidad.
- [ ] **Entrega final:** informe y defensa.

## Autores

- Isidora García
- *[Nombre de tu compañero/a]*

Profesor de cátedra: Jonas Peñailillo P. · Profesor auxiliar: Lucas Marshall R.
