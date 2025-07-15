import numpy as np
from copy import deepcopy

def substituicao_completa(filhos):
    """
    Substituição completa: toda a nova população é formada pelos filhos.
    Args:
        populacao_antiga: Lista de indivíduos da geração anterior
        filhos: Lista de filhos gerados
        fitness_antigo: Dicionário {rota: fitness} da geração anterior
        fitness_filhos: Dicionário {rota: fitness} dos filhos
    Returns:
        Nova população (lista de rotas)
    """
    return deepcopy(filhos)

def substituicao_elitismo(populacao_antiga, filhos, fitness_antigo, fitness_filhos, n_elite):
    """
    Substituição com elitismo: mantém os n_elite melhores da geração anterior.
    Args:
        n_elite: Número de melhores indivíduos a preservar
    """
    # Ordena a população antiga pelo fitness (melhores primeiro)
    elite = sorted(populacao_antiga, key=lambda x: fitness_antigo[tuple(x)], reverse=True)[:n_elite]
    
    # Seleciona os melhores filhos para completar a população
    n_filhos_needed = len(populacao_antiga) - n_elite
    filhos_sorted = sorted(filhos, key=lambda x: fitness_filhos[tuple(x)], reverse=True)
    
    nova_populacao = deepcopy(elite) + deepcopy(filhos_sorted[:n_filhos_needed])
    return nova_populacao

def substituicao_steady_state(populacao_antiga, filhos, fitness_antigo, fitness_filhos, n_substituir):
    """
    Substituição steady-state: substitui apenas os n_substituir piores indivíduos.
    Args:
        n_substituir: Número de piores indivíduos a substituir
    """
    # Ordena população antiga (melhores primeiro) e filhos (melhores primeiro)
    pop_ordenada = sorted(populacao_antiga, key=lambda x: fitness_antigo[tuple(x)], reverse=True)
    filhos_ordenados = sorted(filhos, key=lambda x: fitness_filhos[tuple(x)], reverse=True)
    
    # Mantém os (N - n_substituir) melhores da população antiga
    mantidos = pop_ordenada[:-n_substituir]
    
    # Adiciona os melhores filhos (até completar a população)
    nova_populacao = deepcopy(mantidos) + deepcopy(filhos_ordenados[:n_substituir])
    return nova_populacao

def gerar_nova_populacao(populacao_antiga, filhos, fitness_antigo, fitness_filhos, metodo='steady_state', 
                         n_pop=None, n_pais=None, n_filhos=None, n_elite=5):
    """
    Função principal que aplica a estratégia de substituição selecionada.
    Args:
        metodo: 'completa', 'elitismo' ou 'steady_state'
        n_pop: Tamanho da população (usado para steady-state)
        n_pais: Número de pais selecionados (usado para steady-state)
        n_filhos: Número de filhos gerados (usado para steady-state)
        n_elite: Número de elites a manter (para elitismo)
    Returns:
        Nova população (lista de rotas)
    """
    if metodo == 'completa':
        return substituicao_completa(filhos)
    
    elif metodo == 'elitismo':
        return substituicao_elitismo(populacao_antiga, filhos, fitness_antigo, fitness_filhos, n_elite)
    
    elif metodo == 'steady_state':
        # Calcula quantos indivíduos substituir baseado nos parâmetros
        n_substituir = min(len(filhos), len(populacao_antiga) - (n_pop - n_filhos))
        return substituicao_steady_state(populacao_antiga, filhos, fitness_antigo, fitness_filhos, n_substituir)
    
    else:
        raise ValueError("Método de substituição inválido")