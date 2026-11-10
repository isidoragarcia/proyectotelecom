"""Transmisor: convierte paquetes en una señal física muestreada."""

from __future__ import annotations

import numpy as np

from telecom.componente import ComponenteEnlace
from telecom.datos import Paquete, Senal


class Transmisor(ComponenteEnlace):
    """Genera una señal compuesta por tonos piloto (firma espectral).

    La señal es la suma de K sinusoides. La amplitud de cada tono se
    escala para que la potencia media total sea exactamente la potencia
    de transmisión configurada: P = K * A^2 / 2  =>  A = sqrt(2P / K).

    Atributos privados:
        __potencia_tx_w: Potencia de transmisión [W].
        __frecuencia_muestreo_hz: Frecuencia de muestreo [Hz].
        __ancho_banda_hz: Ancho de banda ocupado [Hz].
        __frecuencias_tono_hz: Tonos que componen la firma [Hz].
        __duracion_simbolo_s: Duración de la señal por paquete [s].
    """

    def __init__(
        self,
        id_componente: str,
        potencia_tx_w: float,
        frecuencia_muestreo_hz: float,
        ancho_banda_hz: float,
        frecuencias_tono_hz: list[float],
        duracion_simbolo_s: float = 0.1,
    ) -> None:
        super().__init__(id_componente)
        self.__potencia_tx_w = 0.0
        self.__frecuencia_muestreo_hz = 0.0
        self.__ancho_banda_hz = 0.0
        self.__frecuencias_tono_hz = np.array([])
        self.__duracion_simbolo_s = 0.0
        # Se usan los setters para que la validación se aplique desde el
        # inicio (no se puede construir un transmisor inválido).
        self.ajustar_potencia_tx(potencia_tx_w)
        self.ajustar_muestreo(frecuencia_muestreo_hz, ancho_banda_hz)
        self.ajustar_tonos(frecuencias_tono_hz)
        self.ajustar_duracion_simbolo(duracion_simbolo_s)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def obtener_potencia_tx(self) -> float:
        """Potencia de transmisión [W]."""
        return self.__potencia_tx_w

    def obtener_frecuencia_muestreo(self) -> float:
        """Frecuencia de muestreo [Hz]."""
        return self.__frecuencia_muestreo_hz

    def obtener_ancho_banda(self) -> float:
        """Ancho de banda [Hz]."""
        return self.__ancho_banda_hz

    def obtener_tonos(self) -> np.ndarray:
        """Copia de los tonos [Hz] (no expone el arreglo original)."""
        return self.__frecuencias_tono_hz.copy()

    def obtener_duracion_simbolo(self) -> float:
        """Duración de la señal generada por paquete [s]."""
        return self.__duracion_simbolo_s

    # ------------------------------------------------------------------
    # Setters con validación física
    # ------------------------------------------------------------------
    def ajustar_potencia_tx(self, potencia_w: float) -> None:
        """Ajusta la potencia de transmisión (0 < P <= 100 W)."""
        if not 0.0 < potencia_w <= 100.0:
            raise ValueError("La potencia debe estar entre 0 y 100 W.")
        self.__potencia_tx_w = float(potencia_w)

    def ajustar_muestreo(
        self, frecuencia_muestreo_hz: float, ancho_banda_hz: float
    ) -> None:
        """Ajusta fs y B verificando el criterio de Nyquist (fs >= 2B)."""
        if ancho_banda_hz <= 0:
            raise ValueError("El ancho de banda debe ser positivo.")
        if frecuencia_muestreo_hz < 2.0 * ancho_banda_hz:
            raise ValueError("Nyquist: la fs debe ser al menos 2 veces B.")
        self.__frecuencia_muestreo_hz = float(frecuencia_muestreo_hz)
        self.__ancho_banda_hz = float(ancho_banda_hz)

    def ajustar_tonos(self, frecuencias_hz: list[float]) -> None:
        """Define los tonos piloto; todos deben caer dentro de (0, B)."""
        tonos = np.asarray(frecuencias_hz, dtype=float)
        if tonos.size == 0:
            raise ValueError("Se requiere al menos un tono.")
        if np.any(tonos <= 0) or np.any(tonos >= self.__ancho_banda_hz):
            raise ValueError("Todos los tonos deben estar dentro de (0, B).")
        self.__frecuencias_tono_hz = tonos

    def ajustar_duracion_simbolo(self, duracion_s: float) -> None:
        """Ajusta la duración de la señal por paquete (> 0)."""
        if duracion_s <= 0:
            raise ValueError("La duración debe ser positiva.")
        self.__duracion_simbolo_s = float(duracion_s)

    # ------------------------------------------------------------------
    # Lógica del transmisor
    # ------------------------------------------------------------------
    def generar_senal(self, duracion_s: float | None = None) -> Senal:
        """Genera la suma de tonos de forma vectorizada (sin ciclos for).

        Se usa broadcasting: tonos (K, 1) x tiempo (1, N) -> matriz (K, N),
        que luego se suma por filas para obtener la señal de N muestras.
        """
        self._verificar_servicio()
        duracion = duracion_s or self.__duracion_simbolo_s
        fs = self.__frecuencia_muestreo_hz
        n_muestras = int(round(duracion * fs))
        t = np.arange(n_muestras) / fs
        k = self.__frecuencias_tono_hz.size
        amplitud = np.sqrt(2.0 * self.__potencia_tx_w / k)
        fases = 2.0 * np.pi * self.__frecuencias_tono_hz[:, None] * t[None, :]
        muestras = amplitud * np.sin(fases).sum(axis=0)
        return Senal(muestras=muestras, frecuencia_muestreo_hz=fs)

    def procesar(self, entrada: Paquete) -> Senal:
        """Convierte un paquete en su señal física (polimorfismo)."""
        if not isinstance(entrada, Paquete):
            raise TypeError("El transmisor solo procesa objetos Paquete.")
        return self.generar_senal()
