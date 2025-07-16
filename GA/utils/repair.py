import numpy as np

def reparar_filho(filho, pai, evrp_data, num_rotas_min=3, estacao=False):
    """
    Corrige uma rota filho com base no pai para atender às restrições do EVRP.
    
    Args:
        filho: Rota filho a ser reparada (array numpy).
        pai: Rota pai usada como referência (array numpy).
        evrp_data: Dicionário com dados do problema.
        num_rotas_min: Número mínimo de rotas exigido.
        estacao: Se True, inclui estações de recarga como nós válidos.
    
    Returns:
        Rota filho reparada (array numpy).
    """
    # Converte para lista para facilitar manipulação
    filho_list = filho.tolist()
    pai_list = pai.tolist()
    
    # 1. Garante que começa e termina com 1
    if filho_list[0] != 1:
        filho_list.insert(0, 1)
    if filho_list[-1] != 1:
        filho_list.append(1)
    
    # 2. Remove 1s consecutivos (rotas vazias)
    i = 1
    while i < len(filho_list) - 1:
        if filho_list[i] == 1 and filho_list[i+1] == 1:
            filho_list.pop(i)
        else:
            i += 1
    
    # 3. Identifica elementos válidos e clientes faltantes
    dimension = evrp_data['DIMENSION']
    clientes_validos = set(range(2, dimension + 1))
    estacoes_validas = set(evrp_data['STATIONS_COORD_SECTION']) if estacao else set()
    elementos_validos = clientes_validos.union(estacoes_validas)
    
    # 4. Remove clientes inválidos (0, IDs maiores que DIMENSION)
    clientes_presentes = []
    for node in filho_list[1:-1]:  # Ignora o primeiro e último 1
        if node in elementos_validos:
            clientes_presentes.append(node)
    
    # 5. Remove duplicatas mantendo a ordem de primeira ocorrência
    clientes_unicos = []
    seen = set()
    for node in clientes_presentes:
        if node not in seen:
            seen.add(node)
            clientes_unicos.append(node)
    
    # 6. Completa com clientes faltantes do pai (se necessário)
    if not estacao:  # Só aplica se não estiver usando estações
        clientes_faltantes = list(clientes_validos - set(clientes_unicos))
        # Adiciona clientes faltantes do pai que não estão no filho
        for node in pai_list[1:-1]:
            if node in clientes_faltantes and node not in clientes_unicos:
                clientes_unicos.append(node)
                clientes_faltantes.remove(node)
    
    # 7. Reconstroi a rota com os clientes válidos
    # Divide em rotas baseado nos 1s do pai (estrutura herdada)
    rotas_pai = []
    current_route = []
    for node in pai_list[1:-1]:  # Ignora o primeiro e último 1
        if node == 1:
            if current_route:
                rotas_pai.append(current_route)
                current_route = []
        else:
            current_route.append(node)
    if current_route:
        rotas_pai.append(current_route)
    
    # Distribui os clientes válidos nas rotas do pai
    filho_reparado = [1]
    clientes_alocados = 0
    
    for rota_pai in rotas_pai:
        if not clientes_unicos:
            break
            
        # Pega os clientes necessários para esta rota
        num_clientes_rota = min(len(rota_pai), len(clientes_unicos) - clientes_alocados)
        rota_filho = clientes_unicos[clientes_alocados:clientes_alocados + num_clientes_rota]
        filho_reparado.extend(rota_filho)
        filho_reparado.append(1)
        clientes_alocados += num_clientes_rota
    
    # Adiciona clientes restantes (se houver) em novas rotas
    while clientes_alocados < len(clientes_unicos):
        num_restante = len(clientes_unicos) - clientes_alocados
        rota_filho = clientes_unicos[clientes_alocados:clientes_alocados + min(num_restante, 10)]  # Máx 10 clientes por rota
        filho_reparado.extend(rota_filho)
        filho_reparado.append(1)
        clientes_alocados += len(rota_filho)
    
    # 8. Garante número mínimo de rotas
    num_rotas = filho_reparado.count(1) - 1

    if num_rotas < num_rotas_min:
        # Divide a maior rota em duas para aumentar o número de rotas
        rotas = []
        current = []
        for node in filho_reparado:
            if node == 1:
                if current:
                    rotas.append(current)
                    current = []
            else:
                current.append(node)
        
        while len(rotas) < num_rotas_min and len(rotas) > 0:
            # Encontra a rota mais longa
            maior_rota_idx = max(range(len(rotas)), key=lambda i: len(rotas[i]))
            maior_rota = rotas[maior_rota_idx]
            
            if len(maior_rota) >= 2:
                # Divide no meio
                meio = len(maior_rota) // 2
                nova_rota1 = maior_rota[:meio]
                nova_rota2 = maior_rota[meio:]
                
                # Substitui a rota original pelas duas novas
                rotas.pop(maior_rota_idx)
                rotas.insert(maior_rota_idx, nova_rota1)
                rotas.insert(maior_rota_idx + 1, nova_rota2)
        
        # Reconstrói o filho
        filho_reparado = [1]
        for rota in rotas:
            filho_reparado.extend(rota)
            filho_reparado.append(1)
    # else:
    #     if num_rotas > 1:
    #         newFilhos = [ x for x in filho_reparado[1:-1] if x != 1]
    #         if newFilhos[0] != 1:
    #             newFilhos.insert(0, 1)
    #         if newFilhos[-1] != 1:
    #             newFilhos.append(1)
    #         filho_reparado = newFilhos

    
    return np.array(filho_reparado)