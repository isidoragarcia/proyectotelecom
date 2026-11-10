"""Clase gestora: orquesta la capa lógica (ruteo) y la capa física."""

from __future__ import annotations

import numpy as np

from telecom.canal import CanalFisico
from telecom.datos import Paquete, ResultadoEspectral
from telecom.enrutador import ENTREGA_LOCAL, Enrutador
from telecom.receptor import Receptor
from telecom.registro import (ERROR_CAPA_FISICA, ERROR_MAC, ERROR_SIN_RUTA,
                              ERROR_TTL, ESTADO_ENTREGADO, EntradaRegistro,
                              RegistroPaquetes)
from telecom.transmisor import Transmisor

MAXIMO_SALTOS = 64


class EnlaceTelecom:
    """Enlace de extremo a extremo (composición).

    Un EnlaceTelecom *tiene* un Transmisor, un CanalFisico, un Receptor,
    una red de Enrutadores y un RegistroPaquetes. No hereda de ellos.

    Atributos privados:
        __transmisor, __canal, __receptor: Cadena física.
        __enrutadores: dict {id -> Enrutador} para acceso O(1).
        __registro: Bitácora ordenada de paquetes.
        __ultimo_resultado: Último análisis espectral (para graficar).
    """

    def __init__(
        self,
        transmisor: Transmisor,
        canal: CanalFisico,
        receptor: Receptor,
    ) -> None:
        if not np.isclose(transmisor.obtener_frecuencia_muestreo(),
                          receptor.obtener_frecuencia_muestreo()):
            raise ValueError("Transmisor y receptor deben usar la misma fs.")
        self.__transmisor = transmisor
        self.__canal = canal
        self.__receptor = receptor
        self.__enrutadores: dict[str, Enrutador] = {}
        self.__registro = RegistroPaquetes()
        self.__ultimo_resultado: ResultadoEspectral | None = None

    # ------------------------------------------------------------------
    # Acceso controlado a los componentes
    # ------------------------------------------------------------------
    def obtener_transmisor(self) -> Transmisor:
        """Transmisor del enlace."""
        return self.__transmisor

    def obtener_canal(self) -> CanalFisico:
        """Canal físico del enlace."""
        return self.__canal

    def obtener_receptor(self) -> Receptor:
        """Receptor del enlace."""
        return self.__receptor

    def obtener_registro(self) -> RegistroPaquetes:
        """Registro histórico de paquetes."""
        return self.__registro

    def obtener_ultimo_resultado(self) -> ResultadoEspectral | None:
        """Último resultado espectral calculado."""
        return self.__ultimo_resultado

    def agregar_enrutador(self, enrutador: Enrutador) -> None:
        """Agrega un enrutador a la red. O(1)."""
        if enrutador.obtener_id() in self.__enrutadores:
            raise ValueError("Ya existe un enrutador con ese id.")
        self.__enrutadores[enrutador.obtener_id()] = enrutador

    def obtener_enrutador(self, id_enrutador: str) -> Enrutador:
        """Busca un enrutador por su id en O(1)."""
        if id_enrutador not in self.__enrutadores:
            raise KeyError(f"No existe el enrutador {id_enrutador}.")
        return self.__enrutadores[id_enrutador]

    # ------------------------------------------------------------------
    # Simulación de extremo a extremo
    # ------------------------------------------------------------------
    def enviar_paquete(
        self, paquete: Paquete, id_enrutador_entrada: str
    ) -> EntradaRegistro:
        """Rutea un paquete salto a salto y, si llega a destino, lo
        transmite por la capa física (Tx -> Canal -> Rx)."""
        ruta: list[str] = []
        actual = id_enrutador_entrada
        estado = ERROR_SIN_RUTA
        snr_db = None
        while len(ruta) < MAXIMO_SALTOS:
            enrutador = self.__enrutadores.get(actual)
            if enrutador is None:
                estado = ERROR_SIN_RUTA
                break
            ruta.append(actual)
            decision = enrutador.procesar(paquete)
            if decision is None:
                estado = self.__diagnosticar_descarte(enrutador, paquete)
                break
            if decision == ENTREGA_LOCAL:
                estado, snr_db = self.__transmitir_capa_fisica(paquete)
                break
            actual = decision
        entrada = EntradaRegistro(
            id_paquete=paquete.id_paquete,
            ip_destino=paquete.ip_destino,
            estado=estado,
            saltos=len(ruta),
            ruta=tuple(ruta),
            snr_db=snr_db,
        )
        self.__registro.registrar(entrada)
        return entrada

    @staticmethod
    def __diagnosticar_descarte(enrutador: Enrutador, paquete: Paquete) -> str:
        """Determina el motivo por el que un enrutador descartó el paquete."""
        if paquete.ttl <= 0:
            return ERROR_TTL
        if enrutador.buscar_siguiente_salto(paquete.ip_destino) is None:
            return ERROR_SIN_RUTA
        return ERROR_MAC

    def __transmitir_capa_fisica(
        self, paquete: Paquete
    ) -> tuple[str, float]:
        """La señal pasa obligatoriamente por el canal antes del receptor."""
        senal_tx = self.__transmisor.procesar(paquete)
        senal_rx = self.__canal.procesar(senal_tx)
        resultado = self.__receptor.procesar(senal_rx)
        self.__ultimo_resultado = resultado
        estado = (ESTADO_ENTREGADO if resultado.enlace_valido
                  else ERROR_CAPA_FISICA)
        return estado, resultado.snr_db

    def simular_barrido_distancias(
        self, distancias_m: np.ndarray
    ) -> np.ndarray:
        """SNR [dB] del enlace para D distancias, calculado sin ciclos for.

        La señal (N,) se propaga a todas las distancias a la vez como una
        matriz (D, N) y la FFT se aplica por filas.
        """
        senal = self.__transmisor.generar_senal()
        matriz_rx = self.__canal.procesar_barrido(senal, distancias_m)
        return self.__receptor.procesar_lote(matriz_rx)
