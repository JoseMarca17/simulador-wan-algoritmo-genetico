"""Configuracion inmutable de la infraestructura WAN."""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Enrutador:
    """Router y posicion normalizada para el canvas."""

    id: int
    nombre: str
    funcion: str
    posicion: tuple[float, float]


@dataclass(frozen=True)
class EnlaceCandidato:
    """Enlace candidato de la topologia."""

    id: int
    nombre: str
    origen: int
    destino: int
    costo: int
    latencia: int


ENRUTADORES: Final[tuple[Enrutador, ...]] = (
    Enrutador(0, "R1", "Sede Central", (0.12, 0.78)),
    Enrutador(1, "R2", "Sucursal Norte", (0.88, 0.78)),
    Enrutador(2, "R3", "Sucursal Sur", (0.50, 0.50)),
    Enrutador(3, "R4", "Sucursal Este", (0.16, 0.16)),
    Enrutador(4, "R5", "Datacenter", (0.84, 0.16)),
)

ENLACES: Final[tuple[EnlaceCandidato, ...]] = (
    EnlaceCandidato(0, "e1 R1-R2", 0, 1, 35, 12),
    EnlaceCandidato(1, "e2 R1-R3", 0, 2, 50, 25),
    EnlaceCandidato(2, "e3 R2-R3", 1, 2, 20, 8),
    EnlaceCandidato(3, "e4 R2-R4", 1, 3, 45, 18),
    EnlaceCandidato(4, "e5 R3-R4", 2, 3, 30, 15),
    EnlaceCandidato(5, "e6 R3-R5", 2, 4, 60, 22),
    EnlaceCandidato(6, "e7 R4-R5", 3, 4, 40, 14),
)

NUM_ENRUTADORES: Final[int] = len(ENRUTADORES)
LONGITUD_CROMOSOMA: Final[int] = len(ENLACES)
# Debe superar el costo maximo de una topologia valida para que nunca
# resulte conveniente apagar enlaces y dejar la red desconectada.
PENALIZACION_DESCONEXION: Final[int] = 1000
PENALIZACION_PUENTE: Final[int] = 90
# Mejor fitness conocido para esta infraestructura fija de 5 routers y 7 enlaces.
FITNESS_OBJETIVO: Final[int] = 321
TAMANO_POBLACION: Final[int] = 8
TASA_MUTACION: Final[float] = 0.15
TASA_CRUCE: Final[float] = 1.0
SEMILLA: Final[int] = 42
