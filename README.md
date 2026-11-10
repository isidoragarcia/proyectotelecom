# Simulador de Enlace de Telecomunicaciones — EL4203 (Opción C)

Simulación de un enlace de extremo a extremo con dos capas:

- **Capa lógica:** los paquetes se rutean salto a salto por una red de
  enrutadores con tablas IP/MAC implementadas como **Tablas Hash** (`dict`),
  y cada paquete queda en un **registro histórico ordenado** donde se audita
  con **búsqueda binaria**.
- **Capa física:** el paquete que llega a destino se transmite como una señal
  (suma de tonos piloto) que pasa **obligatoriamente** por el `CanalFisico`,
  donde sufre **atenuación log-distancia** y **ruido térmico kTBF**. El
  `Receptor` analiza la señal sucia con **FFT (`numpy.fft`)**, detecta los
  tonos y estima la SNR.

## Estructura

```
proyecto_telecom/
├── main.py                  # Simulación completa + gráficos
├── telecom/
│   ├── componente.py        # ComponenteEnlace (superclase abstracta)
│   ├── transmisor.py        # Transmisor
│   ├── canal.py             # CanalFisico (atenuación + ruido)
│   ├── receptor.py          # Receptor (FFT, detección, SNR)
│   ├── enrutador.py         # Enrutador (tablas Hash IP/MAC)
│   ├── registro.py          # RegistroPaquetes (búsqueda binaria)
│   ├── enlace.py            # EnlaceTelecom (clase gestora, composición)
│   ├── datos.py             # Paquete, Senal, ResultadoEspectral
│   └── graficos.py          # Gráficos estándar IEEE
├── benchmarks/complejidad.py  # Mediciones Big-O para el informe
├── tests/test_telecom.py      # Pruebas unitarias
├── docs/                      # UML (Mermaid + PNG) y guía de hitos
└── resultados/                # PDFs generados
```

## Uso

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py                                   # escenario base (1 km)
python main.py --distancia 5000 --paquetes 1000  # otro escenario
python -m benchmarks.complejidad                 # gráficos Big-O
python -m pytest                                 # pruebas
flake8 .                                         # verificación PEP8
```

## Modelo físico

| Magnitud | Expresión | Valor base |
|---|---|---|
| Pérdida de trayecto | PL(d) = 20·log10(4π·d0/λ) + 10·n·log10(d/d0) | n = 3.5, fc = 2.4 GHz |
| Ruido térmico | N = k·T·B·F | T = 290 K, B = 8 kHz, NF = 6 dB |
| Potencia por tono | A = √(2P/K) | P = 1 W, K = 4 tonos |
| Espectro | P_k = 2·\|X_k\|² / N² | fs = 20 kHz, N = 2000 |

Con n = 2 la pérdida se reduce a la fórmula de Friis (espacio libre). La SNR
estimada por FFT coincide con la teórica (Pt − PL − N) con un error menor a
0.5 dB (verificado en `tests/`).
