"""Motor genetico independiente de la interfaz grafica."""

from dataclasses import dataclass, field
import random
from typing import Callable, Sequence

from config import FITNESS_OBJETIVO, LONGITUD_CROMOSOMA, SEMILLA, TAMANO_POBLACION, TASA_CRUCE, TASA_MUTACION
from network import Cromosoma, ResultadoFitness, calcular_fitness


@dataclass
class EstadoEvolucion:
    """Datos actuales de la simulacion."""

    poblacion: list[Cromosoma]
    generacion: int = 0
    mejor_global: Cromosoma | None = None
    resultado_mejor: ResultadoFitness | None = None
    historial_mejor: list[float] = field(default_factory=list)
    historial_promedio: list[float] = field(default_factory=list)


class AlgoritmoGenetico:
    """Minimiza el fitness mediante torneo, cruce, mutacion y elitismo."""

    def __init__(
        self,
        tamano_poblacion: int = TAMANO_POBLACION,
        tasa_mutacion: float = TASA_MUTACION,
        tasa_cruce: float = TASA_CRUCE,
        semilla: int | None = SEMILLA,
        evaluador: Callable[[Sequence[int]], ResultadoFitness] = calcular_fitness,
    ) -> None:
        self.tamano_poblacion = max(4, tamano_poblacion)
        self.tasa_mutacion = max(0.0, min(1.0, tasa_mutacion))
        self.tasa_cruce = max(0.0, min(1.0, tasa_cruce))
        self.evaluador = evaluador
        self.azar = random.Random(semilla)
        self.ultimo_log: list[str] = []
        self.generaciones_sin_mejora = 0
        self.estado = EstadoEvolucion(self._crear_poblacion())
        self._guardar_historial()

    def _crear_poblacion(self) -> list[Cromosoma]:
        """Crea una poblacion inicial variada y reproducible."""

        poblacion = [
            (0,) * LONGITUD_CROMOSOMA,
            (1,) * LONGITUD_CROMOSOMA,
            (1, 0, 1, 0, 1, 0, 1),
            (1, 1, 0, 0, 0, 1, 1),
        ][: self.tamano_poblacion]
        while len(poblacion) < self.tamano_poblacion:
            individuo = tuple(self.azar.randint(0, 1) for _ in range(LONGITUD_CROMOSOMA))
            if individuo not in poblacion or len(poblacion) >= 14:
                poblacion.append(individuo)
        self.azar.shuffle(poblacion)
        return poblacion

    def evaluar_poblacion(self) -> list[ResultadoFitness]:
        """Evalua la poblacion actual."""

        return [self.evaluador(individuo) for individuo in self.estado.poblacion]

    def _guardar_historial(self) -> None:
        resultados = self.evaluar_poblacion()
        indice = min(range(len(resultados)), key=lambda i: resultados[i].fitness)
        mejor = resultados[indice]
        if self.estado.resultado_mejor is None or mejor.fitness < self.estado.resultado_mejor.fitness:
            self.estado.mejor_global = self.estado.poblacion[indice]
            self.estado.resultado_mejor = mejor
            self.generaciones_sin_mejora = 0
        else:
            self.generaciones_sin_mejora += 1
        self.estado.historial_mejor.append(mejor.fitness)
        self.estado.historial_promedio.append(sum(r.fitness for r in resultados) / len(resultados))

    def seleccionar_torneo(self) -> Cromosoma:
        """Selecciona el mejor de dos individuos."""

        candidatos = self.azar.sample(self.estado.poblacion, 2)
        return min(candidatos, key=lambda individuo: self.evaluador(individuo).fitness)

    def cruzar(self, padre_a: Cromosoma, padre_b: Cromosoma) -> tuple[Cromosoma, Cromosoma]:
        """Realiza cruce en un punto."""

        if self.azar.random() > self.tasa_cruce:
            self.ultimo_corte = None
            return padre_a, padre_b
        corte = self.azar.randint(1, LONGITUD_CROMOSOMA - 1)
        self.ultimo_corte = corte
        return padre_a[:corte] + padre_b[corte:], padre_b[:corte] + padre_a[corte:]

    def mutar(self, individuo: Cromosoma) -> Cromosoma:
        """Invierte cada bit segun la tasa de mutacion."""

        return tuple(1 - bit if self.azar.random() < self.tasa_mutacion else bit for bit in individuo)

    def mutar_con_detalle(self, individuo: Cromosoma) -> tuple[Cromosoma, list[int]]:
        """Muta un individuo y devuelve tambien las posiciones modificadas."""

        mutado = list(individuo)
        posiciones: list[int] = []
        for posicion, bit in enumerate(mutado):
            if self.azar.random() < self.tasa_mutacion:
                mutado[posicion] = 1 - bit
                posiciones.append(posicion + 1)
        return tuple(mutado), posiciones

    def siguiente_generacion(self) -> EstadoEvolucion:
        """Crea una generacion y conserva el mejor individuo."""

        resultados = self.evaluar_poblacion()
        indice_elite = min(range(len(resultados)), key=lambda i: resultados[i].fitness)
        elite = self.estado.poblacion[indice_elite]
        nueva_poblacion = [elite]
        self.ultimo_log = [f"ELITISMO TOP-1: {''.join(map(str, elite))} | Z={resultados[indice_elite].fitness:.0f}"]
        while len(nueva_poblacion) < self.tamano_poblacion:
            padre_a = self.seleccionar_torneo()
            padre_b = self.seleccionar_torneo()
            hijo_a, hijo_b = self.cruzar(padre_a, padre_b)
            corte = f"bit {self.ultimo_corte}" if self.ultimo_corte else "sin cruce"
            self.ultimo_log.append(
                f"SELECCION: A={''.join(map(str, padre_a))} B={''.join(map(str, padre_b))} | CRUCE: {corte}"
            )
            hijo_a_mutado, cambios_a = self.mutar_con_detalle(hijo_a)
            nueva_poblacion.append(hijo_a_mutado)
            self.ultimo_log.append(
                f"MUTACION H{len(nueva_poblacion) - 1}: {''.join(map(str, hijo_a))} -> {''.join(map(str, hijo_a_mutado))} | genes: {cambios_a or 'ninguno'}"
            )
            if len(nueva_poblacion) < self.tamano_poblacion:
                hijo_b_mutado, cambios_b = self.mutar_con_detalle(hijo_b)
                nueva_poblacion.append(hijo_b_mutado)
                self.ultimo_log.append(
                    f"MUTACION H{len(nueva_poblacion) - 1}: {''.join(map(str, hijo_b))} -> {''.join(map(str, hijo_b_mutado))} | genes: {cambios_b or 'ninguno'}"
                )
        self.estado.poblacion = nueva_poblacion[: self.tamano_poblacion]
        self.estado.generacion += 1
        self._guardar_historial()
        return self.estado

    def solucion_estable(self) -> bool:
        """Indica si se alcanzo el mejor fitness conocido de esta red."""

        mejor = min(self.evaluar_poblacion(), key=lambda resultado: resultado.fitness)
        return mejor.conectado and mejor.puntos_falla == 0 and mejor.fitness <= FITNESS_OBJETIVO

    def reiniciar(self) -> EstadoEvolucion:
        """Reinicia poblacion, generacion e historiales."""

        self.estado = EstadoEvolucion(self._crear_poblacion())
        self.generaciones_sin_mejora = 0
        self.ultimo_log = []
        self._guardar_historial()
        return self.estado
