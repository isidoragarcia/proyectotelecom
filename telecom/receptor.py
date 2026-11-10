"""Receptor: analiza el espectro de la señal recibida mediante FFT."""

from __future__ import annotations

import numpy as np

from telecom.componente import ComponenteEnlace
from telecom.datos import ResultadoEspectral, Senal, w_a_dbm

# La potencia de ruido por bin sigue una distribución exponencial, cuya
# mediana es ln(2) veces su media. Se usa para estimar el piso de ruido.
FACTOR_MEDIANA_EXPONENCIAL = np.log(2.0)


class Receptor(ComponenteEnlace):
    """Receptor con análisis espectral (DSP) vectorizado.

    Atributos privados:
        __frecuencia_muestreo_hz: fs esperada de la señal [Hz].
        __sensibilidad_dbm: Potencia mínima para considerar válido el enlace.
        __umbral_deteccion_db: Margen sobre el piso de ruido para declarar
            que un bin contiene un tono.
    """

    def __init__(
        self,
        id_componente: str,
        frecuencia_muestreo_hz: float,
        sensibilidad_dbm: float = -120.0,
        umbral_deteccion_db: float = 13.0,
    ) -> None:
        super().__init__(id_componente)
        self.__frecuencia_muestreo_hz = 0.0
        self.__sensibilidad_dbm = 0.0
        self.__umbral_deteccion_db = 0.0
        self.ajustar_frecuencia_muestreo(frecuencia_muestreo_hz)
        self.ajustar_sensibilidad(sensibilidad_dbm)
        self.ajustar_umbral_deteccion(umbral_deteccion_db)

    # ------------------------------------------------------------------
    # Getters y setters
    # ------------------------------------------------------------------
    def obtener_frecuencia_muestreo(self) -> float:
        """Frecuencia de muestreo esperada [Hz]."""
        return self.__frecuencia_muestreo_hz

    def obtener_sensibilidad(self) -> float:
        """Sensibilidad del receptor [dBm]."""
        return self.__sensibilidad_dbm

    def obtener_umbral_deteccion(self) -> float:
        """Umbral de detección de tonos sobre el piso de ruido [dB]."""
        return self.__umbral_deteccion_db

    def ajustar_frecuencia_muestreo(self, frecuencia_hz: float) -> None:
        """Ajusta la fs esperada (debe ser positiva)."""
        if frecuencia_hz <= 0:
            raise ValueError("La frecuencia de muestreo debe ser positiva.")
        self.__frecuencia_muestreo_hz = float(frecuencia_hz)

    def ajustar_sensibilidad(self, sensibilidad_dbm: float) -> None:
        """Ajusta la sensibilidad (rango realista: -150 a 0 dBm)."""
        if not -150.0 <= sensibilidad_dbm <= 0.0:
            raise ValueError("La sensibilidad debe estar entre -150 y 0 dBm.")
        self.__sensibilidad_dbm = float(sensibilidad_dbm)

    def ajustar_umbral_deteccion(self, umbral_db: float) -> None:
        """Ajusta el umbral de detección (debe ser positivo)."""
        if umbral_db <= 0:
            raise ValueError("El umbral de detección debe ser positivo.")
        self.__umbral_deteccion_db = float(umbral_db)

    # ------------------------------------------------------------------
    # Procesamiento digital de señales (sin ciclos for)
    # ------------------------------------------------------------------
    def calcular_espectro(
        self, muestras: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Espectro de potencia unilateral mediante numpy.fft.

        Acepta un vector (N,) o una matriz (D, N); la FFT se aplica sobre
        el último eje. Con P_k = |X_k|^2 / N^2 (duplicado en los bins que
        no son DC ni Nyquist), un tono de amplitud A aparece como A^2 / 2,
        que es exactamente su potencia media (teorema de Parseval).

        Returns:
            (frecuencias [Hz], potencia por bin [W]).
        """
        n = muestras.shape[-1]
        espectro = np.fft.rfft(muestras, axis=-1)
        frecuencias = np.fft.rfftfreq(n, d=1.0 / self.__frecuencia_muestreo_hz)
        potencia = np.abs(espectro) ** 2 / n ** 2
        fin = -1 if n % 2 == 0 else None  # el bin de Nyquist no se duplica
        potencia[..., 1:fin] *= 2.0
        return frecuencias, potencia

    def detectar_tonos(self, potencia_w: np.ndarray) -> np.ndarray:
        """Máscara booleana de bins que contienen un tono.

        Un bin es tono si (1) supera el piso de ruido más el umbral y
        (2) es un máximo local. Todo con máscaras booleanas y slicing.
        """
        piso = self.estimar_piso_ruido(potencia_w)
        umbral = piso * 10.0 ** (self.__umbral_deteccion_db / 10.0)
        sobre_umbral = potencia_w > umbral
        relleno = np.pad(potencia_w, [(0, 0)] * (potencia_w.ndim - 1)
                         + [(1, 1)], constant_values=-np.inf)
        maximo_local = ((relleno[..., 1:-1] >= relleno[..., :-2])
                        & (relleno[..., 1:-1] >= relleno[..., 2:]))
        return sobre_umbral & maximo_local

    @staticmethod
    def estimar_piso_ruido(potencia_w: np.ndarray) -> np.ndarray:
        """Potencia media de ruido por bin, estimada con la mediana."""
        mediana = np.median(potencia_w, axis=-1, keepdims=True)
        return mediana / FACTOR_MEDIANA_EXPONENCIAL

    def estimar_snr_db(
        self, potencia_w: np.ndarray, mascara_tonos: np.ndarray
    ) -> np.ndarray:
        """SNR [dB] = potencia en tonos / potencia de ruido total.

        Si no se detecta ningún tono, la SNR no se puede estimar y se
        retorna NaN (en vez de un valor arbitrariamente bajo).
        """
        piso = self.estimar_piso_ruido(potencia_w)[..., 0]
        n_bins = potencia_w.shape[-1]
        n_tonos = mascara_tonos.sum(axis=-1)
        potencia_tonos = np.where(mascara_tonos, potencia_w, 0.0).sum(axis=-1)
        senal = np.maximum(potencia_tonos - piso * n_tonos, 1e-30)
        ruido = np.maximum(piso * n_bins, 1e-30)
        snr_db = 10.0 * np.log10(senal / ruido)
        return np.where(n_tonos > 0, snr_db, np.nan)

    def procesar(self, entrada: Senal) -> ResultadoEspectral:
        """Analiza una señal recibida y reporta tonos, SNR y validez."""
        self._verificar_servicio()
        if not isinstance(entrada, Senal):
            raise TypeError("El receptor solo procesa objetos Senal.")
        if not np.isclose(entrada.frecuencia_muestreo_hz,
                          self.__frecuencia_muestreo_hz):
            raise ValueError("La fs de la señal no coincide con el receptor.")
        frecuencias, potencia = self.calcular_espectro(entrada.muestras)
        mascara = self.detectar_tonos(potencia)
        potencia_dbm = float(w_a_dbm(entrada.potencia_media_w()))
        return ResultadoEspectral(
            frecuencias_hz=frecuencias,
            potencia_w=potencia,
            tonos_detectados_hz=frecuencias[mascara],
            snr_db=float(self.estimar_snr_db(potencia, mascara)),
            potencia_recibida_dbm=potencia_dbm,
            enlace_valido=potencia_dbm >= self.__sensibilidad_dbm,
            piso_ruido_w=float(self.estimar_piso_ruido(potencia)[0]),
        )

    def procesar_lote(self, matriz: np.ndarray) -> np.ndarray:
        """SNR [dB] de D señales apiladas en una matriz (D, N), sin for."""
        self._verificar_servicio()
        _, potencia = self.calcular_espectro(matriz)
        mascara = self.detectar_tonos(potencia)
        return self.estimar_snr_db(potencia, mascara)
