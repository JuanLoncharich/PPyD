# Proyecto Final Quicksort - Secuencial y Paralelo

Implementación de Quicksort para ordenar jugadores de ajedrez, en versiones secuencial y paralela.

**[Documentación de Experimentos](experiments/README.md)** - Framework completo para análisis de rendimiento

## Estructura del Proyecto

```
proyecto_final_quicksort/
├── quicksort.cpp           # Versión secuencial (LinkedList)
├── parallel/
│   ├── hyperquicksort.cpp  # Versión paralela (LinkedList + MPI)
│   ├── run.slurm          # Script SLURM
│   ├── Makefile           # Makefile para compilación
│   ├── README.md          # Documentación paralela
│   └── results/           # Resultados de ejecuciones
├── generate_players.py    # Script para generar dataset
└── top_chess_players_aug_2020.csv  # Dataset (47MB)
```

## Uso

### Secuencial

```bash
# Compilar
g++ -O3 -std=c++17 quicksort.cpp -o quicksort

# Ejecutar con opciones
./quicksort                              # Usa CSV por defecto
./quicksort --csv data.csv              # CSV específico
./quicksort --generate 10000           # Genera 10000 jugadores aleatorios
./quicksort --help                     # Muestra ayuda
```

### Paralela (Cluster CCAD)

```bash
# Compilar (en login node)
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp

# Ejecutar con SLURM
sbatch run.slurm                                     # Usa CSV por defecto
```

Para generar jugadores aleatorios en el cluster, modificar `run.slurm`:
```bash
#!/bin/bash
#SBATCH --job-name=hyperqs
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --partition=short
#SBATCH --time=00:05:00
#SBATCH --output=hyper_%j.out

. /etc/profile
cd ~/hyperquicksort
srun ./hyperquicksort --generate 100000
```

## Opciones de Línea de Comandos

| Opción | Descripción |
|--------|-------------|
| `--csv <file>` | Cargar jugadores desde archivo CSV |
| `--generate N` | Generar N jugadores aleatorios en runtime |
| `--help` | Mostrar ayuda |

## Dataset

- **Fuente**: Top chess players agosto 2020
- **Total registros**: 977,687 jugadores
- **Jugadores válidos**: 428,313 (con ratings > 0)
- **Tamaño**: ~47 MB

## Resultados

| Versión | Jugadores | Tiempo |
|---------|-----------|--------|
| Secuencial | 428,313 | ~X ms |
| Paralela (4 proc) | 428,313 | ~1.3 s |
| Paralela (4 proc) | 100,000 (gen) | ~X ms |

## Top 5 Jugadores (por rating promedio)

| Rank | Título | Nombre | Mean |
|------|--------|--------|------|
| 1 | GM | Carlsen, Magnus | 2876.7 |
| 2 | GM | Nakamura, Hikaru | 2821.7 |
| 3 | GM | Vachier-Lagrave, Maxime | 2820.0 |
| 4 | GM | Ding, Liren | 2805.0 |
| 5 | GM | Kasparov, Garry | 2798.7 |

## Estructura de Datos Compartida

```cpp
struct Player {
    std::string name;
    std::string title;
    int standard_rating, rapid_rating, blitz_rating;
    double mean;
};

struct Node {
    Player data;
    Node *next;
};

class LinkedList {
    Node *head, *tail;
    int size;
    void push_back(const Player &p);
    void sort();  // Quicksort
};
```

## Cluster CCAD

- **Host**: mulatona.ccad.unc.edu.ar
- **Sistema**: SLURM
- **Nodos**: 7 (bdw01-07)
- **Cores/nodo**: 32

Documentación completa en `parallel/README.md`
