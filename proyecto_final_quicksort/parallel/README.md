# Hyperquicksort - Implementación Paralela para Cluster CCAD

Implementación del algoritmo **Hyperquicksort** usando MPI para ordenamiento paralelo en el cluster CCAD (Mulatona).

## Características

- **Estructura de datos**: LinkedList (igual que versión secuencial)
- **Dataset**: 977,687 jugadores de ajedrez (428,313 con ratings válidos)
- **Algoritmo**: Hyperquicksort paralelo con hypercube communication

## Algoritmo Hyperquicksort

1. **Ordenamiento Local**: Quicksort sobre LinkedList en cada procesador
2. **Selección de Pivote**: Promedio de medianas de todos los procesadores
3. **Partición**: División de LinkedList según pivote
4. **Intercambio**: Comunicación coordinada para evitar deadlock
5. **Fusión**: Merge de LinkedLists recibidas
6. **Iteraciones**: d = log₂(P) dimensiones del hypercube

## Compilación

En **login node** únicamente:

```bash
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
export LD_LIBRARY_PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/lib:$LD_LIBRARY_PATH

mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp
```

O usar el Makefile:
```bash
make
```

## Ejecución

**NO ejecutar en login node**. Usar SLURM:

```bash
sbatch run.slurm
```

## Resultados (4 procesadores)

- 428,313 jugadores ordenados
- Tiempo de ordenamiento: ~430 ms
- Tiempo total: ~1.3 segundos

## Estructura LinkedList

```cpp
struct Node {
    Player data;
    Node *next;
};

class LinkedList {
    Node *head, *tail;
    int size;
    void push_back(const Player &p);
    void sort();  // Quicksort para LinkedList
};
```

## Referencias

- Wiki CCAD: https://wiki.ccad.unc.edu.ar/
- Documentación SLURM: http://slurm.schedmd.com/
