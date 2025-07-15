import numpy as np
import random
from copy import deepcopy
from ..utils.export import *

def mutacao_bit_flip(filho_bin, taxa_mutacao=0.1):
    """
    Aplica mutação por bit flip em um cromossomo binário.
    Args:
        filho_bin: Cromossomo binário (array numpy)
        taxa_mutacao: Probabilidade de cada bit sofrer flip
    Returns:
        Cromossomo mutado (array numpy)
    """
    mutado = deepcopy(filho_bin)
    for i in range(len(mutado)):
        if random.random() < taxa_mutacao:
            mutado[i] = 1 - mutado[i]  # Flip do bit
    return mutado

def mutacao_swap(filho, taxa_mutacao=0.1):
    """
    Aplica mutação por swap em uma rota.
    Args:
        filho: Rota (array numpy)
        taxa_mutacao: Probabilidade de ocorrer swap
    Returns:
        Rota mutada (array numpy)
    """
    if random.random() > taxa_mutacao or len(filho) < 3:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    idx1, idx2 = random.sample(range(1, len(mutado)-1), 2)  # Exclui primeiro e último (depósito)
    mutado[idx1], mutado[idx2] = mutado[idx2], mutado[idx1]
    return mutado

def mutacao_inversao(filho, taxa_mutacao=0.1):
    """
    Aplica mutação por inversão de subsequência.
    Args:
        filho: Rota (array numpy)
        taxa_mutacao: Probabilidade de ocorrer inversão
    Returns:
        Rota mutada (array numpy)
    """
    if random.random() > taxa_mutacao or len(filho) < 4:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    start, end = sorted(random.sample(range(1, len(mutado)-1), 2))  # Exclui depósitos
    mutado[start:end+1] = mutado[start:end+1][::-1]
    return mutado

def mutacao_scramble(filho, taxa_mutacao=0.1):
    """
    Aplica mutação por scramble (embaralhamento de subsequência).
    Args:
        filho: Rota (array numpy)
        taxa_mutacao: Probabilidade de ocorrer scramble
    Returns:
        Rota mutada (array numpy)
    """
    if random.random() > taxa_mutacao or len(filho) < 4:
        return deepcopy(filho)
    
    mutado = deepcopy(filho)
    start, end = sorted(random.sample(range(1, len(mutado)-1), 2))  # Exclui depósitos
    subsequence = mutado[start:end+1]
    random.shuffle(subsequence)
    mutado[start:end+1] = subsequence
    return mutado

def aplicar_mutacao(filhos, evrp_data, num_rotas_min=3, metodo='bit_flip', taxa_mutacao=0.1, estacao=False):
    """
    Aplica mutação em todos os filhos da população.
    Args:
        filhos: Lista de rotas filhas
        evrp_data: Dados do problema EVRP
        num_rotas_min: Número mínimo de rotas
        metodo: Método de mutação ('bit_flip', 'swap', 'inversao', 'scramble')
        taxa_mutacao: Probabilidade de mutação
        estacao: Se True, considera estações de recarga
    Returns:
        Lista de filhos mutados e reparados
    """
    filhos_mutados = []
    
    for filho in filhos:
        # Aplica mutação conforme o método escolhido
        if metodo == 'bit_flip':
            # Para mutação binária, codifica/decodifica
            filho_bin = codificar_rota_binaria(filho, evrp_data)
            filho_bin_mutado = mutacao_bit_flip(filho_bin, taxa_mutacao)
            filho_mutado = decodificar_rota_binaria(filho_bin_mutado, evrp_data)
        elif metodo == 'swap':
            filho_mutado = mutacao_swap(filho, taxa_mutacao)
        elif metodo == 'inversao':
            filho_mutado = mutacao_inversao(filho, taxa_mutacao)
        elif metodo == 'scramble':
            filho_mutado = mutacao_scramble(filho, taxa_mutacao)
        else:
            raise ValueError("Método de mutação inválido")
        
        # Repara o filho mutado usando ele mesmo como "pai" (para manter estrutura)
        filho_reparado = reparar_filho(filho_mutado, filho, evrp_data, num_rotas_min, estacao)
        
        #print(filho)
        # print(filho_reparado)
        # print('\n')
        # Verifica se a rota continua válida
        valido = validar_rota(filho_reparado, evrp_data, num_rotas_min, estacao)
        if not valido:
            # Se inválido mesmo após reparo, mantém o original
            print("Mutação gerou rota inválida, mantendo original")
            filho_reparado = deepcopy(filho)
        
        filhos_mutados.append(filho_reparado)
    
    return filhos_mutados