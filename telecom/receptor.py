from telecom.componente import ComponenteEnlace


class Receptor(ComponenteEnlace):
  def __init__(self, id_componente,ancho_banda, frecuencia_muestreo, umbral_deteccion) -> None:
    super().__init__(id_componente)
    self.__ancho_banda = ancho_banda
    self.__frecuencia_muestreo = frecuencia_muestreo
    self.umbral_deteccion = umbral_deteccion
    self.canales = {}

  @property
  def ancho_banda(self):
    return self.__ancho_banda

  @property
  def frecuencia_muestreo(self):
    return self.__frecuencia_muestreo

  def procesar(self, senal, ip_destino):
    resultado = self.evaluar(senal)
    return resultado
  
  def evaluar(self, senal):
    recibida = True
    if senal.potencia < self.umbral_deteccion:
      recibida = False
    elif senal.frecuencia_muestreo != self.__frecuencia_muestreo:
      recibida = False
    return {"recibida": recibida}    
