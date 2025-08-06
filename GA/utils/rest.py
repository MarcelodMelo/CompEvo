import numpy as np
import math

def aplicar_restricao(rota, evrp_data, num_rotas_min=3):
    """
    Transforma uma rota em uma solução válida para o EVRP, aplicando todas as restrições:
    1. Todos os VEs começam e terminam no depósito.
    2. Número mínimo de rotas/veículos.
    3. Capacidade máxima de carga por VE.
    4. Nível máximo de bateria por VE.
    5. Recarga total em estações/depósito.
    6. Visitas únicas a clientes.
    
    Args:
        rota: Array numpy representando a rota (ex: [1, 24, 21, ..., 1]).
        evrp_data: Dicionário com os dados do problema.
        num_rotas_min: Número mínimo de rotas exigido.
    
    Returns:
        Rota válida (array numpy) com todas as restrições aplicadas.
    """
    # --- 0. Prepara a rota ---
    # Se a rota for uma lista contendo um array, pega o array
    if isinstance(rota, list) and len(rota) == 1 and isinstance(rota[0], np.ndarray):
        rota = rota[0]
    
    # --- 1. Pré-processamento: Divide a rota em sub-rotas por veículo ---
    rotas = []
    current_route = [1]  # Todas as rotas começam no depósito (1)
    
    for node in rota[1:]:  # Ignora o primeiro 1 (já adicionado)
        if node == 1 and len(current_route) > 1:  # Encontrou um novo depósito (fim da rota atual)
            current_route.append(1)
            rotas.append(current_route)
            current_route = [1]
        else:
            current_route.append(node)
    
    if len(current_route) > 1:  # Adiciona a última rota se não terminou com 1
        current_route.append(1)
        rotas.append(current_route)
    
    
    # --- 2. Garante o número mínimo de rotas ---
    while len(rotas) < num_rotas_min:
        if rotas:  # Se houver rotas para dividir
            maior_rota_idx = max(range(len(rotas)), key=lambda i: len(rotas[i]))
            maior_rota = rotas[maior_rota_idx]
            meio = len(maior_rota) // 2
            nova_rota1 = maior_rota[:meio] + [1]
            nova_rota2 = [1] + maior_rota[meio:]
            rotas[maior_rota_idx] = nova_rota1
            rotas.insert(maior_rota_idx + 1, nova_rota2)
        else:
            rotas = [[1, 1] for _ in range(num_rotas_min)]
            break
    
    # --- 3. Remove clientes duplicados (visita única) ---
    clientes_visitados = set()
    clientes_validos = set(range(2, evrp_data['DIMENSION'] + 1))
    
    for i in range(len(rotas)):
        rota = rotas[i]
        nova_rota = [1]
        for node in rota[1:-1]:  # Ignora os depósitos inicial/final
            if node in clientes_validos:
                if node not in clientes_visitados:
                    nova_rota.append(node)
                    clientes_visitados.add(node)
            else:  # Estação de recarga (pode ser repetida)
                nova_rota.append(node)
        nova_rota.append(1)
        rotas[i] = nova_rota
    
    # --- 4. Reconstrói a rota completa ---
    rota_final = []
    for rota in rotas:
        rota_final.extend(rota)

    # 5. Remove 1s consecutivos (rotas vazias)
    i = 1
    while i < len(rota_final) - 1:
        if rota_final[i] == 1 and rota_final[i+1] == 1:
            rota_final.pop(i)
        else:
            i += 1

    # --- 6. Aplica restrições de capacidade e bateria ---
    carga = [evrp_data['CAPACITY']]
    carga_atual = carga[-1]
    bateria = [evrp_data['ENERGY_CAPACITY']]
    atual = 1

    #print(f"Antes da bomba: {tuple(int(node) for node in rota_final)}")
    while atual < len(rota_final):
        #Define o atual como destino, e verifica se ele pode entrar
        # print(f"Sit: {tuple(int(node) for node in rota_final[:atual])}")
        origem = rota_final[atual-1]
        destino = rota_final[atual]
        x1, y1 = evrp_data['NODE_COORD_SECTION'][origem]
        x2, y2 = evrp_data['NODE_COORD_SECTION'][destino]
        distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        consumo = evrp_data['ENERGY_CONSUMPTION'] * distancia
        if destino not in evrp_data['STATIONS_COORD_SECTION']:
            carga_atual = carga[-1] - evrp_data['DEMAND_SECTION'][destino]
        bateria_atual = bateria[-1] - consumo

        #Se o destino não quebra restrições, passamos para o proximo, armazenando os valores de bateria e carga
        # print(f"Atual: {atual}, Destino: {rota_final[atual]}")
        # print(f"CAntes: {carga[-1]}, CDepois {carga_atual}")
        # print(f"BAntes: {bateria[-1]}, BDepois {bateria_atual}")
        # print(f"Tamanhos: A{atual}, C{len(carga)}, B{len(bateria)}")
        # print()
        if bateria_atual > 0 and carga_atual > 0:
            if rota_final[atual] == 1:
                bateria.append(evrp_data['ENERGY_CAPACITY'])
                carga.append(evrp_data['CAPACITY'])
            elif rota_final[atual] in evrp_data['STATIONS_COORD_SECTION']:
                bateria.append(evrp_data['ENERGY_CAPACITY'])
                carga.append(carga[-1])
            else:
                bateria.append(bateria_atual)
                carga.append(carga_atual)
            atual += 1

        elif bateria_atual < 0: #Se não tiver bateria, vai retrocedendo ate conseguir colocar a estação mais proxima
            estacao_encontrada = None
            while atual >= 0 and estacao_encontrada is None:
                # Ponto atual para procurar estação mais próxima
                ponto_atual = rota_final[atual-1]
                xp, yp = evrp_data['NODE_COORD_SECTION'][ponto_atual]
                
                # Encontra estação mais próxima deste ponto, e define o consumo ate ela
                estacoes = evrp_data['STATIONS_COORD_SECTION']
                if estacoes:
                    estacao_proxima = min(
                        estacoes,
                        key=lambda e: math.sqrt(
                            (xp - evrp_data['NODE_COORD_SECTION'][e][0])**2 +
                            (yp - evrp_data['NODE_COORD_SECTION'][e][1])**2
                        )
                    )
                    xe, ye = evrp_data['NODE_COORD_SECTION'][estacao_proxima]
                    distancia_e = math.sqrt((xe - xp)**2 + (ye - yp)**2)
                    consumo_e = evrp_data['ENERGY_CONSUMPTION'] * distancia_e

                    #Se não tem energia, retrocede um cliente e tenta denovo, caso contrario, achamos a estação
                    #print(f"BatNeg: {atual-1}, size: {len(bateria)}, ponto {ponto_atual}, est: {estacao_proxima}, last: {bateria[-1]}, gasto: {consumo_e}")
                    if bateria[atual-1] - consumo_e < 0:
                        atual -= 1
                    else:
                        estacao_encontrada = estacao_proxima
            if estacao_encontrada is None:
                print("Fudeu de maneiras que eu não sei explicar") #Como caralhos que uma rota que esta na porra do deposito não consegue ir para nenhum lugar sem gastar energia e loucura
            else: 
                bateria = bateria[:atual]
                carga = carga[:atual]

                rota_final.insert(atual, estacao_encontrada)
                bateria.append(evrp_data['ENERGY_CAPACITY'])
                carga.append(carga[-1])

                atual += 1
        else: #Carga atual negativada
            end_route = False
            x2, y2 = evrp_data['NODE_COORD_SECTION'][1]
            #print(f"{end_route} and {rota_final[atual-1]}")
            while not end_route and rota_final[atual-1]!=1:
                x1, y1 = evrp_data['NODE_COORD_SECTION'][rota_final[atual-1]]
                distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                consumo = evrp_data['ENERGY_CONSUMPTION'] * distancia
                bateria_atual = bateria[atual-1] - consumo
                if bateria_atual > 0:
                    end_route = True
                    bateria = bateria[:atual]
                    carga = carga[:atual]

                    rota_final.insert(atual, 1)
                    bateria.append(evrp_data['ENERGY_CAPACITY'])
                    carga.append(evrp_data['CAPACITY'])
                    atual +=1
                else:
                    atual -= 1
            if rota_final[atual] == 1:
                print("Vou me matar as 23:45")
    #print(f"Depois da bomba: {tuple(int(node) for node in rota_final)}")

    
    return np.array(rota_final)

# 1, 2, 25, 3, 1, 11, 18, 20, 30, 1