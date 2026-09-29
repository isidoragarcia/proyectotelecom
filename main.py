class ComponenteEnlace:
  def __init__(self, id_componente: str, estado_encendido: bool):
    self.id_componente = id_componente
    self.__estado_encendido = True # atributo privado

  def accionar_breaker(self, estado_encendido: bool):
    self.estado_estado = not self.estado_estado


class Transmisor(ComponenteEnlace):
  def __init__(self, id_componente, potencia_transmision, ancho_banda, frecuencia_muestreo) -> None:
    # 1. Llamamos al constructor del padre para que configure el id_componente
    super().__init__(id_componente)
    self.potencia_transmision = potencia_transmision
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
  def enlazar(self, router):
    
  def transmitir(self, senal, ip_destino:int):
    self.ip_destino=ip_destino



class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.coeficiente_amortiguacion = coeficiente_amortiguacion
    self.temperatura = temperatura
    self
  def deteriorar(senal):
    senal.potencia -= #definir valor en base a coef amortiguacion, temperatura, ancho de banda


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
  
  def procesar(paquete):
    pass 


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

