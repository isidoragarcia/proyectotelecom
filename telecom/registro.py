class RegistroPaquetes:
  def __init__(self) -> None:
    self.__entradas = []   # lista ordenada por id (atributo privado)

  def registrar(self, id_paquete: int, ip_destino: str, recibida: bool, potencia: float) -> None:
    """Agrega un paquete al historial. Los ids deben llegar en orden creciente,
    así la lista queda ordenada sin tener que ordenarla (evita O(n log n))."""
    if self.__entradas and id_paquete <= self.__entradas[-1]["id"]:
      raise ValueError("Los ids deben ser crecientes")
    self.__entradas.append({"id": id_paquete, "ip_destino": ip_destino,
                            "recibida": recibida, "potencia": potencia})

  def buscar_secuencial(self, id_paquete: int):
    """Revisa uno por uno: O(n)."""
    for entrada in self.__entradas:
      if entrada["id"] == id_paquete:
        return entrada
    return None

  def buscar_binaria(self, id_paquete: int):
    """Versión iterativa: O(log n) en tiempo, O(1) en memoria."""
    bajo = 0
    alto = len(self.__entradas) - 1
    while bajo <= alto:
      medio = (bajo + alto) // 2
      id_medio = self.__entradas[medio]["id"]
      if id_medio == id_paquete:
        return self.__entradas[medio]
      elif id_medio < id_paquete:
        bajo = medio + 1      # está en la mitad derecha
      else:
        alto = medio - 1      # está en la mitad izquierda
    return None

  def buscar_binaria_recursiva(self, id_paquete: int, bajo: int = 0, alto: int = None):
    """Versión recursiva: T(n) = T(n/2) + c  =>  O(log n). Usa O(log n) de memoria en la pila."""
    if alto is None:
      alto = len(self.__entradas) - 1
    if bajo > alto:                 # caso base: no está
      return None
    medio = (bajo + alto) // 2
    id_medio = self.__entradas[medio]["id"]
    if id_medio == id_paquete:
      return self.__entradas[medio]
    if id_medio < id_paquete:
      return self.buscar_binaria_recursiva(id_paquete, medio + 1, alto)
    return self.buscar_binaria_recursiva(id_paquete, bajo, medio - 1)

  def buscar_errores(self) -> list:
    """Firmas de error: paquetes que no se recibieron."""
    return [e for e in self.__entradas if not e["recibida"]]
