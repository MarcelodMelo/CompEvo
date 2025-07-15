import math

def avaliacao_distancia_pura(populacao, data):
    """
    Calcula fitness como o inverso da distância total percorrida.
    - Quanto menor a distância, maior o fitness.
    - Retorna: {rota_tuple: fitness}
    """
    fitness = {}
    for rota in populacao:
        rota_tuple = tuple(int(node) for node in rota)
        distancia_total = 0.0
        for i in range(len(rota) - 1):
            x1, y1 = data['NODE_COORD_SECTION'][rota[i]]
            x2, y2 = data['NODE_COORD_SECTION'][rota[i + 1]]
            distancia_total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        fitness[rota_tuple] = 1 / (distancia_total + 1e-6)  # +1e-6 evita divisão por zero
    return fitness

def avaliacao_distancia_restricoes(populacao, data):
    """
    Calcula fitness considerando distância + penalidades fictícias.
    - Restrições simuladas (sem implementação real ainda):
      - Capacidade máxima (CAPACITY)
      - Bateria mínima (ENERGY_CAPACITY)
    - Retorna: {rota_tuple: fitness}
    """
    fitness = {}
    for rota in populacao:
        rota_tuple = tuple(int(node) for node in rota)
        distancia_total = 0.0
        penalidade = 0.0
        
        # Cálculo da distância
        for i in range(len(rota) - 1):
            x1, y1 = data['NODE_COORD_SECTION'][rota[i]]
            x2, y2 = data['NODE_COORD_SECTION'][rota[i + 1]]
            distancia_total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Penalidades fictícias (exemplo)
        if 'CAPACITY' in data:
            demanda_total = sum(data['DEMAND_SECTION'].get(node, 0) for node in rota)
            if demanda_total > data['CAPACITY']:
                penalidade += 1000  # Penalidade alta por excesso de carga
        
        fitness[rota_tuple] = 1 / (distancia_total + penalidade + 1e-6)
    return fitness

def avaliacao_rankeamento(populacao, data):
    """
    Calcula fitness baseado na posição no ranking de distâncias.
    - Rotas mais curtas têm fitness proporcional ao quadrado do ranking.
    - Retorna: {rota_tuple: fitness}
    """
    distancias = {}
    for rota in populacao:
        rota_tuple = tuple(int(node) for node in rota)
        distancia_total = 0.0
        for i in range(len(rota) - 1):
            x1, y1 = data['NODE_COORD_SECTION'][rota[i]]
            x2, y2 = data['NODE_COORD_SECTION'][rota[i + 1]]
            distancia_total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distancias[rota_tuple] = distancia_total
    
    # Ordena rotas pela distância (menor = melhor)
    rotas_ordenadas = sorted(distancias.keys(), key=lambda x: distancias[x])
    
    # Atribui fitness baseado no ranking (melhor rank = maior fitness)
    fitness = {}
    for rank, rota in enumerate(rotas_ordenadas):
        fitness[rota] = (len(rotas_ordenadas) - rank) ** 2  # Quadrado do ranking inverso
    
    # Normaliza para somar 1 (opcional)
    total = sum(fitness.values())
    if total > 0:
        fitness = {rota: val / total for rota, val in fitness.items()}
    
    return fitness

