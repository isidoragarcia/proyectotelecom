class ComponenteEnlace:
  def __init__(self, id_componente: str, estado_encendido: bool):
    self.id_componente = id_componente
    self.__estado_encendido = True # atributo privado

  def accionar_breaker(self, estado_encendido: bool):
    self.estado_estado = not self.estado_estado
    print(f"[{self.id_componente}] Estado de conexión: {self.conectado}")


class Transmisor(ComponenteEnlace):
  def __init__(self, id_componente, potencia_transmision, ancho_banda, frecuencia_muestreo) -> None:
    # 1. Llamamos al constructor del padre para que configure el id_componente
    super().__init__(id_componente)
    self.potencia_transmision = potencia_transmision
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
    pass
    

class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.coeficiente_amortiguacion = coeficiente_amortiguacion
    self.temperatura = temperatura
    self
  def recibir_señal(self):

  def degradar_señal(self):

  def inyectar_ruido(self):

  def propagar(self):        
    pass


class Enrutador(ComponenteEnlace):
  def __init__(self, id_componente, tabla_rutas, vecinos) -> None:
    super().__init__(id_componente)
    self.tabla_rutas = tabla_rutas
    self.vecinos = vecinos
    pass


class Receptor(ComponenteEnlace):
  def __init__(self, id_componente,ancho_banda, frecuencia_muestreo, umbral_deteccion) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
    self.umbral_deteccion = umbral_deteccion
    pass


class Señal:
  def __init__(self, duracion, potencia, frecuencia_muestreo, datos) -> None:
    self.duracion = duracion
    self.potencia = potencia
    self.frecuencia_muestreo = frecuencia_muestreo
    self.datos = datos
    pass
