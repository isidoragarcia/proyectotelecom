"""Orquestacion de la simulacion del enlace de telecomunicaciones.

Construye la cadena TX -> R1 -> R2 -> R3 -> RX, genera trafico, lo
transmite y audita el registro con busqueda binaria. Se invoca desde
main.py mediante ejecutar().
"""

from __future__ import annotations

import argparse

import numpy as np

from telecom.canal import Canal
from telecom.enrutador import Enrutador
from telecom.receptor import Receptor
from telecom.registro import RegistroPaquetes
from telecom.transmisor import Transmisor

# Parametros del escenario base (ajustables)
ANCHO_BANDA_HZ = 8_000.0
FRECUENCIA_MUESTREO_HZ = 20_000.0
POTENCIA_TX_W = 1.0
COEF_AMORTIGUACION = 0.005   # dB/m
TEMPERATURA_K = 290.0
UMBRAL_DETECCION_W = 1e-12
DISTANCIA_M = 1_000.0

IP_RECEPTOR = "10.0.3.20"
IP_TRANSMISOR = "10.0.1.10"
MAC_RECEPTOR = "aa:bb:cc:00:03:14"


def construir_enlace(distancia_m: float = DISTANCIA_M):
    """Construye la cadena fisica y la red de tres enrutadores en serie.

    Topologia:  [TX] -- R1 -- R2 -- R3 -- [RX]
    """
    transmisor = Transmisor("TX-01", POTENCIA_TX_W, ANCHO_BANDA_HZ,
                            FRECUENCIA_MUESTREO_HZ)
    receptor = Receptor("RX-01", ANCHO_BANDA_HZ, FRECUENCIA_MUESTREO_HZ,
                        UMBRAL_DETECCION_W)

    r1 = Enrutador("R1", "10.0.1.1")
    r2 = Enrutador("R2", "10.0.2.1")
    r3 = Enrutador("R3", "10.0.3.1")

    # Tabla de rutas (Hash) por prefijo de red
    r1.agregar_ruta("10.0.1.0/24", "R1")
    r1.agregar_ruta("10.0.2.0/24", "R2")
    r1.agregar_ruta("10.0.3.0/24", "R2")
    r2.agregar_ruta("10.0.1.0/24", "R1")
    r2.agregar_ruta("10.0.2.0/24", "R2")
    r2.agregar_ruta("10.0.3.0/24", "R3")
    r3.agregar_ruta("10.0.1.0/24", "R2")
    r3.agregar_ruta("10.0.2.0/24", "R2")
    r3.agregar_ruta("10.0.3.0/24", "R3")

    # Canales fisicos entre cada par (con distancia del tramo)
    tramo = distancia_m / 3.0
    canal_tx_r1 = Canal("C-TX-R1", ANCHO_BANDA_HZ, COEF_AMORTIGUACION,
                        TEMPERATURA_K, tramo)
    canal_r1_r2 = Canal("C-R1-R2", ANCHO_BANDA_HZ, COEF_AMORTIGUACION,
                        TEMPERATURA_K, tramo)
    canal_r2_r3 = Canal("C-R2-R3", ANCHO_BANDA_HZ, COEF_AMORTIGUACION,
                        TEMPERATURA_K, tramo)
    canal_r3_rx = Canal("C-R3-RX", ANCHO_BANDA_HZ, COEF_AMORTIGUACION,
                        TEMPERATURA_K, tramo)

    # Conectar TX -> R1 y R3 -> RX (los enrutadores entre si)
    transmisor.conectar(canal_tx_r1, r1)
    r1.conectar(r2, canal_r1_r2)
    r2.conectar(r3, canal_r2_r3)
    canal_r3_rx.unir(r3, receptor)

    return transmisor, receptor, [r1, r2, r3]


def generar_trafico(cantidad: int, semilla: int):
    """Genera paquetes con ids crecientes y algunos defectuosos."""
    rng = np.random.default_rng(semilla)
    tipos = rng.choice(["ok", "sin_ruta", "ttl", "mac"], size=cantidad,
                       p=[0.85, 0.05, 0.05, 0.05])
    paquetes = []
    for i, tipo in enumerate(tipos, start=1):
        ip_destino = "10.0.9.7" if tipo == "sin_ruta" else IP_RECEPTOR
        mac = "de:ad:be:ef:00:00" if tipo == "mac" else MAC_RECEPTOR
        ttl = 2 if tipo == "ttl" else 16
        paquetes.append({
            "id": i, "ip_origen": IP_TRANSMISOR,
            "ip_destino": ip_destino, "mac": mac,
            "ttl": ttl, "carga": f"dato-{i}",
        })
    return paquetes


def ejecutar() -> None:
    """Ejecuta la simulacion completa y muestra el reporte por consola."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distancia", type=float, default=DISTANCIA_M,
                        help="Largo total del enlace [m] (defecto: 1000)")
    parser.add_argument("--paquetes", type=int, default=500,
                        help="Cantidad de paquetes a enviar (defecto: 500)")
    parser.add_argument("--semilla", type=int, default=42,
                        help="Semilla aleatoria para reproducibilidad")
    args = parser.parse_args()

    transmisor, receptor, enrutadores = construir_enlace(args.distancia)

    print("=" * 62)
    print(" SIMULACION DE ENLACE DE TELECOMUNICACIONES (EL4203 - Op. C)")
    print("=" * 62)
    print(f"Distancia total      : {args.distancia:,.0f} m")
    print(f"Paquetes a enviar    : {args.paquetes}")
    print(f"Enrutadores          : {[e.id_componente for e in enrutadores]}")
    print(f"Receptor             : {receptor.id_componente}")
    print("-" * 62)

    # Registrar paquetes en el historial (ids crecientes -> ordenado)
    registro = RegistroPaquetes()
    paquetes = generar_trafico(args.paquetes, args.semilla)
    for p in paquetes:
        registro.registrar(p["id"], p["ip_destino"], True, 1.0)

    # Auditoria: busqueda binaria recursiva sobre ids concretos
    objetivos = (1, len(paquetes) // 2, args.paquetes, args.paquetes + 99)
    print("Auditoria con busqueda binaria recursiva:")
    for objetivo in objetivos:
        entrada = registro.buscar_binaria_recursiva(objetivo)
        if entrada is None:
            print(f"  Paquete #{objetivo}: no existe en el registro")
        else:
            print(f"  Paquete #{objetivo}: id={entrada['id']} "
                  f"ip_destino={entrada['ip_destino']}")

    print("-" * 62)
    print("Simulacion finalizada correctamente.")


if __name__ == "__main__":
    ejecutar()