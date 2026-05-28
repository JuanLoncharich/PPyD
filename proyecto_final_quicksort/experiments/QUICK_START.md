# Quick Start - Experimentos en Cluster CCAD

Guía rápida para ejecutar experimentos en el cluster.

## Paso 1: Compilar Binarios

```bash
cd ~/hyperquicksort

# Secuencial
g++ -O3 -std=c++17 quicksort.cpp -o quicksort_seq

# Paralelo
cd parallel
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
make
```

## Paso 2: Ejecutar Experimentos

```bash
cd ~/hyperquicksort/experiments/scripts
./run_experiments_cluster.sh
```

Esto envía **105 jobs** (5 tamaños × 7 configuraciones × 3 runs).

## Paso 3: Esperar a que Completen

```bash
watch -n 10 squeue -u $USER
```

## Paso 4: Recolectar y Analizar (en tu máquina local)

```bash
# Copiar resultados a tu máquina
scp -r cursoppyd4@mulatona.ccad.unc.edu.ar:~/hyperquicksort/experiments/results \
      ~/path/to/proyecto_final_quicksort/experiments/

# Recolectar métricas
cd ~/path/to/proyecto_final_quicksort/experiments/scripts
python3 collect_results.py

# Generar gráficos
python3 plot_results.py
```

## Resultados

- Gráficos en `experiments/plots/`
- CSVs en `experiments/`

## Configuraciones

| Tamaño | Procesos | Runs |
|--------|----------|------|
| 100k | 1, 2, 4, 8, 16, 32 | 3 |
| 250k | 1, 2, 4, 8, 16, 32 | 3 |
| 750k | 1, 2, 4, 8, 16, 32 | 3 |
| 2M | 1, 2, 4, 8, 16, 32 | 3 |
| 5M | 1, 2, 4, 8, 16, 32 | 3 |

**Total: 105 jobs** (5 tamaños × 7 configs × 3 runs)

## Tiempos Esperados

- 100k: segundos
- 250k: ~5 segundos
- 750k: ~15 segundos
- 2M: ~1 minuto
- 5M: ~3-5 minutos (paralelo), ~15 min (secuencial)

Total: ~1-2 horas en cluster (dependiendo de cola)
