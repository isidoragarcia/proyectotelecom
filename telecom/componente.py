class ComponenteEnlace:
  def __init__(self, id_componente: str, estado_encendido: bool=True):
    self.id_componente = id_componente
    self.__estado_encendido = estado_encendido # atributo privado
