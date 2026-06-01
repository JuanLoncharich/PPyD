# Diseño Experimental: Medición de Balanceo de Cargas

## Objetivo

Cuantificar el grado de balanceo de carga en la implementación paralela de Hyperquicksort, identificando variaciones en el tiempo de cómputo entre procesos que puedan afectar el rendimiento global.

## Métricas Definidas

### 1. Tiempo Local de Ordenamiento ($T_{local,i}$)
Tiempo que cada proceso $i$ invierte en ordenar su subarray local, medido inmediatamente después de la fase de distribución y antes de la recolección final.

### 2. Métricas Agregadas
- **$T_{min}$**: Mínimo tiempo local entre todos los procesos
- **$T_{max}$**: Máximo tiempo local entre todos los procesos
- **$T_{avg}$**: Promedio de tiempos locales

### 3. Porcentaje de Desbalance ($B$)

$$ B = \frac{T_{max} - T_{min}}{T_{max}} \times 100\% $$

Un valor de $B = 0\%$ indica balance perfecto; valores mayores indican desbalance.

## Diseño de Medición

### Instrumentación en el Código

La medición se realiza mediante la instrumentación directa del código paralelo:

```cpp
// Cada proceso mide su tiempo local
auto t2 = Clock::now();
std::sort(local_data.begin(), local_data.end(), compare_players);
MPI_Barrier(MPI_COMM_WORLD);
auto t3 = Clock::now();

double local_sort_time = Ms(t3 - t2).count();
```

### Recolección de Datos

1. **Gather en el proceso rank 0**: Se utiliza `MPI_Gather` para recolectar todos los tiempos locales en el proceso maestro.

2. **Cálculo de métricas**: El proceso 0 calcula $T_{min}$, $T_{max}$, $T_{avg}$ y $B$.

3. **Registro detallado**: Se imprime una tabla con el tamaño de subarray y tiempo de cada proceso para análisis posterior.

### Configuraciones Experimentales

Se mide el balanceo para todas las configuraciones del experimento:
- **Tamaños**: 100k, 250k, 750k, 2M, 5M elementos
- **Procesos**: 1, 2, 4, 8, 16, 32 procesos MPI

Cada configuración se ejecuta múltiples veces para obtener desviación estándar.

## Análisis de Resultados

### Visualización

1. **Gráfico de Desbalance vs $p$**: Muestra cómo varía $B$ con el número de procesos para cada tamaño de problema.
2. **Gráfico de Distribución Temporal**: Para cada $p$, muestra $T_{min}$, $T_{avg}$ y $T_{max}$ comparados entre tamaños de problema.

### Interpretación

- **$B < 5\%$**: Balanceo excelente
- **$5\% \leq B < 15\%$**: Balanceo aceptable
- **$B \geq 15\%$**: Desbalance significativo que afecta speedup

## Limitaciones y Consideraciones

1. **Sincronización**: El `MPI_Barrier` asegura que todos los procesos inicien la medición al mismo tiempo, pero el tiempo incluye la latencia de la barrera misma.

2. **Variabilidad porDatos**: Los datos aleatorios pueden producir diferentes distribuciones de pivotes en cada ejecución. Por eso se promedian múltiples ejecuciones.

3. ** overhead de comunicación**: La medición solo cubre la fase de ordenamiento local; no incluye el tiempo de comunicación durante la distribución.
