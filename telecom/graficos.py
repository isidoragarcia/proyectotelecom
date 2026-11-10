"""Gráficos bajo estándar IEEE: grilla, ejes con unidades, sin título
superior y con un caption inferior breve y técnico."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sin ventana: evita fallos al exportar

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from telecom.datos import ResultadoEspectral, w_a_dbm  # noqa: E402

# Paleta apta para daltonismo (verificada: separación CVD y contraste).
AZUL = "#0072B2"
BERMELLON = "#D55E00"
VERDE = "#009E73"
GRIS = "#6B6B6B"

ANCHO_COLUMNA_IEEE_IN = 3.5  # una columna IEEE = 3.5 pulgadas
CARACTERES_POR_LINEA_CAPTION = 58


def configurar_estilo_ieee() -> None:
    """Aplica una configuración global sobria, tipo publicación IEEE."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 8,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.grid": True,
        "grid.linestyle": ":",
        "grid.linewidth": 0.5,
        "grid.color": "#B0B0B0",
        "axes.linewidth": 0.6,
        "lines.linewidth": 1.0,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,  # fuentes embebidas (requisito de IEEE Xplore)
    })


def _crear_figura(alto_in: float = 2.6) -> tuple[plt.Figure, plt.Axes]:
    """Figura de una columna IEEE con espacio inferior para el caption."""
    configurar_estilo_ieee()
    return plt.subplots(figsize=(ANCHO_COLUMNA_IEEE_IN, alto_in))


def _guardar_con_caption(
    fig: plt.Figure, caption: str, ruta: str | Path
) -> Path:
    """Agrega el caption inferior (nunca un título superior) y exporta."""
    texto = textwrap.fill(caption, CARACTERES_POR_LINEA_CAPTION)
    n_lineas = texto.count("\n") + 1
    margen_inferior = 0.20 + 0.055 * n_lineas
    fig.subplots_adjust(left=0.16, right=0.97, top=0.97,
                        bottom=margen_inferior)
    fig.text(0.5, 0.015, texto, ha="center", va="bottom", fontsize=7.5)
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta)
    plt.close(fig)
    return ruta


def graficar_espectro(
    resultado: ResultadoEspectral,
    ruta: str | Path,
    distancia_m: float,
) -> Path:
    """Exporta el espectro de potencia recibido (Magnitud vs Frecuencia)."""
    fig, ax = _crear_figura()
    potencia_dbm = resultado.potencia_dbm()
    ax.plot(resultado.frecuencias_hz, potencia_dbm, color=AZUL,
            linewidth=0.7, label="Espectro recibido")
    piso_dbm = float(w_a_dbm(resultado.piso_ruido_w))
    ax.axhline(piso_dbm, color="black", linestyle="--", linewidth=0.9,
               label="Piso de ruido estimado")
    mascara = np.isin(resultado.frecuencias_hz, resultado.tonos_detectados_hz)
    ax.plot(resultado.frecuencias_hz[mascara], potencia_dbm[mascara],
            linestyle="none", marker="v", markersize=4, color=BERMELLON,
            label="Tonos detectados")
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Magnitud [dBm]")
    ax.set_xlim(0, resultado.frecuencias_hz[-1])
    # Margen superior para que la leyenda no tape ningún tono.
    ax.set_ylim(np.min(potencia_dbm) - 5, np.max(potencia_dbm) + 35)
    ax.legend(loc="upper right", framealpha=0.9)
    caption = (
        f"Fig. 1. Espectro unilateral de la señal recibida a "
        f"{distancia_m / 1e3:.1f} km obtenido con FFT. "
        f"SNR estimada: {resultado.snr_db:.1f} dB; "
        f"{resultado.tonos_detectados_hz.size} tonos detectados."
    )
    return _guardar_con_caption(fig, caption, ruta)


def graficar_snr_vs_distancia(
    distancias_m: np.ndarray,
    snr_simulada_db: np.ndarray,
    snr_teorica_db: np.ndarray,
    ruta: str | Path,
    exponente_perdida: float,
) -> Path:
    """Exporta la SNR simulada y teórica en función de la distancia."""
    fig, ax = _crear_figura()
    detectado = ~np.isnan(snr_simulada_db)
    ax.semilogx(distancias_m, snr_teorica_db, color=GRIS, linestyle="--",
                label="Teórica (log-distancia)")
    ax.semilogx(distancias_m[detectado], snr_simulada_db[detectado],
                color=AZUL, marker="o", markersize=3, linestyle="none",
                label="Simulada (FFT)")
    ax.axhline(0.0, color=BERMELLON, linewidth=0.8, label="SNR = 0 dB")
    ax.set_xlabel("Distancia [m]")
    ax.set_ylabel("SNR [dB]")
    ax.legend(loc="lower left", framealpha=0.9)
    sin_deteccion = distancias_m[~detectado]
    nota = (f" Sobre {sin_deteccion.min() / 1e3:.1f} km el receptor ya no "
            f"detecta tonos." if sin_deteccion.size else "")
    caption = (
        f"Fig. 2. SNR del enlace vs. distancia (n = {exponente_perdida:g}), "
        f"calculada en una sola operación matricial (D x N).{nota}"
    )
    return _guardar_con_caption(fig, caption, ruta)


def graficar_complejidad(
    tamanos: np.ndarray,
    tiempos_rapido_s: np.ndarray,
    tiempos_lento_s: np.ndarray,
    etiquetas: tuple[str, str],
    caption: str,
    ruta: str | Path,
) -> Path:
    """Exporta una comparación empírica de complejidad en escala log-log."""
    fig, ax = _crear_figura()
    ax.loglog(tamanos, tiempos_lento_s * 1e6, color=BERMELLON, marker="s",
              markersize=3, label=etiquetas[1])
    ax.loglog(tamanos, tiempos_rapido_s * 1e6, color=AZUL, marker="o",
              markersize=3, label=etiquetas[0])
    ax.set_xlabel("Cantidad de elementos n [-]")
    ax.set_ylabel("Tiempo por búsqueda [µs]")
    ax.legend(loc="upper left", framealpha=0.9)
    return _guardar_con_caption(fig, caption, ruta)
