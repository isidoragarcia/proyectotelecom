class Señal:
  def __init__(self, duracion, potencia, frecuencia_muestreo, datos, ruido=0.0) -> None:
    self.duracion = duracion
    self.potencia = potencia                        # [W]
    self.frecuencia_muestreo = frecuencia_muestreo  # [Hz]
    self.datos = datos
    self.ruido = ruido                              # potencia de ruido acumulada [W]
