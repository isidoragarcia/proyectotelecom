class Enrutador(ComponenteEnlace):
  def __init__(self, id_componente, tabla_rutas=None, vecinos=None) -> None:
    super().__init__(id_componente)
    # Tabla Hash principal para ruteo IP -> Puerto/ID de salida
    self.__tabla_ip = {id_componente: id_componente} 
    # Diccionario para guardar los objetos Canal conectados
    self.canales = {}

  def agregar_ruta(self, destino: str, camino: list) -> bool:
    """Guarda el camino si es nuevo. Devuelve true si cambió algo"""
    if self.id_componente in camino[1:]:  # evita bucles
      return False
    if destino not in self.__tabla_ip:
      self.__tabla_ip[destino] = camino[1] # Guardamos el SIGUIENTE SALTO directo
      return True
    return False
  
  def conectar(self, otro, canal):
    canal.unir(self, otro)
    self.canales[otro.id_componente] = canal
    if hasattr(otro, 'canales'):
        otro.canales[self.id_componente] = canal
    self.agregar_ruta(otro.id_componente, [self.id_componente, otro.id_componente])

  def buscar_siguiente_salto(self, ip_destino: str) -> str:
    """Búsqueda O(1) en la Tabla Hash"""
    if ip_destino not in self.__tabla_ip:
      raise KeyError(f"{self.id_componente} no tiene ruta hacia {ip_destino}")
    return self.__tabla_ip[ip_destino]
  
  def procesar(self, senal, ip_destino):
    if ip_destino == self.id_componente:
      print(f"{self.id_componente}: la señal llegó, potencia {senal.potencia}")
      return senal
    
    # Usamos la búsqueda O(1) de la tabla hash
    siguiente_salto = self.buscar_siguiente_salto(ip_destino)
    return self.canales[siguiente_salto].enviar(senal, ip_destino, self)