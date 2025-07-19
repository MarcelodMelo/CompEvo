import numpy as np
import random
from ..utils.export import *
from copy import deepcopy

def crossover_rotas(pai1, pai2, tipo='one_point', taxa_crossover=1):
    if random.random() > taxa_crossover:
        return deepcopy(pai1), deepcopy(pai2)
    
    # Remove depósitos duplicados internos
    pai1_clean = [pai1[0]] + [node for node in pai1[1:-1] if node != 1] + [pai1[-1]]
    pai2_clean = [pai2[0]] + [node for node in pai2[1:-1] if node != 1] + [pai2[-1]]
    
    if tipo == 'one_point':
        point = random.randint(1, min(len(pai1_clean), len(pai2_clean))-2)
        filho1 = pai1_clean[:point] + pai2_clean[point:-1] + [1]
        filho2 = pai2_clean[:point] + pai1_clean[point:-1] + [1]
    
    elif tipo == 'two_point':
        indices = list(range(1, len(pai1_clean)-1))
        if len(indices) >= 2:
            point1, point2 = sorted(random.sample(indices, k=2))
            filho1 = pai1_clean[:point1] + pai2_clean[point1:point2] + pai1_clean[point2:-1] + [1]
            filho2 = pai2_clean[:point1] + pai1_clean[point1:point2] + pai2_clean[point2:-1] + [1]
        else:
            filho1, filho2 = deepcopy(pai1_clean), deepcopy(pai2_clean)
    
    elif tipo == 'OX':
        indices = list(range(1, len(pai1_clean)-1))
        if len(indices) >= 2:
            point1, point2 = sorted(random.sample(indices, k=2))
            segment1 = pai1_clean[point1:point2]
            segment2 = pai2_clean[point1:point2]
            
            remaining1 = [node for node in pai2_clean[1:-1] if node not in segment1]
            remaining2 = [node for node in pai1_clean[1:-1] if node not in segment2]
            
            filho1 = [1] + remaining1[:point1] + segment1 + remaining1[point1:] + [1]
            filho2 = [1] + remaining2[:point1] + segment2 + remaining2[point1:] + [1]
        else:
            filho1, filho2 = deepcopy(pai1_clean), deepcopy(pai2_clean)
    
    else:  # uniforme
        filho1 = [1]
        filho2 = [1]
        for i in range(1, min(len(pai1_clean), len(pai2_clean))-1):
            if random.random() < 0.5:
                filho1.append(pai1_clean[i])
                filho2.append(pai2_clean[i])
            else:
                filho1.append(pai2_clean[i])
                filho2.append(pai1_clean[i])
        filho1.append(1)
        filho2.append(1)
    
    return np.array(filho1), np.array(filho2)

def crossover_completo(pais, evrp_data, n_filhos, num_rotas_min=3, tipo_crossover='one_point', taxa_crossover=0.8, estacao=False):
    """
    Executa crossover em população inteira, garantindo n_filhos válidos.
    """
    filhos_reparados = []
    n_pares = (n_filhos + 1) // 2
    
    for i in range(0, min(len(pais), n_pares*2), 2):
        if len(filhos_reparados) >= n_filhos:
            break
        
        pai1, pai2 = pais[i], pais[i+1]
        filho1, filho2 = crossover_rotas(pai1, pai2, tipo_crossover, taxa_crossover)
        
        # Repara os filhos
        filho1 = reparar_filho(filho1, pai1, evrp_data, num_rotas_min, estacao)
        filho2 = reparar_filho(filho2, pai2, evrp_data, num_rotas_min, estacao)
        
        filhos_reparados.extend([filho1, filho2])
    
    return filhos_reparados[:n_filhos]