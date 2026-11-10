from telecom.componente import ComponenteEnlace
from telecom.senal import Señal


class Transmisor(ComponenteEnlace):
  def __init__(self, id_componente, potencia_transmision, ancho_banda, frecuencia_muestreo) -> None:
    # 1. Llamamos al constructor del padre para que configure el id_componente
    super().__init__(id_componente)
    self.__potencia_transmision = potencia_transmision
    self.__ancho_banda = ancho_banda
    self.__frecuencia_muestreo = frecuencia_muestreo
    self.canal = None

  @property
  def potencia_transmision(self):
    return self.__potencia_transmision

  @property
  def ancho_banda(self):
    return self.__ancho_banda

  @property
  def frecuencia_muestreo(self):
    return self.__frecuencia_muestreo

  def conectar(self, canal, router):
    canal.unir(self, router)
    self.canal = canal
  def transmitir(self, datos, ip_destino):
    if self.canal is None:
      print("Error, no estás conectado.")
      return
    senal = Señal(duracion=1, potencia=self.__potencia_transmision,
                  frecuencia_muestreo=self.__frecuencia_muestreo, datos=datos)
    return self.canal.enviar(senal, ip_destino, self)
