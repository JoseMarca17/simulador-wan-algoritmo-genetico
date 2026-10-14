"""Interfaz del simulador con la distribucion original mejorada."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import ENLACES, ENRUTADORES, SEMILLA, TAMANO_POBLACION, TASA_MUTACION
from genetic import AlgoritmoGenetico
from network import ResultadoFitness


class SimuladorWAN(tk.Tk):
    """Dashboard con controles arriba, graficos a la izquierda y datos a la derecha."""

    MIN_GENERACIONES = 5
    MAX_GENERACIONES = 100
    MAX_SIN_MEJORA = 25

    COLORES = {
        "fondo": "#1e1e2e",
        "panel": "#181825",
        "tarjeta": "#24243a",
        "texto": "#f5f5f5",
        "gris": "#a6adc8",
        "cyan": "#00d2d3",
        "verde": "#2ecc71",
        "rojo": "#ff6b6b",
        "amarillo": "#f9c74f",
        "rejilla": "#45475a",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Optimización de Redes WAN | Algoritmos Genéticos")
        self.geometry("1400x900")
        self.minsize(1150, 760)
        self.configure(bg=self.COLORES["fondo"])
        self.ejecutando = False
        self.algoritmo = AlgoritmoGenetico(TAMANO_POBLACION, TASA_MUTACION, semilla=SEMILLA)
        self._configurar_estilos()
        self._crear_interfaz()
        self._actualizar_vista()
        self._escribir_log("Simulador iniciado con semilla reproducible.")

    def _configurar_estilos(self) -> None:
        """Configura ttk para mantener una apariencia oscura consistente."""

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        c = self.COLORES
        estilo.configure("TFrame", background=c["fondo"])
        estilo.configure("Panel.TFrame", background=c["panel"])
        estilo.configure("TLabel", background=c["fondo"], foreground=c["texto"])
        estilo.configure("Panel.TLabel", background=c["panel"], foreground=c["texto"])
        estilo.configure("Gris.TLabel", background=c["fondo"], foreground=c["gris"])
        estilo.configure("Titulo.TLabel", background=c["fondo"], foreground=c["cyan"], font=("Segoe UI", 19, "bold"))
        estilo.configure("TButton", background=c["tarjeta"], foreground=c["texto"], padding=(10, 7), borderwidth=0)
        estilo.map("TButton", background=[("active", c["cyan"])], foreground=[("active", c["fondo"])])
        estilo.configure("Principal.TButton", background=c["cyan"], foreground=c["fondo"])
        estilo.configure("Peligro.TButton", background="#713f46", foreground=c["texto"])
        estilo.configure("TScale", background=c["panel"], troughcolor=c["rejilla"])
        estilo.configure("Treeview", background=c["tarjeta"], fieldbackground=c["tarjeta"], foreground=c["texto"], rowheight=27, borderwidth=0)
        estilo.configure("Treeview.Heading", background=c["panel"], foreground=c["cyan"], font=("Segoe UI", 9, "bold"), relief="flat")
        estilo.map("Treeview", background=[("selected", "#285b66")])

    def _crear_interfaz(self) -> None:
        """Construye la distribucion tipo panel del programa original."""

        encabezado = ttk.Frame(self)
        encabezado.pack(fill="x", padx=18, pady=(15, 8))
        ttk.Label(encabezado, text="OPTIMIZACIÓN DE REDES WAN", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text="Diseno evolutivo de una red WAN | 5 routers | 7 enlaces candidatos", style="Gris.TLabel").pack(anchor="w")

        controles = ttk.Frame(self, style="Panel.TFrame")
        controles.pack(fill="x", padx=18, pady=(0, 10))
        self._crear_controles(controles)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(0, 15))
        izquierda = ttk.Frame(cuerpo)
        izquierda.pack(side="left", fill="both", expand=True)
        derecha = ttk.Frame(cuerpo, style="Panel.TFrame", width=470)
        derecha.pack(side="right", fill="both", padx=(14, 0))
        derecha.pack_propagate(False)
        self._crear_graficos(izquierda)
        self._crear_panel_datos(derecha)

    def _crear_controles(self, marco: ttk.Frame) -> None:
        """Agrega botones y parametros en la barra superior."""

        c = self.COLORES
        ttk.Label(marco, text="CONTROLES", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(14, 10))
        ttk.Button(marco, text="SIGUIENTE GENERACION", style="Principal.TButton", command=self._siguiente).pack(side="left", padx=4, pady=10)
        self.boton_ejecucion = ttk.Button(marco, text="EJECUCION CONTINUA", command=self._alternar_ejecucion)
        self.boton_ejecucion.pack(side="left", padx=4, pady=10)
        ttk.Button(marco, text="REINICIAR", style="Peligro.TButton", command=self._reiniciar).pack(side="left", padx=4, pady=10)

        ttk.Label(marco, text="Mutacion", style="Panel.TLabel").pack(side="left", padx=(20, 3))
        self.valor_mutacion = tk.DoubleVar(value=TASA_MUTACION)
        self.etiqueta_mutacion = ttk.Label(marco, text="15%", style="Panel.TLabel")
        self.etiqueta_mutacion.pack(side="left", padx=(0, 3))
        ttk.Scale(marco, from_=0, to=1, variable=self.valor_mutacion, command=self._cambiar_mutacion, length=100).pack(side="left")

        ttk.Label(marco, text="Poblacion", style="Panel.TLabel").pack(side="left", padx=(15, 3))
        self.valor_poblacion = tk.DoubleVar(value=TAMANO_POBLACION)
        self.etiqueta_poblacion = ttk.Label(marco, text=str(TAMANO_POBLACION), style="Panel.TLabel")
        self.etiqueta_poblacion.pack(side="left", padx=(0, 3))
        ttk.Scale(marco, from_=4, to=24, variable=self.valor_poblacion, command=self._cambiar_poblacion, length=100).pack(side="left")
        self.etiqueta_generacion = ttk.Label(marco, text="Generacion: 0", style="Panel.TLabel", font=("Consolas", 10, "bold"))
        self.etiqueta_generacion.pack(side="right", padx=16)

    def _crear_graficos(self, marco: ttk.Frame) -> None:
        """Prepara las areas del grafo WAN y la curva de convergencia."""

        figura = Figure(figsize=(8, 7), dpi=100, facecolor=self.COLORES["fondo"])
        self.eje_grafo = figura.add_subplot(211)
        self.eje_curva = figura.add_subplot(212)
        figura.subplots_adjust(left=.04, right=.98, top=.95, bottom=.08, hspace=.42)
        self.canvas = FigureCanvasTkAgg(figura, master=marco)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _crear_panel_datos(self, panel: ttk.Frame) -> None:
        """Crea la tabla, tarjetas de metricas, resumen y bitacora."""

        c = self.COLORES
        ttk.Label(panel, text="POBLACION DE LA GENERACION ACTUAL", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(14, 7))
        columnas = ("id", "cromosoma", "costo", "latencia", "estado", "puentes", "fitness")
        self.tabla = ttk.Treeview(panel, columns=columnas, show="headings", height=7)
        titulos = {"id": "ID", "cromosoma": "GENES", "costo": "COSTO", "latencia": "MS", "estado": "RED", "puentes": "FALLA", "fitness": "Z"}
        anchos = {"id": 42, "cromosoma": 85, "costo": 65, "latencia": 50, "estado": 70, "puentes": 50, "fitness": 60}
        for columna in columnas:
            self.tabla.heading(columna, text=titulos[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="center")
        self.tabla.tag_configure("mejor", foreground=c["verde"])
        self.tabla.pack(fill="x", padx=14)

        ttk.Label(panel, text="METRICAS DEL MEJOR DISENO", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        self.texto_metricas = tk.StringVar()
        ttk.Label(panel, textvariable=self.texto_metricas, style="Panel.TLabel", justify="left", font=("Consolas", 9)).pack(anchor="w", padx=14)

        ttk.Label(panel, text="MEJOR SOLUCION GLOBAL", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        self.texto_mejor = tk.StringVar()
        ttk.Label(panel, textvariable=self.texto_mejor, style="Panel.TLabel", justify="left", wraplength=430, font=("Consolas", 9)).pack(anchor="w", padx=14)

        ttk.Label(panel, text="BITACORA DE OPERADORES", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(14, 5))
        self.bitacora = tk.Text(panel, height=9, bg=c["tarjeta"], fg=c["texto"], insertbackground=c["cyan"], relief="flat", font=("Consolas", 8), wrap="word")
        self.bitacora.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _cambiar_mutacion(self, valor: str) -> None:
        tasa = float(valor)
        self.algoritmo.tasa_mutacion = tasa
        self.etiqueta_mutacion.configure(text=f"{tasa:.0%}")

    def _cambiar_poblacion(self, valor: str) -> None:
        self.etiqueta_poblacion.configure(text=str(max(4, round(float(valor)))))

    def _siguiente(self) -> None:
        if self.ejecutando:
            return
        self._avanzar_generacion()

    def _alternar_ejecucion(self) -> None:
        self.ejecutando = not self.ejecutando
        self.boton_ejecucion.configure(text="PAUSAR EJECUCION" if self.ejecutando else "EJECUCION CONTINUA")
        self._escribir_log("Ejecucion continua activada." if self.ejecutando else "Ejecucion pausada.")
        if self.ejecutando:
            self._ejecutar_paso()

    def _ejecutar_paso(self) -> None:
        if self.ejecutando:
            self._avanzar_generacion()
            self.after(180, self._ejecutar_paso)

    def _avanzar_generacion(self) -> None:
        """Ejecuta una generacion y registra sus operadores."""

        mejor_anterior = min(self.algoritmo.evaluar_poblacion(), key=lambda resultado: resultado.fitness)
        self.algoritmo.siguiente_generacion()
        nuevo = self.algoritmo.estado
        mejor_nuevo = min(self.algoritmo.evaluar_poblacion(), key=lambda resultado: resultado.fitness)
        self._escribir_log(f"\n========== GENERACION {nuevo.generacion} ==========")
        self._escribir_log(f"FITNESS: {mejor_anterior.fitness:.0f} -> {mejor_nuevo.fitness:.0f}")
        for detalle in self.algoritmo.ultimo_log:
            self._escribir_log("• " + detalle)
        self._actualizar_vista()
        self._comprobar_parada()

    def _comprobar_parada(self) -> None:
        """Detiene la ejecucion cuando la red es robusta o converge."""

        red_robusta = self.algoritmo.solucion_estable() and self.algoritmo.estado.generacion >= self.MIN_GENERACIONES
        sin_mejora = self.algoritmo.generaciones_sin_mejora >= self.MAX_SIN_MEJORA
        limite = self.algoritmo.estado.generacion >= self.MAX_GENERACIONES
        if not (red_robusta or sin_mejora or limite):
            return
        estaba_ejecutando = self.ejecutando
        self.ejecutando = False
        self.boton_ejecucion.configure(text="EJECUCION CONTINUA")
        if red_robusta:
            mensaje = "PARADA AUTOMATICA: se encontro el mejor fitness conocido para esta infraestructura."
        elif limite:
            mensaje = f"PARADA AUTOMATICA: se alcanzo el limite de {self.MAX_GENERACIONES} generaciones."
        else:
            mensaje = f"PARADA AUTOMATICA: {self.MAX_SIN_MEJORA} generaciones sin mejorar el fitness."
        self._escribir_log(mensaje)
        if estaba_ejecutando:
            self._escribir_log("La ejecucion continua termino; puedes reiniciar o avanzar manualmente.")

    def _reiniciar(self) -> None:
        self.ejecutando = False
        self.boton_ejecucion.configure(text="EJECUCION CONTINUA")
        self.algoritmo.tamano_poblacion = max(4, round(self.valor_poblacion.get()))
        self.algoritmo.reiniciar()
        self.bitacora.delete("1.0", tk.END)
        self._escribir_log("Poblacion reiniciada con diversidad inicial.")
        self._actualizar_vista()

    def _escribir_log(self, mensaje: str) -> None:
        if hasattr(self, "bitacora"):
            self.bitacora.insert(tk.END, mensaje + "\n")
            self.bitacora.see(tk.END)

    def _mejor_actual(self) -> tuple[tuple[int, ...], ResultadoFitness]:
        resultados = self.algoritmo.evaluar_poblacion()
        indice = min(range(len(resultados)), key=lambda i: resultados[i].fitness)
        return self.algoritmo.estado.poblacion[indice], resultados[indice]

    def _actualizar_vista(self) -> None:
        cromosoma, resultado = self._mejor_actual()
        estado = self.algoritmo.estado
        self.etiqueta_generacion.configure(text=f"Generacion: {estado.generacion}")
        self.texto_metricas.set(f"Costo total: ${resultado.costo}k\nLatencia total: {resultado.latencia} ms\nConectividad: {'CONECTADA' if resultado.conectado else 'DESCONECTADA'}\nPuntos unicos de falla: {resultado.puntos_falla}\nFitness Z: {resultado.fitness:.0f}")
        enlaces_activos = ", ".join(enlace.nombre for bit, enlace in zip(cromosoma, ENLACES) if bit) or "Ninguno"
        self.texto_mejor.set(f"Cromosoma: [{''.join(map(str, cromosoma))}]\nGeneracion encontrada: {estado.generacion}\nEnlaces activos: {enlaces_activos}")
        self._actualizar_tabla()
        self._dibujar_grafo(cromosoma, resultado)
        self._dibujar_curva()

    def _actualizar_tabla(self) -> None:
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        resultados = self.algoritmo.evaluar_poblacion()
        mejor = min(range(len(resultados)), key=lambda i: resultados[i].fitness)
        for indice, (individuo, resultado) in enumerate(zip(self.algoritmo.estado.poblacion, resultados)):
            valores = (f"P{indice + 1}", "".join(map(str, individuo)), f"${resultado.costo}k", resultado.latencia, "OK" if resultado.conectado else "NO", resultado.puntos_falla, f"{resultado.fitness:.0f}")
            self.tabla.insert("", "end", values=valores, tags=("mejor",) if indice == mejor else ())

    def _dibujar_grafo(self, cromosoma: tuple[int, ...], resultado: ResultadoFitness) -> None:
        eje = self.eje_grafo
        eje.clear()
        eje.set_facecolor(self.COLORES["panel"])
        posiciones = {enrutador.id: enrutador.posicion for enrutador in ENRUTADORES}
        for indice, enlace in enumerate(ENLACES):
            activo = bool(cromosoma[indice])
            color = self.COLORES["verde"] if activo and resultado.conectado else self.COLORES["rojo"] if activo else self.COLORES["rejilla"]
            eje.plot([posiciones[enlace.origen][0], posiciones[enlace.destino][0]], [posiciones[enlace.origen][1], posiciones[enlace.destino][1]], color=color, linewidth=2.8 if activo else 1, linestyle="-" if activo else ":", alpha=1 if activo else .55)
            x = (posiciones[enlace.origen][0] + posiciones[enlace.destino][0]) / 2
            y = (posiciones[enlace.origen][1] + posiciones[enlace.destino][1]) / 2
            etiqueta = f"e{indice + 1}\n${enlace.costo}k | {enlace.latencia}ms"
            eje.text(x, y, etiqueta, color=self.COLORES["texto"] if activo else self.COLORES["gris"], fontsize=7, ha="center", va="center", bbox={"boxstyle": "round,pad=.2", "facecolor": self.COLORES["tarjeta"], "edgecolor": color, "alpha": .95 if activo else .55})
        eje.scatter([p[0] for p in posiciones.values()], [p[1] for p in posiciones.values()], s=820, c="#155e75", edgecolors=self.COLORES["cyan"], linewidths=2)
        for enrutador in ENRUTADORES:
            eje.text(*enrutador.posicion, enrutador.nombre, color=self.COLORES["texto"], ha="center", va="center", fontweight="bold")
        eje.set_title("TOPOLOGIA WAN DEL MEJOR DISEÑO " + ("CONECTADA" if resultado.conectado else "DESCONECTADA"), color=self.COLORES["verde"] if resultado.conectado else self.COLORES["rojo"], loc="left", fontweight="bold")
        eje.set_xlim(-.05, 1.05)
        eje.set_ylim(.02, .92)
        eje.axis("off")

    def _dibujar_curva(self) -> None:
        eje = self.eje_curva
        eje.clear()
        eje.set_facecolor(self.COLORES["panel"])
        estado = self.algoritmo.estado
        generaciones = range(len(estado.historial_mejor))
        eje.plot(generaciones, estado.historial_mejor, color=self.COLORES["cyan"], marker="o", markersize=3, linewidth=2, label="Mejor fitness Z")
        eje.plot(generaciones, estado.historial_promedio, color=self.COLORES["amarillo"], linestyle="--", linewidth=1.5, label="Promedio poblacion")
        eje.set_title("CONVERGENCIA DEL FITNESS", color=self.COLORES["texto"], loc="left", fontweight="bold")
        eje.set_xlabel("Generacion", color=self.COLORES["gris"])
        eje.set_ylabel("Fitness Z (minimizar)", color=self.COLORES["gris"])
        eje.tick_params(colors=self.COLORES["gris"], labelsize=8)
        for borde in eje.spines.values():
            borde.set_color(self.COLORES["rejilla"])
        eje.grid(color=self.COLORES["rejilla"], linestyle=":", alpha=.55)
        eje.legend(facecolor=self.COLORES["tarjeta"], edgecolor=self.COLORES["rejilla"], labelcolor=self.COLORES["texto"], fontsize=8)
        self.canvas.draw_idle()


def ejecutar() -> None:
    """Inicia la ventana principal."""

    SimuladorWAN().mainloop()
