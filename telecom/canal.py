from telecom.componente import ComponenteEnlace


class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura, distancia=1.0) -> None:
    super().__init__(id_componente)
    self.__ancho_banda = ancho_banda
    self.coeficiente_amortiguacion = coeficiente_amortiguacion
    self.temperatura = temperatura
    self.__distancia = distancia

  @property
  def ancho_banda(self):
    return self.__ancho_banda

  def __aplicar_atenuacion(self, senal):
    perdida_db = self.__coeficiente_amortiguacion * self.__distancia
    senal.potencia *= 10 ** (-perdida_db / 10)

  def __aplicar_ruido_termico(self, senal):
    senal.ruido = 1e-23 * self.__temperatura * self.__ancho_banda
  def unir(self, a, b):
    self.extremo_a = a
    self.extremo_b = b

  def enviar(self, senal, ip_destino, desde):
    # si viene de A va hacia B, y al revés
    hacia = self.extremo_b if desde is self.extremo_a else self.extremo_a
    self.__aplicar_atenuacion(senal)
    self.__aplicar_ruido_termico(senal)
    return hacia.procesar(senal, ip_destino)


