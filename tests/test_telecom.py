"""Pruebas unitarias del simulador (ejecutar con: python -m pytest)."""

import numpy as np
import pytest

from telecom import (CanalFisico, EnlaceTelecom, Enrutador, Paquete,
                     Receptor, RegistroPaquetes, Transmisor)
from telecom.datos import w_a_dbm
from telecom.enrutador import ENTREGA_LOCAL, red_de
from telecom.registro import ESTADO_ENTREGADO, EntradaRegistro

FS = 20_000.0
B = 8_000.0
TONOS = [1_000.0, 2_500.0, 4_000.0]


def crear_transmisor() -> Transmisor:
    return Transmisor("TX", 1.0, FS, B, TONOS)


# ----------------------------------------------------------------------
# Encapsulamiento
# ----------------------------------------------------------------------
def test_atributos_privados_no_accesibles():
    tx = crear_transmisor()
    with pytest.raises(AttributeError):
        _ = tx.__potencia_tx_w  # noqa: SLF001


def test_setter_rechaza_valores_fisicamente_imposibles():
    tx = crear_transmisor()
    with pytest.raises(ValueError):
        tx.ajustar_potencia_tx(-5.0)
    assert tx.obtener_potencia_tx() == 1.0


def test_nyquist_validado():
    with pytest.raises(ValueError):
        Transmisor("TX", 1.0, 10_000.0, 8_000.0, TONOS)


def test_obtener_tonos_devuelve_copia():
    tx = crear_transmisor()
    tonos = tx.obtener_tonos()
    tonos[0] = 999.0
    assert tx.obtener_tonos()[0] == 1_000.0


# ----------------------------------------------------------------------
# Capa física
# ----------------------------------------------------------------------
def test_potencia_transmitida_correcta():
    senal = crear_transmisor().generar_senal()
    assert senal.potencia_media_w() == pytest.approx(1.0, rel=1e-6)


def test_friis_espacio_libre():
    canal = CanalFisico("C", 1_000.0, 2.4e9, B, exponente_perdida=2.0)
    # FSPL(1 km, 2.4 GHz) = 100.05 dB
    assert canal.calcular_perdida_db() == pytest.approx(100.05, abs=0.01)


def test_canal_atenua_segun_modelo():
    canal = CanalFisico("C", 100.0, 2.4e9, B, temperatura_k=1e-9, semilla=0)
    senal_rx = canal.procesar(crear_transmisor().generar_senal())
    perdida_medida = -10 * np.log10(senal_rx.potencia_media_w())
    assert perdida_medida == pytest.approx(canal.calcular_perdida_db(),
                                           abs=0.01)


def test_fft_detecta_tonos_y_snr_coincide_con_teoria():
    canal = CanalFisico("C", 500.0, 2.4e9, B, 3.5, figura_ruido_db=6.0,
                        semilla=1)
    rx = Receptor("RX", FS)
    resultado = rx.procesar(canal.procesar(crear_transmisor().generar_senal()))
    np.testing.assert_allclose(resultado.tonos_detectados_hz, TONOS)
    snr_teorica = (w_a_dbm(1.0) - canal.calcular_perdida_db()
                   - w_a_dbm(canal.calcular_potencia_ruido_w()))
    assert resultado.snr_db == pytest.approx(snr_teorica, abs=0.5)


def test_barrido_devuelve_matriz_d_por_n():
    canal = CanalFisico("C", 100.0, 2.4e9, B, semilla=2)
    senal = crear_transmisor().generar_senal()
    matriz = canal.procesar_barrido(senal, np.array([10.0, 100.0, 1e3]))
    assert matriz.shape == (3, senal.numero_muestras())


# ----------------------------------------------------------------------
# Enrutamiento y registro
# ----------------------------------------------------------------------
def test_red_de():
    assert red_de("10.0.3.25") == "10.0.3.0/24"
    with pytest.raises(ValueError):
        red_de("10.0.300.1")


def test_enrutador_hash_y_ttl():
    r = Enrutador("R", "10.0.1.1")
    r.agregar_ruta("10.0.3.0/24", "R2")
    assert r.procesar(Paquete(1, "a", "10.0.3.7", "m")) == "R2"
    assert r.procesar(Paquete(2, "a", "10.9.9.9", "m")) is None
    assert r.procesar(Paquete(3, "a", "10.0.3.7", "m", ttl=1)) is None


def test_busqueda_binaria_recursiva_e_iterativa():
    registro = RegistroPaquetes()
    for i in range(2, 2_000, 3):
        registro.registrar(EntradaRegistro(i, "x", ESTADO_ENTREGADO, 1, ()))
    for objetivo in (2, 3, 998, 1_997, 5_000):
        esperado = registro.buscar_secuencial(objetivo)
        assert registro.buscar_binaria_recursiva(objetivo) == esperado
        assert registro.buscar_binaria_iterativa(objetivo) == esperado


def test_registro_exige_orden():
    registro = RegistroPaquetes()
    registro.registrar(EntradaRegistro(5, "x", ESTADO_ENTREGADO, 1, ()))
    with pytest.raises(ValueError):
        registro.registrar(EntradaRegistro(3, "x", ESTADO_ENTREGADO, 1, ()))


def test_enlace_extremo_a_extremo():
    canal = CanalFisico("C", 200.0, 2.4e9, B, semilla=3)
    enlace = EnlaceTelecom(crear_transmisor(), canal, Receptor("RX", FS))
    r1 = Enrutador("R1", "10.0.1.1")
    r2 = Enrutador("R2", "10.0.3.1")
    r1.agregar_ruta("10.0.3.0/24", "R2")
    r2.agregar_ruta("10.0.3.0/24", ENTREGA_LOCAL)
    r2.aprender_mac("AA:BB:CC:00:00:01", 1)
    enlace.agregar_enrutador(r1)
    enlace.agregar_enrutador(r2)
    entrada = enlace.enviar_paquete(
        Paquete(1, "10.0.1.5", "10.0.3.9", "aa:bb:cc:00:00:01"), "R1")
    assert entrada.estado == ESTADO_ENTREGADO
    assert entrada.ruta == ("R1", "R2")
