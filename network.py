"""Funciones de grafos y calculo del fitness."""

from collections import deque
from dataclasses import dataclass
from typing import Sequence

import networkx as nx

from config import ENLACES, NUM_ENRUTADORES, PENALIZACION_DESCONEXION, PENALIZACION_PUENTE

Cromosoma = tuple[int, ...]


@dataclass(frozen=True)
class ResultadoFitness:
    """Resultado de evaluar una topologia."""

    fitness: float
    costo: int
    latencia: int
    conectado: bool
    puentes: tuple[tuple[int, int], ...]
    penalizacion_desconexion: int
    penalizacion_puentes: int

    @property
    def puntos_falla(self) -> int:
        """Cantidad de enlaces que son puntos unicos de falla."""

        return len(self.puentes)


def crear_grafo(cromosoma: Sequence[int]) -> nx.Graph:
    """Crea un grafo con los enlaces cuyo bit vale uno."""

    grafo = nx.Graph()
    grafo.add_nodes_from(range(NUM_ENRUTADORES))
    for bit, enlace in zip(cromosoma, ENLACES):
        if bit:
            grafo.add_edge(enlace.origen, enlace.destino)
    return grafo


def es_conectado_bfs(cromosoma: Sequence[int]) -> bool:
    """Comprueba conectividad usando un recorrido BFS."""

    vecinos: dict[int, list[int]] = {nodo: [] for nodo in range(NUM_ENRUTADORES)}
    for bit, enlace in zip(cromosoma, ENLACES):
        if bit:
            vecinos[enlace.origen].append(enlace.destino)
            vecinos[enlace.destino].append(enlace.origen)

    visitados = {0}
    pendientes = deque([0])
    while pendientes:
        actual = pendientes.popleft()
        for vecino in vecinos[actual]:
            if vecino not in visitados:
                visitados.add(vecino)
                pendientes.append(vecino)
    return len(visitados) == NUM_ENRUTADORES


def buscar_puentes(cromosoma: Sequence[int]) -> tuple[tuple[int, int], ...]:
    """Encuentra enlaces cuya eliminacion rompe el grafo."""

    return tuple(sorted(nx.bridges(crear_grafo(cromosoma))))


def calcular_fitness(cromosoma: Sequence[int]) -> ResultadoFitness:
    """Calcula Z = costo + latencia + penalizaciones."""

    activos = [enlace for bit, enlace in zip(cromosoma, ENLACES) if bit]
    costo = sum(enlace.costo for enlace in activos)
    latencia = sum(enlace.latencia for enlace in activos)
    conectado = es_conectado_bfs(cromosoma)
    puentes = buscar_puentes(cromosoma) if conectado else ()
    penalizacion_desconexion = 0 if conectado else PENALIZACION_DESCONEXION
    penalizacion_puentes = len(puentes) * PENALIZACION_PUENTE
    return ResultadoFitness(
        fitness=costo + latencia + penalizacion_desconexion + penalizacion_puentes,
        costo=costo,
        latencia=latencia,
        conectado=conectado,
        puentes=puentes,
        penalizacion_desconexion=penalizacion_desconexion,
        penalizacion_puentes=penalizacion_puentes,
    )


es_grafo_conexo = es_conectado_bfs
