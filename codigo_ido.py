# -*- coding: utf-8 -*-
"""codigo_idO.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WpGPi7Rrin-Y0YrQ12anHwaoUE9QAC_1
"""

import math
import time
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, value, LpStatus
import matplotlib.pyplot as plt
import random
import itertools
import numpy as np
import pandas as pd




#===========================================================
# Función: calcular matriz de distancias
#===========================================================
def calcular_matriz_dist(coords, inicio = None):
    """
    Dada una lista de ciudades con sus coordenadas [(id_ciudad, x, y), ...],
    calcula la matriz de distancias euclidianas redondeadas.

    Parámetros:
        coords: lista de tuplas (id_ciudad, x, y).

    Retorna:
        matriz_dist: matriz (lista de listas) n x n, con las distancias
                     entre cada par de ciudades.
    """
    n = len(coords)
    matriz_dist = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                matriz_dist[i][j] = 0
            else:
                xi, yi = coords[i][1], coords[i][2]
                xj, yj = coords[j][1], coords[j][2]
                dist = math.sqrt((xi - xj)**2 + (yi - yj)**2)
                matriz_dist[i][j] = round(dist)
    return matriz_dist

#===========================================================
# Heurística del Vecino Más Cercano
#===========================================================
def vecino_mas_cercano(matriz_dist, inicio=0):
    """
    Aplica la heurística del vecino más cercano para el TSP.
    Comienza en la ciudad 'inicio', y en cada paso se desplaza a la ciudad
    no visitada más cercana. Continúa hasta visitar todas las ciudades,
    y luego regresa a la ciudad inicial.

    Parámetros:
        matriz_dist: matriz de distancias entre las ciudades.
        inicio: índice de la ciudad inicial (entero).

    Retorna:
        ruta: lista con el orden de visita de las ciudades (incluyendo el retorno).
        costo_total: costo total de la ruta.
    """
    n = len(matriz_dist)
    visitadas = [False]*n
    actual = inicio
    visitadas[actual] = True
    ruta = [actual]
    costo_total = 0

    # Visitar el resto de las ciudades
    for _ in range(n-1):
        prox_ciudad = None
        mejor_dist = float('inf')
        # Buscar la ciudad no visitada más cercana
        for j in range(n):
            if not visitadas[j] and matriz_dist[actual][j] < mejor_dist:
                mejor_dist = matriz_dist[actual][j]
                prox_ciudad = j
        visitadas[prox_ciudad] = True
        ruta.append(prox_ciudad)
        costo_total += mejor_dist
        actual = prox_ciudad

    # Regresar a la ciudad inicial
    costo_total += matriz_dist[actual][inicio]
    ruta.append(inicio)
    return ruta, costo_total

#===========================================================
# Función para leer coordenadas desde un archivo txt
#===========================================================
def leer_coords_txt(ruta_archivo):
    """
    Lee un archivo de texto que contiene en cada línea:
    id_ciudad x y

    Ignora líneas que no cumplan este formato.

    Parámetros:
        ruta_archivo: ruta del archivo .txt

    Retorna:
        coords: lista de tuplas (id_ciudad, x, y)
    """
    coords = []
    with open(ruta_archivo, 'r') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split()

            # Se necesitan exactamente 3 partes para (id_ciudad, x, y)
            if len(partes) != 3:
                # Línea no válida, probablemente encabezado u otra cosa
                continue

            # Intentar convertir los datos
            try:
                id_ciudad = int(partes[0])
                x = float(partes[1])
                y = float(partes[2])
                coords.append((id_ciudad, x, y))
            except ValueError:
                # Si no se puede convertir, ignorar la línea
                continue
    return coords




#===========================================================
# Función: plot_ruta
#===========================================================
def plot_ruta(coords, ruta, titulo="Ruta TSP"):
    """
    Grafica la ruta del TSP utilizando matplotlib.

    Parámetros:
        coords: lista de tuplas (id_ciudad, x, y).
        ruta: lista con el orden de visita de las ciudades (incluyendo el retorno).
        titulo: título del gráfico (cadena de texto).
    """
    # Extraer las coordenadas en el orden de la ruta
    x = [coords[ciudad][1] for ciudad in ruta]
    y = [coords[ciudad][2] for ciudad in ruta]

    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'o-', color='blue', label='Ruta')

    # Anotar cada ciudad con su ID
    for ciudad in ruta:
        plt.text(coords[ciudad][1], coords[ciudad][2], str(coords[ciudad][0]),
                 fontsize=9, ha='right')

    plt.title(titulo)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend()
    plt.grid(True)
    plt.show()

#===========================================================
# Función: vecino_mas_cercano_prob
#===========================================================

def vecino_mas_cercano_prob(matriz_dist, inicio=0, top_k=2):
    """
    Vecinos más cercanos con probabilidades.
    Selecciona el siguiente vecino no solo por distancia, sino también por probabilidad,
    considerando solo los 'top_k' vecinos más cercanos.

    Parámetros:
        matriz_dist: Matriz de distancias entre las ciudades (2D list o numpy array).
        inicio: Índice de la ciudad inicial (entero).
        top_k: Número de vecinos más cercanos a considerar para la selección (entero).
    """
    n = len(matriz_dist)
    visitadas = [False] * n
    actual = inicio
    visitadas[actual] = True
    ruta = [actual]
    costo_total = 0

    for _ in range(n - 1):

        distancias = [(j, matriz_dist[actual][j]) for j in range(n) if not visitadas[j]]

        distancias.sort(key=lambda x: x[1])
        candidatos = distancias[:top_k]


        indices, dists = zip(*candidatos)

        total_dist = sum(dists)
        if total_dist == 0:
            probabilidades = [1 / len(candidatos)] * len(candidatos)
        else:
            probabilidades = [1 / dist if dist > 0 else 0 for dist in dists]
            total_prob = sum(probabilidades)
            probabilidades = [p / total_prob for p in probabilidades]

        siguiente = np.random.choice(indices, p=probabilidades)

        visitadas[siguiente] = True
        ruta.append(siguiente)
        costo_total += matriz_dist[actual][siguiente]
        actual = siguiente

    costo_total += matriz_dist[actual][inicio]
    ruta.append(inicio)
    return ruta, costo_total

#===========================================================
# Función: colonia_hormigas
#===========================================================

def colonia_hormigas(matriz_dist, n_ants=10, n_iterations=10, rho=0.05, inicio = None):
    """
    Algoritmo de colonia de hormigas para el TSP.

    Resuelve el problema con el método de colonia de hormigas, dejando feromonas (recompensas) en los nodos prometedores.

    Parámetros:
        matriz_dist: matriz de distancias entre las ciudades.
        n_ants: número de hormigas (entero).
        n_iterations: número de iteraciones (entero).
    """
    n = len(matriz_dist)
    pheromone = np.ones((n, n))
    best_cost = float('inf')
    best_route = None

    for _ in range(n_iterations):
        rutas = []
        costos = []

        for _ in range(n_ants):
            inicio = random.randint(0, n - 1)
            ruta, costo = vecino_mas_cercano(matriz_dist, inicio)
            rutas.append(ruta)
            costos.append(costo)

        for i in range(n):
            for j in range(n):
                pheromone[i][j] *= (1 - rho)

        for ruta, costo in zip(rutas, costos):
            for i in range(len(ruta) - 1):
                pheromone[ruta[i]][ruta[i + 1]] += 1 / costo

        min_cost = min(costos)
        if min_cost < best_cost:
            best_cost = min_cost
            best_route = rutas[costos.index(min_cost)]

    return best_route, best_cost


#===========================================================
# Función: kruskal_mst
#===========================================================
def kruskal_mst(matriz_dist):
    """
    Arbol de expansion mínima de Kruskal para el TSP.

    Parámetros:
        matriz_dist: matriz de distancias entre las ciudades.
    """
    n = len(matriz_dist)
    edges = [(i, j, matriz_dist[i][j]) for i in range(n) for j in range(i + 1, n)]
    edges.sort(key=lambda x: x[2])

    parent = list(range(n))
    rank = [0] * n

    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])
        return parent[v]

    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:
            if rank[root_u] > rank[root_v]:
                parent[root_v] = root_u
            elif rank[root_u] < rank[root_v]:
                parent[root_u] = root_v
            else:
                parent[root_v] = root_u
                rank[root_u] += 1

    mst_cost = 0
    mst_edges = []

    for u, v, cost in edges:
        if find(u) != find(v):
            union(u, v)
            mst_cost += cost
            mst_edges.append((u, v))

    return mst_cost, mst_edges

#===========================================================
# Función: two_opt
#===========================================================
def two_opt(route, matriz_dist, inicio = None):
    """
    """
    def swap(route, i, k):
        return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

    n = len(route)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 2):
            for k in range(i + 1, n - 1):
                new_route = swap(route, i, k)
                if calcula_costo(new_route, matriz_dist) < calcula_costo(route, matriz_dist):
                    route = new_route
                    improved = True

    return route

#===========================================================
# Función: calcula_costo
#===========================================================
def calcula_costo(route, matriz_dis):
    """
    Calculate the cost of a TSP route.
    """
    return sum(matriz_dist[route[i]][route[i + 1]] for i in range(len(route) - 1))

#===========================================================
# Función: test_efectividad
#===========================================================
def test_efectividad(coords):
    matriz_dist = calcular_matriz_dist(coords)
    mst_cost,_ = kruskal_mst(matriz_dist)
    algorithms = {
        'NNH': vecino_mas_cercano,
        'PNNH': vecino_mas_cercano_prob,
        'HC': colonia_hormigas,
    }

    results = {}

    start_list = np.random.randint(0, len(coords) - 1, size=10)
    start_list = list(start_list)

    for name, algo in algorithms.items():
        total_cost = 0
        costs = []
        for i in range(10):
            start = start_list[i]
            route, cost = algo(matriz_dist, inicio=start)
            costs.append(costs)
            #optimized_route = two_opt(route, matriz_dist)
            #optimized_cost = calculate_cost(optimized_route, matriz_dist)
            total_cost += cost

        min_route = pd.Series(costs).idxmin()
        optimized_route = two_opt(route, matriz_dist)
        optimized_cost = calcula_costo(optimized_route, matriz_dist)

        avg_cost = total_cost / 10
        results[name] = {
            'Costo promedio': avg_cost,
            'Tasa vs arbol expansión minima': avg_cost / mst_cost,
            'Costo 2-opt': optimized_cost,
        }

    return results, mst_cost

#===========================================================
# Función: test_tiempo_distintas_ciudades
#===========================================================
def test_tiempo_distintas_ciudades(coords):
    matriz_dist = calcular_matriz_dist(coords)

    algorithms = {
        'NNH': vecino_mas_cercano,
        'PNNH': vecino_mas_cercano_prob,
        'HC': colonia_hormigas,
    }

    results = {}

    start_list = np.random.randint(0, len(coords) - 1, size=60)
    start_list = list(start_list)

    for name, algo in algorithms.items():
        tiempos = []
        for i in range(60):
            tiempo0 = time.time()
            start = start_list[i]
            _, _ = algo(matriz_dist, inicio=start)
            tiempo1 = time.time()
            tiempos.append(tiempo1 - tiempo0)

        results[name] = {
            'Tiempo promedio': np.mean(tiempos),
            'Varianza en tiempo': np.var(tiempos)
        }

    return results

#===========================================================
# Programa principal de ejemplo
#===========================================================
if __name__ == "__main__":
    resultados_tiempo = []
    for _ in range(3):
        # Nombre del archivo con las coordenadas
        print(f"\nProcesando archivo número {_ + 1}")
        if _ == 0:
            archivo = "Qatar.txt"
            pais = "Qatar"
        elif _ == 1:
            archivo = "Uruguay.txt"
            pais = "Uruguay"
        elif _ == 2:
            archivo = "Zimbabwe.txt"
            pais = "Zimbabwe"

        # Leer coordenadas
        coords = leer_coords_txt(archivo)
        results = test_tiempo_distintas_ciudades(coords)
        df = pd.DataFrame.from_dict(results, orient='index')
        df['Pais'] = pais

        resultados_tiempo.append(df)

        if not coords:
            print(f"No se pudieron leer las coordenadas del archivo {archivo}.")
            continue

        res, mst_cost = test_efectividad(coords)

        df = pd.DataFrame.from_dict(res, orient='index')
        df['Tasa OPT-2 vs AEM'] = df['Costo 2-opt'] / mst_cost

        df

        # Calcular matriz de distancias
        matriz_dist = calcular_matriz_dist(coords)

        # Heurística del vecino más cercano
        tiempo0 = time.time()
        ruta_vc, costo_vc = vecino_mas_cercano(matriz_dist, inicio=0)
        tiempof = time.time()
        print(f"\nResultados para {archivo}:")
        print("Ruta (Vecino más cercano):", ruta_vc)
        print("Costo total (Vecino más cercano):", costo_vc)
        print("Tiempo (Vecino más cercano): {:.4f} segundos".format(tiempof - tiempo0))

        # Graficar la ruta obtenida por la heurística del vecino más cercano
        plot_ruta(coords, ruta_vc, titulo=f"Ruta (Vecino más cercano) - {archivo}")

        # Heurística del vecino más cercano
        tiempo0 = time.time()
        ruta_vc, costo_vc = vecino_mas_cercano_prob(matriz_dist, inicio=0)
        tiempof = time.time()
        print(f"\nResultados para {archivo}:")
        print("Ruta (Vecino más cercano con probabilidad):", ruta_vc)
        print("Costo total (Vecino más cercano con probabilidad):", costo_vc)
        print("Tiempo (Vecino más cercano con probabilidad): {:.4f} segundos".format(tiempof - tiempo0))

        # Graficar la ruta obtenida por la heurística del vecino más cercano
        plot_ruta(coords, ruta_vc, titulo=f"Ruta (Vecino más cercano con probabilidad) - {archivo}")

        # Heurística del vecino más cercano
        tiempo0 = time.time()
        ruta_vc, costo_vc = colonia_hormigas(matriz_dist, inicio=0)
        tiempof = time.time()
        print(f"\nResultados para {archivo}:")
        print("Ruta (Hormiguero):", ruta_vc)
        print("Costo total (Hormiguero):", costo_vc)
        print("Tiempo (Hormiguero): {:.4f} segundos".format(tiempof - tiempo0))

        # Graficar la ruta obtenida por la heurística del vecino más cercano
        plot_ruta(coords, ruta_vc, titulo=f"Ruta (Hormiguero) - {archivo}")