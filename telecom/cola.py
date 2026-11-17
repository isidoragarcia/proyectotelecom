from collections import deque


class ColaFIFO:
  """TDA Cola (FIFO): el primer elemento que entra es el primero que sale.

  Se implementa sobre collections.deque, que encola y desencola en O(1).
  Con una lista de Python, sacar el primer elemento (pop(0)) cuesta O(n)
  porque hay que correr todos los demás.
  """

  def __init__(self, capacidad: int = None) -> None:
    self.__elementos = deque()
    self.__capacidad = capacidad   # None = sin límite

  def encolar(self, elemento) -> bool:
    """Agrega al final: O(1). Devuelve False si la cola está llena."""
    if self.esta_llena():
      return False
    self.__elementos.append(elemento)
    return True

  def desencolar(self):
    """Saca el elemento más antiguo: O(1)."""
    if self.esta_vacia():
      raise IndexError("La cola está vacía")
    return self.__elementos.popleft()

  def esta_vacia(self) -> bool:
    return len(self.__elementos) == 0

  def esta_llena(self) -> bool:
    return self.__capacidad is not None and len(self.__elementos) >= self.__capacidad

  def __len__(self) -> int:
    return len(self.__elementos)
