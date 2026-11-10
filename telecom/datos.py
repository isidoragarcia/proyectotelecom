"""Estructuras de datos que viajan entre los componentes del enlace."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Paquete:
    """Paquete de datos de la capa lógica (red).

    Attributes:
        id_paquete: Número de secuencia único y creciente.
        ip_origen: Dirección IPv4 de origen (ej. "10.0.1.5").
        ip_destino: Dirección IPv4 de destino.
        mac_destino: Dirección MAC del equipo final.
        ttl: Tiempo de vida (saltos restantes antes de descartarse).
        carga_util: Contenido del paquete.
    """

    id_paquete: int
    ip_origen: str
    ip_destino: str
    mac_destino: str
    ttl: int = 16
    carga_util: str = ""


@dataclass(frozen=True)
class Senal:
    """Señal muestreada de la capa física.

    Attributes:
        muestras: Arreglo 1D de NumPy con la señal [V] (carga de 1 ohm).
        frecuencia_muestreo_hz: Frecuencia de muestreo [Hz].
    """

    muestras: np.ndarray
    frecuencia_muestreo_hz: float

    def numero_muestras(self) -> int:
        """Cantidad de muestras de la señal."""
        return int(self.muestras.size)

    def vector_tiempo(self) -> np.ndarray:
        """Vector de tiempo [s] asociado a cada muestra."""
        return np.arange(self.muestras.size) / self.frecuencia_muestreo_hz

    def potencia_media_w(self) -> float:
        """Potencia media [W] sobre una carga de 1 ohm: mean(x^2)."""
        return float(np.mean(self.muestras ** 2))


@dataclass
class ResultadoEspectral:
    """Resultado del análisis FFT hecho por el Receptor.

    Attributes:
        frecuencias_hz: Eje de frecuencias del espectro unilateral [Hz].
        potencia_w: Potencia por bin de frecuencia [W].
        tonos_detectados_hz: Frecuencias de los tonos encontrados [Hz].
        snr_db: Relación señal a ruido estimada [dB].
        potencia_recibida_dbm: Potencia media recibida [dBm].
        enlace_valido: False si la potencia está bajo la sensibilidad.
    """

    frecuencias_hz: np.ndarray
    potencia_w: np.ndarray
    tonos_detectados_hz: np.ndarray
    snr_db: float
    potencia_recibida_dbm: float
    enlace_valido: bool
    piso_ruido_w: float = field(default=0.0)

    def potencia_dbm(self) -> np.ndarray:
        """Espectro de potencia expresado en dBm."""
        return w_a_dbm(self.potencia_w)


def w_a_dbm(potencia_w: np.ndarray | float) -> np.ndarray | float:
    """Convierte potencia en watts a dBm (vectorizado)."""
    return 10.0 * np.log10(np.maximum(potencia_w, 1e-30) / 1e-3)


def dbm_a_w(potencia_dbm: np.ndarray | float) -> np.ndarray | float:
    """Convierte potencia en dBm a watts (vectorizado)."""
    return 1e-3 * 10.0 ** (np.asarray(potencia_dbm) / 10.0)
