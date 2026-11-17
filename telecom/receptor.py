import math

from telecom.componente import ComponenteEnlace


class Receptor(ComponenteEnlace):
  def __init__(self, id_componente, ancho_banda, frecuencia_muestreo, umbral_deteccion, direccion_mac=None) -> None:
    super().__init__(id_componente)
    self.__ancho_banda = ancho_banda
    self.__frecuencia_muestreo = frecuencia_muestreo
    self.__direccion_mac = direccion_mac   # None = no se revisa la MAC
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
    """Decide si la señal se recibe. Devuelve también el motivo del rechazo,
    la potencia recibida [W] y la relación señal a ruido [dB]."""
    motivo = None
    mac = senal.datos.get("mac") if isinstance(senal.datos, dict) else None
    if senal.potencia < self.umbral_deteccion:
      motivo = "potencia_bajo_umbral"
    elif senal.frecuencia_muestreo != self.__frecuencia_muestreo:
      motivo = "frecuencia_muestreo_distinta"
    elif self.__direccion_mac is not None and mac is not None and mac != self.__direccion_mac:
      motivo = "mac_incorrecta"

    if senal.ruido > 0 and senal.potencia > 0:
      snr_db = 10 * math.log10(senal.potencia / senal.ruido)
    else:
      snr_db = None
    return {"recibida": motivo is None, "motivo": motivo,
            "potencia": senal.potencia, "snr_db": snr_db}
