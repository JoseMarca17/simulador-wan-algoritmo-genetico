# Optimización de Redes WAN

Simulador académico de algoritmos genéticos para optimizar una topología WAN con:

- 5 routers.
- 7 enlaces candidatos.
- Cromosomas binarios de 7 bits.
- Selección por torneo.
- Cruce en un punto.
- Mutación bit-flip.
- Elitismo Top-1.
- Visualización de la red y convergencia.

## Requisitos

- Python 3.10 o superior.
- Tkinter, incluido normalmente con Python.

## Instalación

Abre una terminal dentro de esta carpeta y ejecuta:

```bash
python -m venv .venv
```

Activa el entorno virtual.

### Windows

```bash
.venv\Scripts\activate
```

### Linux o macOS

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activo, ejecuta:

```bash
python main.py
```

## Uso rápido

- **Siguiente generación:** ejecuta un ciclo del algoritmo.
- **Ejecución continua:** ejecuta generaciones automáticamente.
- **Reiniciar:** crea una nueva población inicial.
- **Mutación:** cambia la probabilidad de mutación.
- **Población:** cambia el tamaño de la población al reiniciar.
- **Bitácora:** muestra selección, cruce, mutación y elitismo.

La ejecución automática se detiene al encontrar el mejor fitness conocido, después de varias generaciones sin mejora o al alcanzar el límite de seguridad.

## Archivos principales

| Archivo | Función |
| --- | --- |
| `config.py` | Routers, enlaces, costos y constantes. |
| `network.py` | Grafo, conectividad, puentes y fitness. |
| `genetic.py` | Motor del algoritmo genético. |
| `gui.py` | Interfaz gráfica y visualizaciones. |
| `main.py` | Inicio del programa. |
