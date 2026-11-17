from telecom.componente import ComponenteEnlace


class Enrutador(ComponenteEnlace):
    """Enrutador de la red de telecomunicaciones.

    Mantiene una tabla hash privada de rutas (destino -> siguiente salto)
    y un diccionario privado de canales hacia vecinos. El acceso a ambos
    se realiza exclusivamente mediante metodos publicos, garantizando el
    encapsulamiento del estado interno.
    """

    def __init__(self, id_componente, tabla_rutas=None, vecinos=None) -> None:
        super().__init__(id_componente)
        # Tabla Hash principal para ruteo: destino -> siguiente salto
        self.__tabla_ip = {id_componente: id_componente}
        # Diccionario privado: vecino_id -> objeto Canal
        self.__canales = {}
        # Tabla hash privada: IP de un host conectado directo -> objeto Canal
        self.__hosts = {}

    # ------------------------------------------------------------------
    # Acceso controlado al estado privado (encapsulamiento)
    # ------------------------------------------------------------------
    def obtener_canal(self, vecino_id: str):
        """Devuelve el canal hacia un vecino, o None si no esta conectado."""
        return self.__canales.get(vecino_id)

    def registrar_canal(self, vecino_id: str, canal) -> None:
        """Registra un canal hacia un vecino (uso interno entre enrutadores)."""
        self.__canales[vecino_id] = canal

    # ------------------------------------------------------------------
    # Tabla de rutas (Hash)
    # ------------------------------------------------------------------
    def agregar_ruta(self, destino: str, camino) -> bool:
        """Registra el siguiente salto hacia `destino`.

        `camino` puede ser:
          - una lista [origen, siguiente_salto, ...] (uso interno de conectar)
          - un string con el ID del siguiente salto (uso desde main)
        Devuelve True si la ruta es nueva.
        """
        if isinstance(camino, str):
            siguiente = camino
            saltos = [self.id_componente, camino]
        else:
            saltos = list(camino)
            siguiente = saltos[1] if len(saltos) > 1 else saltos[0]
        # Si el siguiente salto es este mismo enrutador, la red es local
        # (entrega directa al host) y no es un bucle
        es_entrega_local = siguiente == self.id_componente and len(saltos) == 2
        if not es_entrega_local and self.id_componente in saltos[1:]:  # evita bucles
            return False
        if destino not in self.__tabla_ip:
            self.__tabla_ip[destino] = siguiente  # SIGUIENTE SALTO directo
            return True
        return False

    @staticmethod
    def __prefijo_red(ip: str):
        """Prefijo /24 de una IP: '10.0.3.20' -> '10.0.3.0/24'."""
        octetos = ip.split(".")
        if len(octetos) != 4:
            return None
        return ".".join(octetos[:3]) + ".0/24"

    def buscar_siguiente_salto(self, ip_destino: str) -> str:
        """Busqueda O(1) en la Tabla Hash.

        Primero busca el destino exacto y despues su prefijo de red /24.
        Son a lo mas dos consultas a la tabla, cada una O(1) en promedio.
        """
        if ip_destino in self.__tabla_ip:
            return self.__tabla_ip[ip_destino]
        prefijo = self.__prefijo_red(ip_destino)
        if prefijo in self.__tabla_ip:
            return self.__tabla_ip[prefijo]
        raise KeyError(f"{self.id_componente} no tiene ruta hacia {ip_destino}")

    # ------------------------------------------------------------------
    # Topologia y procesamiento
    # ------------------------------------------------------------------
    def conectar(self, otro, canal):
        """Conecta este enrutador con `otro` a traves de `canal`."""
        canal.unir(self, otro)
        self.__canales[otro.id_componente] = canal
        if hasattr(otro, 'registrar_canal'):
            otro.registrar_canal(self.id_componente, canal)
        self.agregar_ruta(otro.id_componente,
                          [self.id_componente, otro.id_componente])

    def conectar_host(self, host, canal, ip_host: str) -> None:
        """Conecta un equipo final (por ejemplo el receptor) a este enrutador."""
        canal.unir(self, host)
        self.__hosts[ip_host] = canal

    @staticmethod
    def __descartar(senal, motivo: str) -> dict:
        """Resultado de un paquete que no llego al receptor."""
        return {"recibida": False, "motivo": motivo,
                "potencia": senal.potencia, "snr_db": None}

    def procesar(self, senal, ip_destino):
        """Procesa una senal: la entrega si es local o la reenvia."""
        if ip_destino == self.id_componente:
            print(f"{self.id_componente}: la senal llego, potencia {senal.potencia}")
            return senal

        # Cada enrutador descuenta un salto; con TTL 0 el paquete se descarta
        datos = senal.datos
        if isinstance(datos, dict) and "ttl" in datos:
            datos["ttl"] -= 1
            if datos["ttl"] <= 0:
                return self.__descartar(senal, "ttl_expirado")

        # Usamos la busqueda O(1) de la tabla hash
        try:
            siguiente_salto = self.buscar_siguiente_salto(ip_destino)
        except KeyError:
            return self.__descartar(senal, "sin_ruta")

        if siguiente_salto == self.id_componente:
            # La red de destino es la de este enrutador: entrega al host
            canal = self.__hosts.get(ip_destino)
            if canal is None:
                return self.__descartar(senal, "host_inalcanzable")
        else:
            canal = self.obtener_canal(siguiente_salto)
            if canal is None:
                return self.__descartar(senal, "sin_canal")
        return canal.enviar(senal, ip_destino, self)