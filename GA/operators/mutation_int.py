import numpy as np
import random
from copy import deepcopy
from ..utils.export import *

def mutacao_swap(filho, taxa_mutacao=0.1):
    """Troca duas posições não-depósito."""
    if random.random() > taxa_mutacao or len(filho) < 3:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    idx1, idx2 = random.sample([i for i in range(1, len(mutado)-1) if mutado[i] != 1], 2)
    mutado[idx1], mutado[idx2] = mutado[idx2], mutado[idx1]
    return mutado

def mutacao_inversao(filho, taxa_mutacao=0.1):
    """Inverte uma subsequência."""
    if random.random() > taxa_mutacao or len(filho) < 4:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    start, end = sorted(random.sample(range(1, len(mutado)-1), 2))
    mutado[start:end+1] = mutado[start:end+1][::-1]
    return mutado

def mutacao_scramble(filho, taxa_mutacao=0.1):
    """Embaralha uma subsequência."""
    if random.random() > taxa_mutacao or len(filho) < 4:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    start, end = sorted(random.sample(range(1, len(mutado)-1), 2))
    subsequence = mutado[start:end+1]
    random.shuffle(subsequence)
    mutado[start:end+1] = subsequence
    return mutado

def mutacao_insercao(filho, taxa_mutacao=0.1):
    """Move um nó para outra posição (compatível com numpy.ndarray)."""
    if random.random() > taxa_mutacao or len(filho) < 3:
        return deepcopy(filho)
    
    mutado = filho.copy()  # Cria uma cópia do array numpy
    
    # Encontra índices válidos (não depósito)
    indices_validos = [i for i in range(1, len(mutado)-1) if mutado[i] != 1]
    
    if not indices_validos:  # Se não há nós para mover
        return mutado
    
    idx = random.choice(indices_validos)
    node = mutado[idx]
    
    # Remove o nó da posição original (numpy não tem pop, fazemos manualmente)
    mutado = np.concatenate([mutado[:idx], mutado[idx+1:]])
    
    # Escolhe nova posição (ajustada porque o array agora é menor)
    new_pos = random.choice([i for i in range(1, len(mutado)) if i != idx])
    
    # Insere o nó na nova posição
    mutado = np.insert(mutado, new_pos, node)
    
    return mutado

def aplicar_mutacao(filhos, evrp_data, num_rotas_min=3, metodo='swap', taxa_mutacao=0.1, estacao=False):
    """
    Aplica mutação e repara os filhos.
    """
    mutacoes = {
        'swap': mutacao_swap,
        'inversao': mutacao_inversao,
        'scramble': mutacao_scramble,
        'insercao': mutacao_insercao
    }
    
    filhos_mutados = []
    for filho in filhos:
        filho_mutado = mutacoes[metodo](filho, taxa_mutacao)
        filho_reparado = reparar_filho(filho_mutado, filho, evrp_data, num_rotas_min, estacao)
        filhos_mutados.append(filho_reparado)
    
    return filhos_mutados