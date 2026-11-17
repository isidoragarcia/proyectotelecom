"""Pruebas del enlace completo. Ejecutar desde la raíz del repo:

    python -m pytest
"""

import pytest

from telecom.cola import ColaFIFO
from telecom.registro import RegistroPaquetes
from telecom.simulacion import (IP_RECEPTOR, MAC_RECEPTOR, construir_enlace)


def paquete(**cambios) -> dict:
    base = {"id": 1, "ip_destino": IP_RECEPTOR, "mac": MAC_RECEPTOR,
            "ttl": 16, "carga": "dato"}
    base.update(cambios)
    return base


def enviar(p: dict, distancia_m: float = 1_000.0) -> dict:
    transmisor, _, _ = construir_enlace(distancia_m)
    return transmisor.transmitir(p, p["ip_destino"])


def test_paquete_correcto_se_recibe():
    resultado = enviar(paquete())
    assert resultado["recibida"] is True
    # 1 W atenuado 5 dB en total (0.005 dB/m * 1000 m)
    assert resultado["potencia"] == pytest.approx(10 ** (-0.5))
    assert resultado["snr_db"] > 0


def test_destino_sin_ruta():
    assert enviar(paquete(ip_destino="10.0.9.7"))["motivo"] == "sin_ruta"


def test_ttl_expira_antes_de_llegar():
    assert enviar(paquete(ttl=2))["motivo"] == "ttl_expirado"


def test_mac_incorrecta():
    assert enviar(paquete(mac="de:ad:be:ef:00:00"))["motivo"] == "mac_incorrecta"


def test_enlace_muy_largo_queda_bajo_el_umbral():
    assert enviar(paquete(), distancia_m=30_000.0)["motivo"] == "potencia_bajo_umbral"


def test_cola_respeta_orden_fifo_y_capacidad():
    cola = ColaFIFO(capacidad=2)
    assert cola.encolar("a") and cola.encolar("b")
    assert cola.encolar("c") is False      # llena
    assert cola.desencolar() == "a"
    assert cola.desencolar() == "b"
    with pytest.raises(IndexError):
        cola.desencolar()


def test_busquedas_entregan_lo_mismo():
    registro = RegistroPaquetes()
    for i in range(1, 201):
        registro.registrar(i, IP_RECEPTOR, True, 1.0)
    for objetivo in (1, 77, 200, 201):
        esperado = registro.buscar_secuencial(objetivo)
        assert registro.buscar_binaria(objetivo) == esperado
        assert registro.buscar_binaria_recursiva(objetivo) == esperado
