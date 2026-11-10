"""Mediciones empíricas de complejidad para el informe del Hito 2.

1. Ruteo: Tabla Hash (dict) O(1) vs búsqueda en lista O(n).
2. Registro: búsqueda binaria O(log n) vs búsqueda secuencial O(n).

Uso (desde la raíz del proyecto):
    python -m benchmarks.complejidad
"""

from __future__ import annotations

import timeit
from pathlib import Path

import numpy as np

from telecom.enrutador import Enrutador
from telecom.graficos import graficar_complejidad
from telecom.registro import (ESTADO_ENTREGADO, EntradaRegistro,
                              RegistroPaquetes)

TAMANOS = np.array([10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6])
REPETICIONES = 20
RONDAS = 5
CARPETA_SALIDA = Path("resultados")


def medir(funcion) -> float:
    """Tiempo por llamada [s]: mínimo de varias rondas (reduce el ruido)."""
    return min(timeit.repeat(funcion, number=REPETICIONES,
                             repeat=RONDAS)) / REPETICIONES


def red_numero(i: int) -> str:
    """Red /24 única para el índice i (hasta 16 millones de redes)."""
    return f"{(i >> 16) & 255}.{(i >> 8) & 255}.{i & 255}.0/24"


def medir_ruteo() -> tuple[np.ndarray, np.ndarray]:
    """Tiempo por búsqueda de la peor ruta: dict vs lista de tuplas."""
    t_hash, t_lista = [], []
    for n in TAMANOS:
        enrutador = Enrutador("R-BENCH", "10.0.0.1")
        lista_rutas = []
        for i in range(n):
            enrutador.agregar_ruta(red_numero(i), "R2")
            lista_rutas.append((red_numero(i), "R2"))
        # Peor caso para la lista: la ruta buscada es la última.
        ip_objetivo = red_numero(n - 1).replace(".0/24", ".7")
        red_objetivo = red_numero(n - 1)

        def buscar_en_lista() -> str | None:
            for red, salto in lista_rutas:
                if red == red_objetivo:
                    return salto
            return None

        t_hash.append(
            medir(lambda: enrutador.buscar_siguiente_salto(ip_objetivo)))
        t_lista.append(medir(buscar_en_lista))
        print(f"  ruteo   n={n:>9,}  hash={t_hash[-1] * 1e6:9.2f} us"
              f"  lista={t_lista[-1] * 1e6:12.2f} us")
    return np.array(t_hash), np.array(t_lista)


def medir_busqueda() -> tuple[np.ndarray, np.ndarray]:
    """Tiempo por búsqueda en el registro: binaria vs secuencial."""
    t_binaria, t_secuencial = [], []
    for n in TAMANOS:
        registro = RegistroPaquetes()
        for i in range(1, n + 1):
            registro.registrar(EntradaRegistro(i, "10.0.3.20",
                                               ESTADO_ENTREGADO, 3, ()))
        objetivo = int(n)  # peor caso para la secuencial: el último
        t_binaria.append(
            medir(lambda: registro.buscar_binaria_recursiva(objetivo)))
        t_secuencial.append(
            medir(lambda: registro.buscar_secuencial(objetivo)))
        print(f"  busqueda n={n:>9,}  binaria={t_binaria[-1] * 1e6:8.2f} us"
              f"  secuencial={t_secuencial[-1] * 1e6:12.2f} us"
              f"  (log2 n = {np.log2(n):.1f} comparaciones)")
    return np.array(t_binaria), np.array(t_secuencial)


def main() -> None:
    """Ejecuta ambos experimentos y exporta los gráficos IEEE."""
    print("Midiendo ruteo (Hash vs lista)...")
    t_hash, t_lista = medir_ruteo()
    graficar_complejidad(
        TAMANOS, t_hash, t_lista,
        ("Tabla Hash (dict), O(1)", "Lista secuencial, O(n)"),
        "Fig. 3. Tiempo de búsqueda de la ruta en el peor caso según el "
        "número de redes en la tabla del enrutador.",
        CARPETA_SALIDA / "complejidad_ruteo.pdf")

    print("Midiendo búsqueda en el registro (binaria vs secuencial)...")
    t_binaria, t_secuencial = medir_busqueda()
    graficar_complejidad(
        TAMANOS, t_binaria, t_secuencial,
        ("Búsqueda binaria, O(log n)", "Búsqueda secuencial, O(n)"),
        "Fig. 4. Tiempo de búsqueda de un paquete en el registro histórico "
        "ordenado según la cantidad de paquetes almacenados.",
        CARPETA_SALIDA / "complejidad_busqueda.pdf")
    print(f"Gráficos guardados en {CARPETA_SALIDA}/")


if __name__ == "__main__":
    main()
