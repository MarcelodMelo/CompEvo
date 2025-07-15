import numpy as np

def selecao_roleta(populacao, fitness, n_pais):
    """
    Seleciona pais proporcionalmente ao seu fitness.
    
    Args:
        populacao: Lista de indivíduos (rotas).
        fitness: Dicionário {rota: valor_fitness}.
        n_pais: Número de pais a selecionar.
    
    Returns:
        Lista com os pais selecionados.
    """
    rotas = list(fitness.keys())
    valores_fitness = np.array([fitness[rota] for rota in rotas])
    probabilidades = valores_fitness / valores_fitness.sum()
    
    # Seleciona índices ao invés de rotas diretamente
    indices_selecionados = np.random.choice(
        len(rotas), 
        size=n_pais, 
        p=probabilidades,
        replace=True
    )
    
    return [populacao[i] for i in indices_selecionados]

def selecao_torneio(populacao, fitness, n_pais, tamanho_torneio=2):
    """
    Seleciona pais através de torneios entre indivíduos aleatórios.
    
    Args:
        tamanho_torneio: Número de indivíduos que competem em cada torneio.
    """
    pais_selecionados = []
    indices = list(range(len(populacao)))  # Trabalhamos com índices
    
    for _ in range(n_pais):
        # Seleciona índices dos competidores
        competidores_idx = np.random.choice(indices, size=tamanho_torneio, replace=False)
        
        # Encontra o vencedor pelo fitness máximo
        vencedor_idx = max(competidores_idx, key=lambda i: fitness[tuple(populacao[i])])
        pais_selecionados.append(populacao[vencedor_idx])
    
    return pais_selecionados

def selecao_rank(populacao, fitness, n_pais):
    """
    Seleciona pais baseado no ranking (não no valor absoluto do fitness).
    """
    # Ordena a população pelo fitness (do melhor para o pior)
    indices_ordenados = sorted(
        range(len(populacao)), 
        key=lambda i: fitness[tuple(populacao[i])], 
        reverse=True
    )
    
    pesos = np.arange(len(populacao), 0, -1)
    probabilidades = pesos / pesos.sum()
    
    indices_selecionados = np.random.choice(
        indices_ordenados,
        size=n_pais,
        p=probabilidades,
        replace=True
    )
    
    return [populacao[i] for i in indices_selecionados]

def selecao_elitismo(populacao, fitness, n_elite):
    """
    Seleciona os n_elite melhores indivíduos diretamente.
    """
    # Ordena pelo fitness (melhor primeiro)
    indices_ordenados = sorted(
        range(len(populacao)), 
        key=lambda i: fitness[tuple(populacao[i])], 
        reverse=True
    )
    return [populacao[i] for i in indices_ordenados[:n_elite]]

