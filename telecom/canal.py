from telecom.componente import ComponenteEnlace

CONSTANTE_BOLTZMANN = 1.380649e-23   # [J/K]


class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura, distancia=1.0) -> None:
    super().__init__(id_componente)
    self.__ancho_banda = ancho_banda                              # [Hz]
    self.__coeficiente_amortiguacion = coeficiente_amortiguacion  # [dB/m]
    self.__temperatura = temperatura                              # [K]
    self.__distancia = distancia                                  # [m]
    self.extremo_a = None
    self.extremo_b = None

  @property
  def ancho_banda(self):
    return self.__ancho_banda

  def __aplicar_atenuacion(self, senal):
    perdida_db = self.__coeficiente_amortiguacion * self.__distancia
    ganancia = 10 ** (-perdida_db / 10)
    senal.potencia *= ganancia
    senal.ruido *= ganancia   # el ruido que ya traía la señal se atenúa igual

  def __aplicar_ruido_termico(self, senal):
    # N = k * T * B, se suma al ruido acumulado en los tramos anteriores
    senal.ruido += CONSTANTE_BOLTZMANN * self.__temperatura * self.__ancho_banda

  def unir(self, a, b):
    self.extremo_a = a
    self.extremo_b = b

  def enviar(self, senal, ip_destino, desde):
    if self.extremo_a is None or self.extremo_b is None:
      raise RuntimeError(f"El canal {self.id_componente} no está unido a dos componentes")
    # si viene de A va hacia B, y al revés
    hacia = self.extremo_b if desde is self.extremo_a else self.extremo_a
    self.__aplicar_atenuacion(senal)
    self.__aplicar_ruido_termico(senal)
    return hacia.procesar(senal, ip_destino)
