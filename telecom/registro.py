"""Registro histórico de paquetes con búsqueda binaria.

Los paquetes se registran en orden estrictamente creciente de id (número de
secuencia), por lo que el registro está ordenado por construcción y admite
búsqueda binaria O(log n) sin ordenar nada.
"""

from __future__ import annotations

from dataclasses import dataclass

ESTADO_ENTREGADO = "ENTREGADO"
ERROR_SIN_RUTA = "ERR_SIN_RUTA"
ERROR_TTL = "ERR_TTL_AGOTADO"
ERROR_MAC = "ERR_MAC_DESCONOCIDA"
ERROR_CAPA_FISICA = "ERR_SENAL_BAJO_SENSIBILIDAD"


@dataclass(frozen=True)
class EntradaRegistro:
    """Una línea del registro histórico."""

    id_paquete: int
    ip_destino: str
    estado: str
    saltos: int
    ruta: tuple[str, ...]
    snr_db: float | None = None

    def es_error(self) -> bool:
        """True si el paquete no fue entregado."""
        return self.estado != ESTADO_ENTREGADO


class RegistroPaquetes:
    """Bitácora ordenada de paquetes.

    Atributos privados:
        __entradas: Lista de EntradaRegistro ordenada por id_paquete.
        __ids: Lista paralela con solo los ids (comparaciones más rápidas).
    """

    def __init__(self) -> None:
        self.__entradas: list[EntradaRegistro] = []
        self.__ids: list[int] = []

    def __len__(self) -> int:
        return len(self.__entradas)

    def registrar(self, entrada: EntradaRegistro) -> None:
        """Agrega una entrada al final. O(1) amortizado.

        Exige que el id sea mayor que el último, lo que mantiene el
        invariante "lista ordenada" sin necesidad de reordenar.
        """
        if self.__ids and entrada.id_paquete <= self.__ids[-1]:
            raise ValueError("Los ids deben registrarse en orden creciente.")
        self.__entradas.append(entrada)
        self.__ids.append(entrada.id_paquete)

    def obtener_entradas(self) -> tuple[EntradaRegistro, ...]:
        """Copia inmutable de todas las entradas."""
        return tuple(self.__entradas)

    def contar_errores(self) -> dict[str, int]:
        """Cantidad de paquetes por estado (Tabla Hash de conteo)."""
        conteo: dict[str, int] = {}
        for entrada in self.__entradas:
            conteo[entrada.estado] = conteo.get(entrada.estado, 0) + 1
        return conteo

    # ------------------------------------------------------------------
    # Búsquedas
    # ------------------------------------------------------------------
    def buscar_binaria_recursiva(
        self, id_objetivo: int
    ) -> EntradaRegistro | None:
        """Búsqueda binaria recursiva. O(log n) en tiempo y en pila."""
        indice = self.__buscar_rec(id_objetivo, 0, len(self.__ids) - 1)
        return None if indice < 0 else self.__entradas[indice]

    def __buscar_rec(self, objetivo: int, bajo: int, alto: int) -> int:
        """Paso recursivo: descarta la mitad del intervalo en cada llamada.

        Se trabaja con índices (no con slicing) para no copiar la lista,
        lo que arruinaría la complejidad (cada slice cuesta O(n)).
        """
        if bajo > alto:
            return -1  # caso base: intervalo vacío, no está
        medio = (bajo + alto) // 2
        if self.__ids[medio] == objetivo:
            return medio  # caso base: encontrado
        if self.__ids[medio] < objetivo:
            return self.__buscar_rec(objetivo, medio + 1, alto)
        return self.__buscar_rec(objetivo, bajo, medio - 1)

    def buscar_binaria_iterativa(
        self, id_objetivo: int
    ) -> EntradaRegistro | None:
        """Búsqueda binaria iterativa. O(log n) en tiempo, O(1) memoria."""
        bajo, alto = 0, len(self.__ids) - 1
        while bajo <= alto:
            medio = (bajo + alto) // 2
            if self.__ids[medio] == id_objetivo:
                return self.__entradas[medio]
            if self.__ids[medio] < id_objetivo:
                bajo = medio + 1
            else:
                alto = medio - 1
        return None

    def buscar_secuencial(self, id_objetivo: int) -> EntradaRegistro | None:
        """Búsqueda lineal, solo como línea base de comparación. O(n)."""
        for entrada in self.__entradas:
            if entrada.id_paquete == id_objetivo:
                return entrada
        return None
