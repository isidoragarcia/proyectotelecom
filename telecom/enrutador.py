from telecom.componente import ComponenteEnlace


class Enrutador(ComponenteEnlace):
    """Enrutador de la red de telecomunicaciones.

    Mantiene una tabla hash privada de rutas (destino -> siguiente salto)
    y un diccionario privado de canales hacia vecinos. El acceso a ambos
    se realiza exclusivamente mediante métodos publicos, garantizando el
    encapsulamiento del estado interno.
    """

    def __init__(self, id_componente, tabla_rutas=None, vecinos=None) -> None:
        super().__init__(id_componente)
        # Tabla Hash principal para ruteo: destino -> siguiente salto
        self.__tabla_ip = {id_componente: id_componente}
        # Diccionario privado: vecino_id -> objeto Canal
        self.__canales = {}

    
    # Acceso controlado al estado privado (encapsulamiento)
    
    def obtener_canal(self, vecino_id: str):
        """Devuelve el canal hacia un vecino, o None si no esta conectado."""
        return self.__canales.get(vecino_id)

    def registrar_canal(self, vecino_id: str, canal) -> None:
        """Registra un canal hacia un vecino (uso interno entre enrutadores)."""
        self.__canales[vecino_id] = canal

    
    # Tabla de rutas (Hash)
    
    def agregar_ruta(self, destino: str, camino) -> bool:
        """Registra el siguiente salto hacia `destino`.

        `camino` puede ser:
          - Una lista [origen, siguiente_salto, ...] (uso interno de conectar)
          - Un string con el ID del siguiente salto (uso desde main)
        Devuelve True si la ruta es nueva.
        """
        if isinstance(camino, str):
            siguiente = camino
            saltos = [self.id_componente, camino]
        else:
            saltos = list(camino)
            siguiente = saltos[1] if len(saltos) > 1 else saltos[0]
        if self.id_componente in saltos[1:]:  # evita bucles
            return False
        if destino not in self.__tabla_ip:
            self.__tabla_ip[destino] = siguiente  # SIGUIENTE SALTO directo
            return True
        return False

    def buscar_siguiente_salto(self, ip_destino: str) -> str:
        """Busqueda O(1) en la Tabla Hash."""
        if ip_destino not in self.__tabla_ip:
            raise KeyError(f"{self.id_componente} no tiene ruta hacia {ip_destino}")
        return self.__tabla_ip[ip_destino]

    
    # Topologia y procesamiento
    
    def conectar(self, otro, canal):
        """Conecta este enrutador con `otro` a traves de `canal`."""
        canal.unir(self, otro)
        self.__canales[otro.id_componente] = canal
        if hasattr(otro, 'registrar_canal'):
            otro.registrar_canal(self.id_componente, canal)
        self.agregar_ruta(otro.id_componente,
                          [self.id_componente, otro.id_componente])

    def procesar(self, senal, ip_destino):
        """Procesa una senal: la entrega si es local o la reenvía."""
        if ip_destino == self.id_componente:
            print(f"{self.id_componente}: la senal llego, potencia {senal.potencia}")
            return senal

        # Usamos la búsqueda O(1) de la tabla hash
        siguiente_salto = self.buscar_siguiente_salto(ip_destino)
        canal = self.obtener_canal(siguiente_salto)
        if canal is None:
            raise KeyError(
                f"{self.id_componente} no tiene canal hacia {siguiente_salto}")
        return canal.enviar(senal, ip_destino, self)