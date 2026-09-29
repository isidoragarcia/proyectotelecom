class ComponenteEnlace:
  def __init__(self, id_componente: str, estado_encendido: bool):
    self.id_componente = id_componente
    self.__estado_encendido = True # atributo privado


class Transmisor(ComponenteEnlace):
  def __init__(self, id_componente, potencia_transmision, ancho_banda, frecuencia_muestreo) -> None:
    # 1. Llamamos al constructor del padre para que configure el id_componente
    super().__init__(id_componente)
    self.potencia_transmision = potencia_transmision
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
  def conectar(self, router):
    self.router = router
    return router
  def transmitir(self, senal, ip_destino:int):
    if self.router is None:
      print("Error, no estás conectado.")
    self.router.procesar(senal, ip_destino)



class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.coeficiente_amortiguacion = coeficiente_amortiguacion
    self.temperatura = temperatura
    self
  def deteriorar(self, senal):
    senal.potencia *= (1-self.coeficiente_amortiguacion)#definir valor en base a coef amortiguacion, temperatura, ancho de banda

  def unir(self, a, b):
    self.extremo_a = a
    self.extremo_b = b

  def enviar(self, senal, ip_destino, desde):
    # si viene de A va hacia B, y al revés
    hacia = self.extremo_b if desde is self.extremo_a else self.extremo_a
    self.deteriorar(senal)
    return hacia.procesar(senal, ip_destino)

class Enrutador(ComponenteEnlace):
  def __init__(self, id_componente, tabla_rutas, vecinos) -> None:
    super().__init__(id_componente)
    self.tabla_rutas = tabla_rutas
    self.vecinos = vecinos
  def agregar_ruta(self, destino: str, camino: str) -> bool:
    """Guarda el camino si es nuevo. Devuelve true si cambió algo, false si no se añadió"""
    if self.id_componente in camino[1:]:          # evita bucles
      return False
    if destino not in self.tabla_rutas:
      self.tabla_rutas[destino] = camino
      return True
    return False
  
  def buscar_siguiente_salto(self, ip_destino: str) -> str:
    if ip_destino not in self.__tabla_ip:
      raise KeyError(f"{self.obtener_id()} no tiene ruta hacia {ip_destino}")
    return self.__tabla_ip[ip_destino]
  
  def procesar(self, senal, ip_destino):
    siguiente = self.buscar_siguiente_salto(ip_destino)
    print(f"{self.id_componente} recibió señal para {ip_destino}, la reenvía a {siguiente}")
    # aquí después la mandas al siguiente router o al receptor



class Receptor(ComponenteEnlace):
  def __init__(self, id_componente,ancho_banda, frecuencia_muestreo, umbral_deteccion) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
    self.umbral_deteccion = umbral_deteccion
  def asociar_router(self, id_router):
    self.id_router



class Señal:
  def __init__(self, duracion, potencia, frecuencia_muestreo, datos) -> None:
    self.duracion = duracion
    self.potencia = potencia
    self.frecuencia_muestreo = frecuencia_muestreo
    self.datos = datos

