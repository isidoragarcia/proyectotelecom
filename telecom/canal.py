from telecom.componente import ComponenteEnlace


class Canal(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, coeficiente_amortiguacion, temperatura) -> None:
    super().__init__(id_componente)
    self.__ancho_banda = ancho_banda
    self.coeficiente_amortiguacion = coeficiente_amortiguacion
    self.temperatura = temperatura

  @property
  def ancho_banda(self):
    return self.__ancho_banda

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
