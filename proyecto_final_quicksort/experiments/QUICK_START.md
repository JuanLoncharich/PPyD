# Quick Start - Experimentos en Cluster CCAD

Guía rápida para ejecutar experimentos en el cluster.

## Paso 1: Compilar Binarios

```bash
cd ~/hyperquicksort

# Secuencial
g++ -O3 -std=c++17 quicksort_seq.cpp -o quicksort_seq

# Paralelo
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
export LD_LIBRARY_PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/lib:$LD_LIBRARY_PATH
mpicxx -O3 -std=c++17 -o hyperquicksort hyperquicksort.cpp
```

## Paso 2: Ejecutar Experimentos

```bash
cd ~/hyperquicksort/experiments/scripts

# Un tamaño específico (recomendado para empezar)
./run_100k.sh    # 18 jobs, ~5 min
./run_250k.sh    # 18 jobs, ~10 min
./run_750k.sh    # 18 jobs, ~15 min
./run_2M.sh      # 18 jobs, ~30 min
./run_5M.sh      # 18 jobs, ~60 min

# O todos los tamaños (90 jobs totales)
./run_experiments_cluster.sh

# Monitorear cola
squeue -u $USER
```

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

## Configuraciones

| Tamaño | Procesos | Runs | Jobs |
|--------|----------|------|-------|
| 100k | 1, 2, 4, 8, 16, 32 | 3 | 18 |
| 250k | 1, 2, 4, 8, 16, 32 | 3 | 18 |
| 750k | 1, 2, 4, 8, 16, 32 | 3 | 18 |
| 2M | 1, 2, 4, 8, 16, 32 | 3 | 18 |
| 5M | 1, 2, 4, 8, 16, 32 | 3 | 18 |

**Total: 90 jobs** (5 tamaños × 6 configs × 3 runs)

## Tiempos Esperados

- 100k: segundos
- 250k: ~5 segundos
- 750k: ~15 segundos
- 2M: ~1 minuto
- 5M: ~3-5 minutos (paralelo), ~15 min (secuencial)

Total estimado: **2-3 horas** en cluster (dependiendo de cola)

## Troubleshooting

**Jobs pendientes por mucho tiempo:**
```bash
squeue -u $USER  # Ver estado
scancel <job_id>  # Cancelar si es necesario
```

**Error "mpirun: command not found":**
Asegúrate de que el script SLURM incluya:
```bash
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
export LD_LIBRARY_PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/lib:$LD_LIBRARY_PATH
```

**Archivos de output vacíos:**
El job puede haber fallado. Revisa el archivo `.err`:
```bash
cat ~/hyperquicksort/experiments/results/seq_100k_run1.err
```

## Referencias

- DISEÑO EXPERIMENTAL.txt: Detalles completos del diseño experimental
- Hyperquicksort: Algorithm for parallel sorting using hypercube communication
- CCAD Wiki: https://wiki.ccad.unc.edu.ar/
