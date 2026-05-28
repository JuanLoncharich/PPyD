# QuickSort Performance Experiments

Framework para ejecutar y analizar experimentos de rendimiento del QuickSort secuencial y paralelo (Hyperquicksort) en el cluster CCAD.

## Configuración Experimental

### Tamaños de Array (N)
- 100,000 elementos (100k)
- 1,000,000 elementos (1M)
- 2,500,000 elementos (2.5M)

### Número de Procesos (p)
- 1, 2, 4, 8, 16, 32 procesos MPI

### Repeticiones
- 3 ejecuciones por configuración
- Se reporta promedio ± desviación estándar

## Estructura de Directorios

```
experiments/
├── slurm/                 # Scripts SLURM para cluster
│   ├── run_seq.slurm     # Ejecución secuencial
│   └── run_par.slurm     # Ejecución paralela
├── scripts/               # Scripts de análisis
│   ├── run_experiments.sh # Enviar todos los jobs
│   ├── collect_results.py # Parsear outputs y extraer métricas
│   └── plot_results.py   # Generar gráficos
├── results/               # Output files de SLURM (generado al ejecutar)
├── plots/                 # Gráficos generados (generado al ejecutar)
├── sequential_times.csv  # Tiempos secuenciales (promedio)
└── parallel_times.csv    # Tiempos paralelos (promedio)
```

## Flujo de Trabajo

### 1. Compilar los Binarios

En el cluster CCAD (login node):

```bash
# Secuencial
cd ~/hyperquicksort
g++ -O3 -std=c++17 quicksort.cpp -o quicksort_seq

# Paralelo
cd ~/hyperquicksort/parallel
export PATH=/ccad/stack/23.02/base/linux-rocky9-broadwell/gcc-12.2.0/openmpi-4.1.4-olpnqaqkqy7xxf26653hwdpsc42tno6w/bin:$PATH
make
```

### 2. Ejecutar Experimentos

**Opción A: Desde tu máquina local**

```bash
cd experiments/scripts
chmod +x run_experiments.sh
./run_experiments.sh
```

Este script:
1. Crea los scripts SLURM correspondientes
2. Los copia al cluster
3. Envía todos los jobs (secuencial y paralelo)
4. Reporta los job IDs

**Opción B: Manualmente en el cluster**

```bash
cd ~/hyperquicksort/experiments/slurm

# Ejemplo: secuencial 100k, run 1
export SIZE=100000 SIZE_NAME=100k RUN=1 EXP_DIR=$HOME/hyperquicksort
sbatch run_seq.slurm

# Ejemplo: paralelo 100k, 4 procesos, run 1
export SIZE=100000 SIZE_NAME=100k PROCS=4 RUN=1 EXP_DIR=$HOME/hyperquicksort
sbatch run_par.slurm
```

### 3. Recolectar Resultados

Después de que todos los jobs completen:

```bash
cd experiments/scripts
python3 collect_results.py
```

Este script:
1. Lee todos los archivos `.out` del directorio `results/`
2. Extrae los tiempos usando regex
3. Calcula promedios y desviaciones estándar
4. Genera `sequential_times.csv` y `parallel_times.csv`

### 4. Generar Gráficos

```bash
cd experiments/scripts
python3 plot_results.py
```

Genera 7 archivos PNG en `experiments/plots/`:
- `00_summary_table.png` - Tabla resumen de métricas
- `01_execution_time.png` - Tiempo vs Tamaño (log-log)
- `02_speedup.png` - Speedup con referencia ideal S=p
- `03_efficiency.png` - Eficiencia con referencia ideal 100%
- `04_strong_scaling.png` - Strong scaling con T=T_s/p
- `05_weak_scaling.png` - Weak scaling con T=constante
- `06_load_balance.png` - Distribución de datos por proceso

## Métricas Calculadas

| Métrica | Fórmula | Referencia Teórica |
|---------|---------|-------------------|
| Tiempo Secuencial | T_s | - |
| Tiempo Paralelo | T_p | - |
| Speedup | S(p) = T_s / T_p | S_ideal(p) = p |
| Eficiencia | E(p) = (S(p)/p) × 100% | E_ideal = 100% |
| Strong Scaling | T_p(p) para N fijo | T_ideal = T_s / p |
| Weak Scaling | T_p(p) para N ∝ p | T_ideal = constante |

## Requisitos

### Cluster CCAD
- Cuenta en mulatona.ccad.unc.edu.ar
- SLURM para job scheduling
- OpenMPI 4.1.4

### Local (para análisis)
- Python 3.8+
- matplotlib
- numpy
- seaborn

```bash
pip install matplotlib numpy seaborn
```

## Tiempo Estimado de Ejecución

- Total jobs: 3 tamaños × (1 secuencial + 6 configuraciones paralelas) × 3 runs = **63 jobs**
- Tiempo estimado total: ~30-45 minutos (dependiendo de cola del cluster)

## Troubleshooting

**Jobs pendientes por mucho tiempo:**
```bash
squeue -u $USER  # Ver estado
scancel <job_id>  # Cancelar job si es necesario
```

**Error de compilación:**
Verificar que las rutas a MPI sean correctas en `parallel/Makefile`

**Archivos de output vacíos:**
El job puede haber fallado. Revisar el archivo `.err` correspondiente:

```bash
cat ~/hyperquicksort/experiments/results/seq_100k_run1.err
```

## Referencias

- Hyperquicksort: Algorithm for parallel sorting using hypercube communication pattern
- CCAD Wiki: https://wiki.ccad.unc.edu.ar/
- SLURM Documentation: https://slurm.schedmd.com/
