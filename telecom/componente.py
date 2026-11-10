"""Superclase común de todos los componentes del enlace de telecomunicaciones.

Define la identidad y el estado de operación compartidos por el Transmisor,
el CanalFisico, el Receptor y el Enrutador, además del método polimórfico
``procesar`` que cada subclase implementa a su manera.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ComponenteEnlace(ABC):
    """Componente genérico de un enlace de telecomunicaciones.

    Atributos privados:
        __id_componente: Identificador único del componente (ej. "TX-01").
        __en_servicio: Indica si el componente está operativo.
    """

    def __init__(self, id_componente: str) -> None:
        if not isinstance(id_componente, str) or not id_componente.strip():
            raise ValueError("El identificador debe ser un texto no vacío.")
        self.__id_componente = id_componente
        self.__en_servicio = True

    # ------------------------------------------------------------------
    # Getters y setters seguros
    # ------------------------------------------------------------------
    def obtener_id(self) -> str:
        """Retorna el identificador único del componente."""
        return self.__id_componente

    def esta_en_servicio(self) -> bool:
        """Indica si el componente está operativo."""
        return self.__en_servicio

    def poner_en_servicio(self) -> None:
        """Habilita el componente para procesar datos."""
        self.__en_servicio = True

    def poner_fuera_de_servicio(self) -> None:
        """Deshabilita el componente (simula una falla o mantención)."""
        self.__en_servicio = False

    def _verificar_servicio(self) -> None:
        """Lanza un error si el componente está fuera de servicio."""
        if not self.__en_servicio:
            raise RuntimeError(
                f"{self.__id_componente} está fuera de servicio."
            )

    # ------------------------------------------------------------------
    # Polimorfismo
    # ------------------------------------------------------------------
    @abstractmethod
    def procesar(self, entrada: Any) -> Any:
        """Procesa la entrada según el rol del componente en el enlace.

        Transmisor: Paquete -> Senal.
        CanalFisico: Senal -> Senal degradada.
        Receptor: Senal -> ResultadoEspectral.
        Enrutador: Paquete -> id del siguiente salto.
        """

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id='{self.__id_componente}')"
