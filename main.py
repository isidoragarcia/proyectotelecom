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
  def conectar(self, canal, router):
    canal.unir(self, router)
    self.canal = canal
  def transmitir(self, senal, ip_destino:int):
    if self.canal is None:
      print("Error, no estás conectado.")
      return
    self.canal.enviar(senal, ip_destino, self)



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



class Receptor(ComponenteEnlace):
  def __init__(self, id_componente,ancho_banda, frecuencia_muestreo, umbral_deteccion) -> None:
    super().__init__(id_componente)
    self.ancho_banda = ancho_banda
    self.frecuencia_muestreo = frecuencia_muestreo
    self.umbral_deteccion = umbral_deteccion
    self.canales = {}
    
  def procesar(self, senal, ip_destino):
    resultado = self.evaluar(senal)
    return resultado
  
  def evaluar(self, senal):
    recibida = True
    if senal.potencia < self.umbral_deteccion:
      recibida = False
    elif senal.frecuencia_muestreo != self.frecuencia_muestreo:
      recibida = False
    return {"recibida": recibida}    




class Señal:
  def __init__(self, duracion, potencia, frecuencia_muestreo, datos) -> None:
    self.duracion = duracion
    self.potencia = potencia
    self.frecuencia_muestreo = frecuencia_muestreo
    self.datos = datos