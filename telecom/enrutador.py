"""Enrutador con tablas de direccionamiento IP y MAC basadas en Hash."""

from __future__ import annotations

from telecom.componente import ComponenteEnlace
from telecom.datos import Paquete

ENTREGA_LOCAL = "LOCAL"


def red_de(ip: str) -> str:
    """Obtiene la red /24 de una IPv4. Ej: '10.0.3.25' -> '10.0.3.0/24'."""
    octetos = ip.split(".")
    if len(octetos) != 4 or not all(o.isdigit() and 0 <= int(o) <= 255
                                    for o in octetos):
        raise ValueError(f"Dirección IPv4 inválida: {ip}")
    return ".".join(octetos[:3]) + ".0/24"


class Enrutador(ComponenteEnlace):
    """Enrutador de capa 3 con conmutación de capa 2.

    Atributos privados:
        __ip_propia: IPv4 de la interfaz del enrutador.
        __tabla_ip: dict {red /24 -> id del siguiente salto o "LOCAL"}.
        __tabla_mac: dict {MAC -> puerto de salida}, para entrega local.
        __paquetes_procesados: Contador de paquetes que pasaron por aquí.

    Ambas tablas son Tablas Hash (dict de Python): la búsqueda de una clave
    cuesta O(1) en promedio, sin importar cuántas rutas existan.
    """

    def __init__(self, id_componente: str, ip_propia: str) -> None:
        super().__init__(id_componente)
        red_de(ip_propia)  # valida el formato
        self.__ip_propia = ip_propia
        self.__tabla_ip: dict[str, str] = {}
        self.__tabla_mac: dict[str, int] = {}
        self.__paquetes_procesados = 0

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def obtener_ip(self) -> str:
        """IPv4 propia del enrutador."""
        return self.__ip_propia

    def obtener_paquetes_procesados(self) -> int:
        """Cantidad de paquetes procesados."""
        return self.__paquetes_procesados

    def cantidad_rutas(self) -> int:
        """Número de redes conocidas en la tabla IP."""
        return len(self.__tabla_ip)

    def obtener_tabla_ip(self) -> dict[str, str]:
        """Copia de la tabla IP (no expone el diccionario interno)."""
        return dict(self.__tabla_ip)

    # ------------------------------------------------------------------
    # Configuración de las tablas Hash
    # ------------------------------------------------------------------
    def agregar_ruta(self, red_destino: str, siguiente_salto: str) -> None:
        """Registra que la red ``red_destino`` se alcanza por
        ``siguiente_salto`` (id de otro enrutador o "LOCAL"). O(1)."""
        if not red_destino.endswith("/24"):
            raise ValueError("La red debe tener formato 'a.b.c.0/24'.")
        self.__tabla_ip[red_destino] = siguiente_salto

    def eliminar_ruta(self, red_destino: str) -> None:
        """Elimina una ruta si existe. O(1)."""
        self.__tabla_ip.pop(red_destino, None)

    def aprender_mac(self, mac: str, puerto: int) -> None:
        """Asocia una MAC a un puerto físico (como un switch). O(1)."""
        if puerto < 0:
            raise ValueError("El puerto debe ser no negativo.")
        self.__tabla_mac[mac.lower()] = puerto

    # ------------------------------------------------------------------
    # Búsquedas O(1)
    # ------------------------------------------------------------------
    def buscar_siguiente_salto(self, ip_destino: str) -> str | None:
        """Consulta Hash de la ruta: O(1) promedio."""
        return self.__tabla_ip.get(red_de(ip_destino))

    def buscar_puerto(self, mac: str) -> int | None:
        """Consulta Hash del puerto asociado a una MAC: O(1) promedio."""
        return self.__tabla_mac.get(mac.lower())

    def procesar(self, entrada: Paquete) -> str | None:
        """Decide qué hacer con un paquete (polimorfismo).

        Returns:
            Id del siguiente enrutador, "LOCAL" si el destino está en una
            red directamente conectada y su MAC es conocida, o None si el
            paquete se descarta (sin ruta, TTL agotado o MAC desconocida).
        """
        self._verificar_servicio()
        if not isinstance(entrada, Paquete):
            raise TypeError("El enrutador solo procesa objetos Paquete.")
        self.__paquetes_procesados += 1
        entrada.ttl -= 1
        if entrada.ttl <= 0:
            return None
        salto = self.buscar_siguiente_salto(entrada.ip_destino)
        if salto == ENTREGA_LOCAL and self.buscar_puerto(
                entrada.mac_destino) is None:
            return None
        return salto
