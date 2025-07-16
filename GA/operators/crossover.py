import numpy as np
from copy import deepcopy
from ..utils.export import *

def crossover_one_point(pai1_bin, pai2_bin, taxa_crossover=1.0):
    """Crossover em um ponto aleatório"""
    if np.random.rand() > taxa_crossover:
        return deepcopy(pai1_bin), deepcopy(pai2_bin)
    
    size = len(pai1_bin)
    point = np.random.randint(1, size-1)
    filho1 = np.concatenate([pai1_bin[:point], pai2_bin[point:]])
    filho2 = np.concatenate([pai2_bin[:point], pai1_bin[point:]])
    return filho1, filho2

def crossover_two_point(pai1_bin, pai2_bin, taxa_crossover=1.0):
    """Crossover em dois pontos aleatórios"""
    if np.random.rand() > taxa_crossover:
        return deepcopy(pai1_bin), deepcopy(pai2_bin)
    
    size = len(pai1_bin)
    point1, point2 = sorted(np.random.choice(range(1, size), size=2, replace=False))
    filho1 = np.concatenate([pai1_bin[:point1], pai2_bin[point1:point2], pai1_bin[point2:]])
    filho2 = np.concatenate([pai2_bin[:point1], pai1_bin[point1:point2], pai2_bin[point2:]])
    return filho1, filho2

def crossover_uniforme(pai1_bin, pai2_bin, taxa_crossover=1.0):
    """Crossover uniforme (máscara aleatória)"""
    if np.random.rand() > taxa_crossover:
        return deepcopy(pai1_bin), deepcopy(pai2_bin)
    
    size = len(pai1_bin)
    mask = np.random.randint(0, 2, size=size).astype(bool)
    filho1 = np.where(mask, pai1_bin, pai2_bin)
    filho2 = np.where(mask, pai2_bin, pai1_bin)
    return filho1, filho2

def crossover_binario(pai1_bin, pai2_bin, bits_por_elemento, tipo='one_point', taxa_crossover=1):
    """
    Versão modificada que respeita a estrutura de blocos de bits
    """
    if np.random.rand() > taxa_crossover:
        return deepcopy(pai1_bin), deepcopy(pai2_bin)
    
    # Garante que o tamanho é múltiplo de bits_por_elemento
    assert len(pai1_bin) % bits_por_elemento == 0, "Tamanho do pai1 não é múltiplo de bits_por_elemento"
    assert len(pai2_bin) % bits_por_elemento == 0, "Tamanho do pai2 não é múltiplo de bits_por_elemento"
    
    # Converte para matriz de blocos
    blocos_pai1 = pai1_bin.reshape(-1, bits_por_elemento)
    blocos_pai2 = pai2_bin.reshape(-1, bits_por_elemento)
    
    if tipo == 'one_point':
        point = np.random.randint(1, len(blocos_pai1)-1)
        filho1 = np.vstack([blocos_pai1[:point], blocos_pai2[point:]]) # [111,1] [222,2] => [111,2] [222,1]
        filho2 = np.vstack([blocos_pai2[:point], blocos_pai1[point:]])
    
    elif tipo == 'two_point':
        point1, point2 = sorted(np.random.choice(range(1, len(blocos_pai1)), size=2, replace=False))
        filho1 = np.vstack([blocos_pai1[:point1], blocos_pai2[point1:point2], blocos_pai1[point2:]]) #[1,11,1] [2,22,2]
        filho2 = np.vstack([blocos_pai2[:point1], blocos_pai1[point1:point2], blocos_pai2[point2:]])
    
    elif tipo == 'uniforme':
        # Para cada bloco, decide qual pai usar
        mask = 0
        if len(blocos_pai1) > len(blocos_pai2):
            mask = np.random.randint(0, 2, size=len(blocos_pai2)).astype(bool)
        else:
            mask = np.random.randint(0, 2, size=len(blocos_pai1)).astype(bool)
        filho1 = np.vstack([blocos_pai1[i] if mask[i] else blocos_pai2[i] for i in range(len(mask))]) #[0,1,1,0,1]
        filho2 = np.vstack([blocos_pai2[i] if mask[i] else blocos_pai1[i] for i in range(len(mask))])
    
    # Retorna a forma linear
    return filho1.flatten(), filho2.flatten()

def crossover_completo(pais, evrp_data, n_filhos, num_rotas_min=3, 
                     tipo_crossover='one_point', taxa_crossover=0.8, estacao=False):
    """
    Executa o crossover completo controlando o número de filhos gerados.
    
    Args:
        pais: Lista de rotas pais (cada rota é um array numpy)
        evrp_data: Dicionário com dados do problema EVRP
        n_filhos: Número total de filhos a serem gerados
        num_rotas_min: Número mínimo de rotas exigido
        tipo_crossover: Tipo de crossover ('one_point', 'two_point', 'uniforme')
        taxa_crossover: Probabilidade de aplicar crossover (0 a 1)
        estacao: Se True, considera estações de recarga como nós válidos
    
    Returns:
        filhos_reparados: Lista com exatamente n_filhos rotas filhas válidas
    """
    filhos_reparados = []
    n_pares = (n_filhos + 1) // 2  # Arredonda para cima
    
    # Garante que temos pais suficientes
    if len(pais) < 2:
        raise ValueError("Necessário pelo menos 2 pais para crossover")
    
    # Repete a lista de pais se necessário
    pais_ampliados = (pais * ((n_pares // len(pais)) + 1))[:n_pares*2]
    
    for i in range(0, min(len(pais_ampliados), n_pares*2), 2):
        if len(filhos_reparados) >= n_filhos:
            break
            
        pai1 = pais_ampliados[i]
        pai2 = pais_ampliados[i+1]
        
        # 1. Codifica para binário (calculando bits_por_elemento)
        bits_cidade = max(5, (evrp_data['DIMENSION']).bit_length())
        bits_deposito = 1
        bits_por_elemento = bits_cidade + bits_deposito
        
        pai1_bin = codificar_rota_binaria(pai1, evrp_data,bits_cidade)
        pai2_bin = codificar_rota_binaria(pai2, evrp_data,bits_cidade)
        
        # 2. Aplica crossover com controle de blocos
        filho1_bin, filho2_bin = crossover_binario(
            pai1_bin, pai2_bin,
            bits_por_elemento=bits_por_elemento,
            tipo=tipo_crossover,
            taxa_crossover=taxa_crossover
        )
        
        # 3. Decodifica
        filho1 = decodificar_rota_binaria(filho1_bin, evrp_data,bits_cidade)
        filho2 = decodificar_rota_binaria(filho2_bin, evrp_data,bits_cidade)
        
        # 4. Repara
        filho1 = reparar_filho(filho1, pai1, evrp_data, num_rotas_min, estacao)
        filho2 = reparar_filho(filho2, pai2, evrp_data, num_rotas_min, estacao)
        
        # 5. Valida e adiciona
        for filho in [filho1, filho2]:
            if len(filhos_reparados) < n_filhos:
                if not validar_rota(filho, evrp_data, num_rotas_min, estacao):
                    print("Filho inválido após reparo! Gerando novo...")
                    continue
                filhos_reparados.append(filho)
    
    # Se não gerou filhos suficientes, completa com cópias dos pais
    while len(filhos_reparados) < n_filhos:
        filhos_reparados.append(deepcopy(random.choice(pais)))
    
    return filhos_reparados[:n_filhos]  # Garante o número exato