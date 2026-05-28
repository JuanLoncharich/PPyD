# Proyecto Final Quicksort - Secuencial y Paralelo

Implementación de Quicksort para ordenar jugadores de ajedrez, en versiones secuencial y paralela.

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

## Dataset

- **Fuente**: Top chess players agosto 2020
- **Total registros**: 977,687 jugadores
- **Jugadores válidos**: 428,313 (con ratings > 0)
- **Tamaño**: ~47 MB

## Versiones

### Secuencial (quicksort.cpp)

- **Estructura**: LinkedList
- **Algoritmo**: Quicksort con median-of-three
- **Compilación**: `g++ -O3 -std=c++17 quicksort.cpp -o quicksort`
- **Ejecución**: `./quicksort`

### Paralela (parallel/hyperquicksort.cpp)

- **Estructura**: LinkedList + MPI
- **Algoritmo**: Hyperquicksort (hypercube communication)
- **Compilación**: En login node del cluster CCAD
- **Ejecución**: `sbatch run.slurm`

## Resultados

| Versión | Jugadores | Tiempo |
|---------|-----------|--------|
| Secuencial | 428,313 | ~X ms |
| Paralela (4 proc) | 428,313 | ~1.3 s |

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
