"""Benchmark empírico: búsqueda secuencial O(n) vs binaria O(log n).

Genera una tabla por consola 

"""

from __future__ import annotations

import time
from pathlib import Path

from telecom.registro import RegistroPaquetes

TAMANOS = [10**2, 10**3, 10**4, 10**5, 10**6]
REPETICIONES = 5


def construir_registro(n: int) -> RegistroPaquetes:
    """Registro con n entradas ordenadas (id = 1..n)."""
    reg = RegistroPaquetes()
    for i in range(1, n + 1):
        reg.registrar(i, f"10.0.0.{i % 256}", True, 1.0)
    return reg


def medir(funcion, *args) -> float:
    """Tiempo promedio [s] de REPETICIONES ejecuciones."""
    inicio = time.perf_counter()
    for _ in range(REPETICIONES):
        funcion(*args)
    return (time.perf_counter() - inicio) / REPETICIONES


def graficar(filas: list) -> None:
    """Genera el gráfico IEEE si matplotlib está instalado. Si no, avisa."""
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print("\n[aviso] matplotlib no está instalado: se omite el gráfico.")
        print("        Instálalo con: pip install matplotlib")
        return

    ns = [f[0] for f in filas]
    plt.figure(figsize=(7, 4.5))
    plt.loglog(ns, [f[1] for f in filas], "o-", label="Secuencial $O(n)$")
    plt.loglog(ns, [f[2] for f in filas], "s-", label="Binaria iterativa $O(\\log n)$")
    plt.loglog(ns, [f[3] for f in filas], "^-", label="Binaria recursiva $O(\\log n)$")
    plt.xlabel("Cantidad de entradas $n$")
    plt.ylabel("Tiempo de búsqueda [s]")
    plt.grid(True, which="both", linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    salida = Path("resultados/benchmark_busqueda.pdf")
    salida.parent.mkdir(exist_ok=True)
    plt.savefig(salida, format="pdf", bbox_inches="tight")
    print(f"\nGráfico exportado: {salida}")
    print("Caption sugerido: Comparación empírica del costo de búsqueda "
          "secuencial vs binaria en el registro de paquetes (escala log-log).")


def main() -> None:
    filas = []
    print(f"{'n':>10} | {'secuencial [us]':>16} | "
          f"{'binaria [us]':>13} | {'recursiva [us]':>14}")
    print("-" * 62)
    for n in TAMANOS:
        reg = construir_registro(n)
        objetivo = n  # peor caso para secuencial (último elemento)
        t_seq = medir(reg.buscar_secuencial, objetivo)
        t_bin = medir(reg.buscar_binaria, objetivo)
        t_rec = medir(reg.buscar_binaria_recursiva, objetivo)
        filas.append((n, t_seq, t_bin, t_rec))
        print(f"{n:>10,} | {t_seq*1e6:>16.2f} | "
              f"{t_bin*1e6:>13.2f} | {t_rec*1e6:>14.2f}")

    graficar(filas)


if __name__ == "__main__":
    main()