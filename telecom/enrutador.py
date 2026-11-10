from telecom.componente import ComponenteEnlace


class Enrutador(ComponenteEnlace):
  def __init__(self, id_componente, tabla_rutas, vecinos) -> None:
    super().__init__(id_componente)
    self.tabla_rutas = {id_componente: [id_componente]}
    self.canales = {}
  def agregar_ruta(self, destino: str, camino: str) -> bool:
    """Guarda el camino si es nuevo. Devuelve true si cambió algo, false si no se añadió"""
    if self.id_componente in camino[1:]:          # evita bucles
      return False
    if destino not in self.tabla_rutas:
      self.tabla_rutas[destino] = camino
      return True
    return False
  
  def conectar(self, otro, canal):
    canal.unir(self, otro)
    self.canales[otro.id_componente] = canal
    otro.canales[self.id_componente] = canal   # si "otro" es otro Enrutador o un Receptor con este atributo
    self.agregar_ruta(otro.id_componente, [self.id_componente, otro.id_componente])

  def buscar_siguiente_salto(self, ip_destino: str) -> str:
    if ip_destino not in self.__tabla_ip:
      raise KeyError(f"{self.obtener_id()} no tiene ruta hacia {ip_destino}")
    return self.__tabla_ip[ip_destino]
  
  def procesar(self, senal, ip_destino):
    if ip_destino == self.id_componente:
      print(f"{self.id_componente}: la señal llegó, potencia {senal.potencia}")
      return senal
    siguiente = self.tabla_rutas[ip_destino][1]      # 2º punto del camino
    return self.canales[siguiente].enviar(senal, ip_destino, self)
