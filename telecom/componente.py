class ComponenteEnlace:
  def __init__(self, id_componente: str, estado_encendido: bool):
    self.id_componente = id_componente
    self.__estado_encendido = True # atributo privado
