
* Alumnos:
* Julian Ignacio Fernandez
* Juan Andres Loncharich


# Ejercicio Nº 5

Considerar el Ejercicio 1 desde un punto de vista abstracto, en cuanto a las características y a los elementos de la solución propuesta. Determinar y explicar:

- Qué tipo de estrategias de **descomposición** y **asignación** se utilizaron.
- Cuántos y qué tipos de procesos se propusieron.
- Con qué tipo de modelo de algoritmo puede identificarse mejor.
- Analizar si para el resto de los ejercicios el análisis es similar o si hay cambios significativos.

---

# Ejercicio 1

## Descomposición

La descomposición principal es por **funciones**:

- **Productores**: 10 usuarios.
- **Consumidor**: 1 impresora.

No hay descomposición de datos compleja; únicamente existe un recurso compartido: una **cola**.

## Asignación

- **Estática en cantidad de entidades**:  
  10 + 1 hilos creados al inicio.
- **Dinámica en ejecución**:  
  El orden de acceso a la cola lo determina el planificador y el mecanismo de sincronización.

## Modelo algorítmico

El modelo que mejor lo describe es **Productor–Consumidor con buffer acotado (capacidad 1)**, equivalente a una cola bloqueante.

## Tipos de procesos lógicos

- 2 tipos:
  - Usuario (productor)
  - Impresora (consumidor)
- 11 instancias concurrentes en total.

## Estrategia de coordinación

- Espera bloqueante (mutex + variables de condición).
- Exclusión mutua sobre la cola.
- Señalización de estados: “vacía” / “llena”.

---

# Comparación con los demás ejercicios

## Ejercicio 2

- Mantiene el mismo modelo.
- Cambia parámetros:
  - 2 consumidores.
  - Buffer de tamaño 4.
- La descomposición sigue siendo **productor–consumidor**, pero con mayor paralelismo en el servicio.

## Ejercicio 3

- Cambia el mecanismo de implementación:
  - Procesos en vez de hilos.
- No cambia la lógica abstracta:
  - Sigue siendo productor–consumidor con buffer 1.

## Ejercicio 4

- Combina ambos cambios:
  - 2 impresoras.
  - Buffer de tamaño 4.
  - Uso de procesos.
- Conceptualmente equivalente al Ejercicio 2.
  - Mayor costo de comunicación y cambio de contexto.
