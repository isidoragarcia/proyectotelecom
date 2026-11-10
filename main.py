"""Punto de entrada del simulador de enlace de telecomunicaciones.

Uso:
    python main.py
    python main.py --distancia 3000 --paquetes 1000 --semilla 7
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from telecom import (CanalFisico, EnlaceTelecom, Enrutador, Paquete,
                     Receptor, Transmisor)
from telecom.datos import w_a_dbm
from telecom.enrutador import ENTREGA_LOCAL
from telecom.graficos import graficar_espectro, graficar_snr_vs_distancia

# Parámetros del escenario base
FRECUENCIA_MUESTREO_HZ = 20_000.0
ANCHO_BANDA_HZ = 8_000.0
TONOS_PILOTO_HZ = [1_000.0, 2_500.0, 4_000.0, 6_000.0]
POTENCIA_TX_W = 1.0
FRECUENCIA_PORTADORA_HZ = 2.4e9
EXPONENTE_PERDIDA = 3.5
FIGURA_RUIDO_DB = 6.0

IP_RECEPTOR = "10.0.3.20"
MAC_RECEPTOR = "aa:bb:cc:00:03:14"
IP_TRANSMISOR = "10.0.1.10"


def construir_enlace(distancia_m: float, semilla: int) -> EnlaceTelecom:
    """Crea la cadena física y una red de tres enrutadores en serie.

    Topología:  [TX] -- R1 (10.0.1.0/24) -- R2 (10.0.2.0/24)
                -- R3 (10.0.3.0/24) -- [RX]
    """
    transmisor = Transmisor("TX-01", POTENCIA_TX_W, FRECUENCIA_MUESTREO_HZ,
                            ANCHO_BANDA_HZ, TONOS_PILOTO_HZ)
    canal = CanalFisico("CANAL-01", distancia_m, FRECUENCIA_PORTADORA_HZ,
                        ANCHO_BANDA_HZ, EXPONENTE_PERDIDA,
                        figura_ruido_db=FIGURA_RUIDO_DB, semilla=semilla)
    receptor = Receptor("RX-01", FRECUENCIA_MUESTREO_HZ)
    enlace = EnlaceTelecom(transmisor, canal, receptor)

    r1 = Enrutador("R1", "10.0.1.1")
    r2 = Enrutador("R2", "10.0.2.1")
    r3 = Enrutador("R3", "10.0.3.1")
    r1.agregar_ruta("10.0.1.0/24", ENTREGA_LOCAL)
    r1.agregar_ruta("10.0.2.0/24", "R2")
    r1.agregar_ruta("10.0.3.0/24", "R2")
    r2.agregar_ruta("10.0.1.0/24", "R1")
    r2.agregar_ruta("10.0.2.0/24", ENTREGA_LOCAL)
    r2.agregar_ruta("10.0.3.0/24", "R3")
    r3.agregar_ruta("10.0.1.0/24", "R2")
    r3.agregar_ruta("10.0.2.0/24", "R2")
    r3.agregar_ruta("10.0.3.0/24", ENTREGA_LOCAL)
    r3.aprender_mac(MAC_RECEPTOR, puerto=1)
    for enrutador in (r1, r2, r3):
        enlace.agregar_enrutador(enrutador)
    return enlace


def generar_trafico(cantidad: int, semilla: int) -> list[Paquete]:
    """Genera tráfico mayormente válido, con algunos paquetes defectuosos
    para poblar el registro con firmas de error."""
    rng = np.random.default_rng(semilla)
    tipos = rng.choice(["ok", "sin_ruta", "ttl", "mac"], size=cantidad,
                       p=[0.85, 0.05, 0.05, 0.05])
    paquetes = []
    for id_paquete, tipo in enumerate(tipos, start=1):
        ip_destino = "10.0.9.7" if tipo == "sin_ruta" else IP_RECEPTOR
        mac = "de:ad:be:ef:00:00" if tipo == "mac" else MAC_RECEPTOR
        ttl = 2 if tipo == "ttl" else 16
        paquetes.append(Paquete(id_paquete, IP_TRANSMISOR, ip_destino, mac,
                                ttl=ttl, carga_util=f"dato-{id_paquete}"))
    return paquetes


def main() -> None:
    """Ejecuta la simulación completa y exporta los gráficos."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distancia", type=float, default=1000.0,
                        help="Largo del enlace físico [m] (defecto: 1000)")
    parser.add_argument("--paquetes", type=int, default=500,
                        help="Cantidad de paquetes a enviar (defecto: 500)")
    parser.add_argument("--semilla", type=int, default=42,
                        help="Semilla aleatoria para reproducibilidad")
    parser.add_argument("--salida", type=Path, default=Path("resultados"),
                        help="Carpeta donde se guardan los gráficos")
    args = parser.parse_args()

    enlace = construir_enlace(args.distancia, args.semilla)
    canal = enlace.obtener_canal()

    # 1) Capa lógica + física: enviar todos los paquetes
    for paquete in generar_trafico(args.paquetes, args.semilla):
        enlace.enviar_paquete(paquete, "R1")
    registro = enlace.obtener_registro()

    print("=" * 60)
    print(" SIMULACIÓN DE ENLACE DE TELECOMUNICACIONES (EL4203 - Op. C)")
    print("=" * 60)
    print(f"Distancia del enlace : {args.distancia:,.0f} m")
    print(f"Pérdida de trayecto  : {canal.calcular_perdida_db():.1f} dB")
    print(f"Ruido térmico (kTBF) : "
          f"{w_a_dbm(canal.calcular_potencia_ruido_w()):.1f} dBm")
    print(f"Paquetes enviados    : {len(registro)}")
    for estado, cantidad in sorted(registro.contar_errores().items()):
        print(f"  {estado:<30s}: {cantidad}")

    # 2) Auditoría: búsqueda binaria en el registro ordenado
    print("-" * 60)
    objetivos = (1, len(registro) // 2, len(registro), len(registro) + 99)
    for objetivo in objetivos:
        entrada = registro.buscar_binaria_recursiva(objetivo)
        if entrada is None:
            print(f"Paquete #{objetivo}: no existe en el registro")
        else:
            ruta = " -> ".join(entrada.ruta)
            print(f"Paquete #{objetivo}: {entrada.estado} vía {ruta}")

    # 3) Resultado espectral y gráficos IEEE
    resultado = enlace.obtener_ultimo_resultado()
    print("-" * 60)
    if resultado is None:
        print("Ningún paquete llegó a la capa física; no hay espectro.")
        return
    print(f"Potencia recibida    : {resultado.potencia_recibida_dbm:.1f} dBm")
    print(f"SNR estimada (FFT)   : {resultado.snr_db:.1f} dB")
    print(f"Tonos detectados [Hz]: {resultado.tonos_detectados_hz}")

    distancias = np.logspace(1, np.log10(20_000), 40)
    snr_simulada = enlace.simular_barrido_distancias(distancias)
    transmisor = enlace.obtener_transmisor()
    potencia_tx_dbm = w_a_dbm(transmisor.obtener_potencia_tx())
    snr_teorica = (potencia_tx_dbm - canal.calcular_perdida_db(distancias)
                   - w_a_dbm(canal.calcular_potencia_ruido_w()))

    ruta_1 = graficar_espectro(
        resultado, args.salida / "espectro_recibido.pdf", args.distancia)
    ruta_2 = graficar_snr_vs_distancia(
        distancias, snr_simulada, snr_teorica,
        args.salida / "snr_vs_distancia.pdf",
        canal.obtener_exponente_perdida())
    print(f"Gráficos exportados  : {ruta_1}, {ruta_2}")


if __name__ == "__main__":
    main()
