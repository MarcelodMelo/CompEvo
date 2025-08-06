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

def avaliacao_com_penalidades(populacao, data):
    fitness = {}
    for rota in populacao:
        rota_tuple = tuple(rota)
        distancia_total = 0.0
        penalidade = 0
        
        # Verifica clientes não visitados
        clientes_visitados = set(node for node in rota if node not in data['STATIONS_COORD_SECTION'] and node != 1)
        clientes_faltantes = len([i for i in range(2, data['DIMENSION'] + 1) if i not in clientes_visitados])
        penalidade += 1000 * clientes_faltantes  # Penalidade alta por cliente faltante

        # Verifica bateria e carga
        carga_atual = data['CAPACITY']
        bateria_atual = data['ENERGY_CAPACITY']
        for i in range(len(rota) - 1):
            origem, destino = rota[i], rota[i+1]
            x1, y1 = data['NODE_COORD_SECTION'][origem]
            x2, y2 = data['NODE_COORD_SECTION'][destino]
            distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distancia_total += distancia
            
            # Atualiza bateria e carga
            if destino != 1 and destino not in data['STATIONS_COORD_SECTION']:
                carga_atual -= data['DEMAND_SECTION'][destino]
            bateria_atual -= data['ENERGY_CONSUMPTION'] * distancia
            
            # Penaliza se bateria/carga ficar negativa
            if carga_atual < 0:
                penalidade += 1000  # Penalidade por excesso de carga
            if bateria_atual < 0:
                penalidade += 1000  # Penalidade por bateria insuficiente
            
            # Recarrega se chegar a uma estação ou depósito
            if destino in data['STATIONS_COORD_SECTION'] + [1]:
                bateria_atual = data['ENERGY_CAPACITY']
        
        fitness[rota_tuple] = 1 / (distancia_total + penalidade + 1e-6)  # Evita divisão por zero
    
    return fitness

def avaliacao_distancia_restricoes(populacao, data):
    """
    Calcula fitness considerando distância + penalidades fictícias.
    - Restrições simuladas (sem implementação real ainda):
        - cada cliente é visitado exatamente uma vez por exatamente um VE; 
        - todos os VEs começam (carregados e com a bateria cheia) e terminam no depósito;
        - há uma quantidade mínima de rotas/veículos (V);
        - para cada rota de VE, a demanda total de clientes não excede a capacidade máxima de carga (C) do VE;
        - para cada rota de VE, o consumo total de energia não excede o nível máximo de carga da bateria (Q) do VE;
        - os VEs sempre saem do posto de recarga com a bateria totalmente carregada (observe que o depósito também é considerado um posto de recarga); e
        - os postos de recarga (incluindo o depósito) podem ser visitados várias vezes por qualquer VE.
    - Retorna: {rota_tuple: fitness}
    """
    """
    Restrições ja relacionadas no resto do codigo:
    - cada cliente é visitado exatamente uma vez por exatamente um VE (geração de rotas garante isso, e reparação de rotas por mutação/crossover tambem)
    - há uma quantidade mínima de rotas/veículos (V) (geração e reparação garantem isso)
    - todos os VEs começam (carregados e com a bateria cheia) e terminam no depósito; (a parte da carga eu faço aqui em baixo)
    """
    fitness = {}

    for rota in populacao:
        rota_tuple = tuple(int(node) for node in rota)
        rotas_individuais = [list(rota_tuple[i:j+1]) for i, j in zip([idx for idx, x in enumerate(rota_tuple) if x == 1][:-1], [idx for idx, x in enumerate(rota_tuple) if x == 1][1:])] #Divide as rotas por VE
        
        distancia_total = 0.0
        for rot in rotas_individuais:
            distancia_parcial = 0.0
            gasto_capacidade = 0
            consumo = 0

            for i in range(len(rot) - 1):
                x1, y1 = data['NODE_COORD_SECTION'][rot[i]]
                x2, y2 = data['NODE_COORD_SECTION'][rot[i + 1]]
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                #consumo += 
                distancia_parcial += dist

    #1.para cada rota de VE, a demanda total de clientes não excede a capacidade máxima de carga (C) do VE;
    #2. para cada rota de VE, o consumo total de energia não excede o nível máximo de carga da bateria (Q) do VE;
            for cliente in rot:
                gasto_capacidade += data['DEMAND_SECTION'][cliente]
                consumo
            if gasto_capacidade > data['CAPACITY']:
                print(f"Erro: capacidade elevada de {gasto_capacidade} na rota: {rot}")
                distancia_total += 800
    



        fitness[rota_tuple] = 1 / (distancia_total + 1e-6)  # +1e-6 evita divisão por zero
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

