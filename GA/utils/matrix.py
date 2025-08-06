import numpy as np
import random
from copy import deepcopy
import math

def calcular_matriz_prioridade(evrp_data):
    """
    Calcula a matriz de prioridade baseada nas distâncias euclidianas entre os nós.
    Quanto menor a distância, maior a prioridade.
    
    Inclui TODOS os nós como índices de origem, mas apenas clientes como destinos prioritários.
    """
    node_coords = evrp_data['NODE_COORD_SECTION']
    dimension = evrp_data['DIMENSION']
    stations = evrp_data['STATIONS_COORD_SECTION']
    depot = 1
    
    # Identifica os nós de clientes (exclui depósito e estações)
    clientes = [i for i in range(2, dimension + 1) if i not in stations]
    
    # Inicializa a matriz de distâncias
    distancias = np.zeros((dimension + 1, dimension + 1))  # +1 porque os nós começam em 1
    
    # Calcula todas as distâncias
    for i in range(1, dimension + 1):
        for j in range(i + 1, dimension + 1):
            x1, y1 = node_coords[i]
            x2, y2 = node_coords[j]
            distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distancias[i][j] = distancia
            distancias[j][i] = distancia
    
    # Converte distâncias para prioridades
    matriz_prioridade = {}
    
    # Para TODOS os nós (depósito, clientes e estações)
    for i in range(1, dimension + 1):
        # Calcula prioridades apenas para clientes (exclui o próprio nó e estações)
        destinos_validos = [j for j in clientes if j != i]
        
        if not destinos_validos:
            # Caso não haja clientes válidos (ex.: matriz para uma estação isolada)
            matriz_prioridade[i] = {'nodes': [], 'probs': []}
            continue
        
        # Pares (nó, distância) para destinos válidos
        dists = [(j, distancias[i][j]) for j in destinos_validos]
        dists.sort(key=lambda x: x[1])  # Ordena por distância
        
        # Probabilidades (inverso da distância)
        pesos = [1/(d + 1e-6) for _, d in dists]  # +1e-6 evita divisão por zero
        total = sum(pesos)
        probabilidades = [p/total for p in pesos]
        
        matriz_prioridade[i] = {
            'nodes': [node for node, _ in dists],
            'probs': probabilidades
        }
    
    return matriz_prioridade


def escolher_por_prioridade(node, matriz_prioridade):
    """
    Escolhe um nó cliente baseado na matriz de prioridade.
    Se não houver clientes disponíveis, retorna None.
    """
    if node not in matriz_prioridade:
        return None
    
    if not matriz_prioridade[node]['nodes']:
        return None
    
    # Roleta viciada
    r = random.random()
    cumulative_prob = 0.0
    for i, prob in enumerate(matriz_prioridade[node]['probs']):
        cumulative_prob += prob
        if r <= cumulative_prob:
            return matriz_prioridade[node]['nodes'][i]
    
    return matriz_prioridade[node]['nodes'][-1]