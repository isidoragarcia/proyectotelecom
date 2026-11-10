"""Canal físico: aplica atenuación por distancia y ruido térmico.

Modelo de pérdida log-distancia (con n = 2 se reduce a Friis/espacio libre):

    PL(d) [dB] = 20*log10(4*pi*d0 / lambda) + 10*n*log10(d / d0),  d0 = 1 m

Ruido térmico gaussiano con potencia (sobre 1 ohm):

    N = k * T * B * F,   F = 10^(NF/10)
"""

from __future__ import annotations

import numpy as np

from telecom.componente import ComponenteEnlace
from telecom.datos import Senal

K_BOLTZMANN = 1.380649e-23  # [J/K]
VELOCIDAD_LUZ = 299_792_458.0  # [m/s]
DISTANCIA_REFERENCIA_M = 1.0


class CanalFisico(ComponenteEnlace):
    """Medio de transmisión entre el Transmisor y el Receptor.

    La señal NO puede llegar al receptor sin pasar por ``procesar``, que
    internamente llama a los métodos privados de atenuación y ruido.

    Atributos privados:
        __distancia_m: Largo del enlace [m].
        __frecuencia_portadora_hz: Portadora usada para calcular lambda [Hz].
        __ancho_banda_hz: Ancho de banda de ruido [Hz].
        __exponente_perdida: n del modelo log-distancia (2 = espacio libre).
        __temperatura_k: Temperatura de ruido [K].
        __figura_ruido_db: Figura de ruido del receptor [dB].
        __generador: Generador aleatorio de NumPy (reproducible con semilla).
    """

    def __init__(
        self,
        id_componente: str,
        distancia_m: float,
        frecuencia_portadora_hz: float,
        ancho_banda_hz: float,
        exponente_perdida: float = 2.0,
        temperatura_k: float = 290.0,
        figura_ruido_db: float = 0.0,
        semilla: int | None = None,
    ) -> None:
        super().__init__(id_componente)
        self.__distancia_m = 0.0
        self.__frecuencia_portadora_hz = 0.0
        self.__ancho_banda_hz = 0.0
        self.__exponente_perdida = 0.0
        self.__temperatura_k = 0.0
        self.__figura_ruido_db = 0.0
        self.__generador = np.random.default_rng(semilla)
        self.ajustar_distancia(distancia_m)
        self.ajustar_frecuencia_portadora(frecuencia_portadora_hz)
        self.ajustar_ancho_banda(ancho_banda_hz)
        self.ajustar_exponente_perdida(exponente_perdida)
        self.ajustar_temperatura(temperatura_k)
        self.ajustar_figura_ruido(figura_ruido_db)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def obtener_distancia(self) -> float:
        """Largo del enlace [m]."""
        return self.__distancia_m

    def obtener_frecuencia_portadora(self) -> float:
        """Frecuencia portadora [Hz]."""
        return self.__frecuencia_portadora_hz

    def obtener_ancho_banda(self) -> float:
        """Ancho de banda de ruido [Hz]."""
        return self.__ancho_banda_hz

    def obtener_exponente_perdida(self) -> float:
        """Exponente de pérdida n."""
        return self.__exponente_perdida

    # ------------------------------------------------------------------
    # Setters con validación física
    # ------------------------------------------------------------------
    def ajustar_distancia(self, distancia_m: float) -> None:
        """Ajusta la distancia (debe ser >= d0 = 1 m)."""
        if distancia_m < DISTANCIA_REFERENCIA_M:
            raise ValueError("La distancia debe ser al menos 1 m.")
        self.__distancia_m = float(distancia_m)

    def ajustar_frecuencia_portadora(self, frecuencia_hz: float) -> None:
        """Ajusta la portadora (debe ser positiva)."""
        if frecuencia_hz <= 0:
            raise ValueError("La frecuencia portadora debe ser positiva.")
        self.__frecuencia_portadora_hz = float(frecuencia_hz)

    def ajustar_ancho_banda(self, ancho_banda_hz: float) -> None:
        """Ajusta el ancho de banda de ruido (debe ser positivo)."""
        if ancho_banda_hz <= 0:
            raise ValueError("El ancho de banda debe ser positivo.")
        self.__ancho_banda_hz = float(ancho_banda_hz)

    def ajustar_exponente_perdida(self, exponente: float) -> None:
        """Ajusta n: 2 (espacio libre) a 6 (interior con obstáculos)."""
        if not 2.0 <= exponente <= 6.0:
            raise ValueError("El exponente de pérdida debe estar en [2, 6].")
        self.__exponente_perdida = float(exponente)

    def ajustar_temperatura(self, temperatura_k: float) -> None:
        """Ajusta la temperatura de ruido (debe ser positiva)."""
        if temperatura_k <= 0:
            raise ValueError("La temperatura debe ser positiva [K].")
        self.__temperatura_k = float(temperatura_k)

    def ajustar_figura_ruido(self, figura_ruido_db: float) -> None:
        """Ajusta la figura de ruido (NF >= 0 dB)."""
        if figura_ruido_db < 0:
            raise ValueError("La figura de ruido no puede ser negativa.")
        self.__figura_ruido_db = float(figura_ruido_db)

    # ------------------------------------------------------------------
    # Leyes físicas (aceptan escalares o arreglos: vectorizadas)
    # ------------------------------------------------------------------
    def calcular_perdida_db(
        self, distancias_m: np.ndarray | float | None = None
    ) -> np.ndarray | float:
        """Pérdida de trayecto [dB] para una o varias distancias."""
        d = self.__distancia_m if distancias_m is None else distancias_m
        d = np.asarray(d, dtype=float)
        longitud_onda = VELOCIDAD_LUZ / self.__frecuencia_portadora_hz
        perdida_ref = 20.0 * np.log10(
            4.0 * np.pi * DISTANCIA_REFERENCIA_M / longitud_onda
        )
        perdida = perdida_ref + 10.0 * self.__exponente_perdida * np.log10(
            d / DISTANCIA_REFERENCIA_M
        )
        return float(perdida) if perdida.ndim == 0 else perdida

    def calcular_potencia_ruido_w(self) -> float:
        """Potencia de ruido térmico N = k*T*B*F [W]."""
        factor_ruido = 10.0 ** (self.__figura_ruido_db / 10.0)
        return (K_BOLTZMANN * self.__temperatura_k
                * self.__ancho_banda_hz * factor_ruido)

    # ------------------------------------------------------------------
    # Métodos internos (privados): la señal solo se degrada aquí
    # ------------------------------------------------------------------
    def __aplicar_atenuacion(
        self, muestras: np.ndarray, distancias_m: np.ndarray | float
    ) -> np.ndarray:
        """Escala la amplitud por sqrt(10^(-PL/10)).

        Si ``distancias_m`` es un arreglo (D,) y ``muestras`` es (N,), el
        broadcasting (D, 1) * (1, N) genera la matriz (D, N) de una vez.
        """
        perdida_db = np.asarray(self.calcular_perdida_db(distancias_m))
        factor_amplitud = 10.0 ** (-perdida_db / 20.0)
        return factor_amplitud[..., None] * muestras

    def __aplicar_ruido_termico(self, muestras: np.ndarray) -> np.ndarray:
        """Suma ruido gaussiano de varianza k*T*B*F a toda la matriz."""
        sigma = np.sqrt(self.calcular_potencia_ruido_w())
        ruido = self.__generador.normal(0.0, sigma, size=muestras.shape)
        return muestras + ruido

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------
    def procesar(self, entrada: Senal) -> Senal:
        """Propaga una señal por el canal a la distancia configurada."""
        self._verificar_servicio()
        if not isinstance(entrada, Senal):
            raise TypeError("El canal solo procesa objetos Senal.")
        atenuada = self.__aplicar_atenuacion(
            entrada.muestras, self.__distancia_m
        )
        recibida = self.__aplicar_ruido_termico(atenuada)
        return Senal(muestras=recibida,
                     frecuencia_muestreo_hz=entrada.frecuencia_muestreo_hz)

    def procesar_barrido(
        self, entrada: Senal, distancias_m: np.ndarray
    ) -> np.ndarray:
        """Propaga la misma señal a D distancias simultáneamente.

        Returns:
            Matriz (D, N): fila i = señal recibida a la distancia i.
            Todo se calcula con broadcasting, sin ciclos for.
        """
        self._verificar_servicio()
        distancias = np.asarray(distancias_m, dtype=float)
        if np.any(distancias < DISTANCIA_REFERENCIA_M):
            raise ValueError("Todas las distancias deben ser >= 1 m.")
        atenuadas = self.__aplicar_atenuacion(entrada.muestras, distancias)
        return self.__aplicar_ruido_termico(atenuadas)
