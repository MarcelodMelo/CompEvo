import numpy as np
import random
from copy import deepcopy
from ..utils.export import *

def crossover_nn(pai1, pai2, data, matriz_prioridade, num_rotas_min = 3):
    # 1. Extrai sub-rotas viáveis dos pais (já considera bateria/carga)
    subrotas_pai1 = extrair_subrotas_viáveis(pai1, data)
    subrotas_pai2 = extrair_subrotas_viáveis(pai2, data)
    
    # 2. Combina sub-rotas dos pais, priorizando as mais próximas do depósito
    filho = [1]  # Começa no depósito
    todas_subrotas = subrotas_pai1 + subrotas_pai2
    
    while todas_subrotas:
        # Usa a matriz de prioridade para escolher a sub-rota mais próxima do último ponto do filho
        último_ponto = filho[-1]
        
        # Pega os clientes iniciais de cada sub-rota disponível
        clientes_iniciais = [subrota[0] for subrota in todas_subrotas]
        
        # Escolhe o cliente mais próximo do último_ponto usando a matriz de prioridade
        try:
            cliente_mais_proximo = escolher_por_prioridade(último_ponto, matriz_prioridade)
            
            # Encontra a sub-rota que começa com esse cliente
            subrota_escolhida = None
            for subrota in todas_subrotas:
                if subrota[0] == cliente_mais_proximo:
                    subrota_escolhida = subrota
                    break
            
            # Se não encontrar, pega a sub-rota mais próxima manualmente
            if subrota_escolhida is None:
                distâncias = [
                    math.sqrt(
                        (data['NODE_COORD_SECTION'][último_ponto][0] - data['NODE_COORD_SECTION'][subrota[0]][0])**2 +
                        (data['NODE_COORD_SECTION'][último_ponto][1] - data['NODE_COORD_SECTION'][subrota[0]][1])**2
                    )
                    for subrota in todas_subrotas
                ]
                subrota_escolhida = todas_subrotas[np.argmin(distâncias)]
        
        except (ValueError, KeyError):
            # Fallback: escolhe aleatoriamente se houver erro na matriz
            subrota_escolhida = random.choice(todas_subrotas)
        
        # Adiciona a sub-rota ao filho
        filho.extend(subrota_escolhida)
        todas_subrotas.remove(subrota_escolhida)
        
        # Verifica se precisa inserir uma estação de recarga
        if len(filho) > 1:
            último_ponto = filho[-1]
            dist_ao_depósito = math.sqrt(
                (data['NODE_COORD_SECTION'][último_ponto][0] - data['NODE_COORD_SECTION'][1][0])**2 +
                (data['NODE_COORD_SECTION'][último_ponto][1] - data['NODE_COORD_SECTION'][1][1])**2
            )
            consumo = data['ENERGY_CONSUMPTION'] * dist_ao_depósito
            
            if consumo > data['ENERGY_CAPACITY'] * 0.8:  # Bateria crítica
                estações = data['STATIONS_COORD_SECTION'] + [1]
                estação_próxima = min(
                    estações,
                    key=lambda e: math.sqrt(
                        (data['NODE_COORD_SECTION'][último_ponto][0] - data['NODE_COORD_SECTION'][e][0])**2 +
                        (data['NODE_COORD_SECTION'][último_ponto][1] - data['NODE_COORD_SECTION'][e][1])**2
                    )
                )
                filho.append(estação_próxima)
    
    filho.append(1)  # Fecha a rota
    # Antes do return, verifica balanceamento
    if abs(len(subrotas_pai1) - len(subrotas_pai2)) > 2:  # Se houver desbalanceamento
        filho = aplicar_balanceamento_light(filho, data)  # Versão simplificada
    filho = reparar_filho(filho, pai1, data, num_rotas_min, estacao = True)
    return np.array(filho)

def aplicar_balanceamento_light(rota, data):
    subrotas = extrair_subrotas_viáveis(rota, data)
    if len(subrotas) < 2:
        return rota
    
    # Calcula médias
    avg_clientes = sum(len(s) for s in subrotas) / len(subrotas)
    
    # Transfere 1 cliente se diferença > 2
    for i in range(len(subrotas)):
        if len(subrotas[i]) > avg_clientes + 1:
            for j in range(len(subrotas)):
                if len(subrotas[j]) < avg_clientes - 1:
                    cliente = subrotas[i].pop()
                    subrotas[j].append(cliente)
                    break
    
    return reconstruir_rota(subrotas, data)

def extrair_subrotas_viáveis(rota, data):
    subrotas = []
    subrota_atual = []
    bateria = data['ENERGY_CAPACITY']
    carga = data['CAPACITY']
    
    for i in range(1, len(rota) - 1):
        nó = rota[i]
        próximo_nó = rota[i+1]
        
        # Calcula consumo
        dist = math.sqrt(
            (data['NODE_COORD_SECTION'][nó][0] - data['NODE_COORD_SECTION'][próximo_nó][0])**2 +
            (data['NODE_COORD_SECTION'][nó][1] - data['NODE_COORD_SECTION'][próximo_nó][1])**2
        )
        consumo = data['ENERGY_CONSUMPTION'] * dist
        
        # Verifica viabilidade
        if (bateria - consumo > 0) and (carga - data['DEMAND_SECTION'].get(próximo_nó, 0) > 0):
            subrota_atual.append(nó)
            bateria -= consumo
            carga -= data['DEMAND_SECTION'].get(próximo_nó, 0)
        else:
            if subrota_atual:
                subrotas.append(subrota_atual)
            subrota_atual = []
            bateria = data['ENERGY_CAPACITY']
            carga = data['CAPACITY']
    
    if subrota_atual:
        subrotas.append(subrota_atual)
    
    return subrotas


def crossover_balanceador(pai1, pai2, data, matriz_prioridade, num_rotas_min):
    """Transfere clientes entre rotas para melhorar o equilíbrio"""
    
    # 1. Extrai todas as sub-rotas viáveis dos pais
    subrotas_pai1 = extrair_subrotas_viáveis(pai1, data)
    subrotas_pai2 = extrair_subrotas_viáveis(pai2, data)
    
    # 2. Analisa desbalanceamento (rotas com muitos/poucos clientes)
    media_clientes = (len([n for n in pai1 if n not in data['STATIONS_COORD_SECTION'] and n != 1]) + 
                     len([n for n in pai2 if n not in data['STATIONS_COORD_SECTION'] and n != 1])) / (len(subrotas_pai1) + len(subrotas_pai2))
    
    # 3. Seleciona doadores (rotas com > média+1 clientes) e receptores
    doadores = [r for r in subrotas_pai1 + subrotas_pai2 if len(r) > media_clientes + 1]
    receptores = [r for r in subrotas_pai1 + subrotas_pai2 if len(r) < media_clientes]
    
    # 4. Processa transferências
    for doador in doadores:
        if not receptores:
            break
            
        # Escolhe o cliente mais distante do centroide da rota doadora
        cliente = selecionar_cliente_para_transferir(doador, data)
        
        # Encontra a melhor rota receptora
        receptor = min(
            receptores,
            key=lambda r: calcular_custo_insercao(cliente, r, data)
        )
        
        # Transfere se mantiver viabilidade
        if verificar_viabilidade_transferencia(cliente, doador, receptor, data):
            doador.remove(cliente)
            receptor.append(cliente)
            receptores.remove(receptor) if len(receptor) >= media_clientes else None
    
    # 5. Reconstrói os filhos
    filho1 = reconstruir_rota(subrotas_pai1, data)
    filho2 = reconstruir_rota(subrotas_pai2, data)
    filho1 = reparar_filho(filho1, pai1, data, num_rotas_min, estacao = True)
    filho2 = reparar_filho(filho2, pai2, data, num_rotas_min, estacao = True)
    return filho1, filho2

def selecionar_cliente_para_transferir(subrota, data):
    """Seleciona o cliente mais 'isolado' na sub-rota"""
    centroide = calcular_centroide(subrota, data)
    return max(
        subrota,
        key=lambda c: math.sqrt(
            (data['NODE_COORD_SECTION'][c][0] - centroide[0])**2 +
            (data['NODE_COORD_SECTION'][c][1] - centroide[1])**2
        )
    )
def calcular_centroide(subrota, data):
    """Calcula o ponto central (centroide) de uma sub-rota"""
    if not subrota:
        return (0, 0)
    
    soma_x = 0
    soma_y = 0
    for cliente in subrota:
        x, y = data['NODE_COORD_SECTION'][cliente]
        soma_x += x
        soma_y += y
    
    return (soma_x / len(subrota), (soma_y / len(subrota)))
    
def calcular_custo_insercao(cliente, subrota, data):
    """Calcula o melhor ponto de inserção"""
    if not subrota:
        return calcular_distancia([1, cliente, 1], data)
    
    custos = []
    for i in range(len(subrota)+1):
        nova_sub = subrota[:i] + [cliente] + subrota[i:]
        custos.append(calcular_distancia_subrota(nova_sub, data))
    return min(custos)

def verificar_viabilidade_transferencia(cliente, doador, receptor, data):
    """Verifica restrições de capacidade e bateria de forma robusta"""
    try:
        demanda = data['DEMAND_SECTION'].get(cliente, 0)
        
        # Verifica capacidade (ignora estações/depósito)
        carga_receptor = sum(data['DEMAND_SECTION'].get(c, 0) for c in receptor) + demanda
        if carga_receptor > data['CAPACITY']:
            return False
        
        # Verifica bateria (rota simulada: último ponto -> cliente -> depósito)
        if len(receptor) > 0:
            ultimo_ponto = receptor[-1]
        else:
            ultimo_ponto = 1  # Depósito
            
        dist1 = calcular_distancia([ultimo_ponto, cliente], data)
        dist2 = calcular_distancia([cliente, 1], data)
        consumo_total = data['ENERGY_CONSUMPTION'] * (dist1 + dist2)
        
        return consumo_total <= data['ENERGY_CAPACITY']
    
    except KeyError:
        return False

def avaliar_viabilidade_bateria(rota, data):
    """Verifica se uma rota é viável em termos de bateria"""
    bateria = data['ENERGY_CAPACITY']
    
    for i in range(len(rota)-1):
        origem = rota[i]
        destino = rota[i+1]
        distancia = calcular_distancia([origem, destino], data)
        consumo = data['ENERGY_CONSUMPTION'] * distancia
        
        # Verifica se chegou em estação ou depósito
        if destino in data['STATIONS_COORD_SECTION'] + [1]:
            bateria = data['ENERGY_CAPACITY']  # Recarrega
        else:
            bateria -= consumo
            if bateria < 0:
                return False
    
    return True

def reconstruir_rota(subrotas, data):
    """Reconstrói a rota completa com recargas"""
    rota = [1]
    bateria = data['ENERGY_CAPACITY']
    
    for sub in subrotas:
        for cliente in sub:
            distancia = calcular_distancia([rota[-1], cliente], data)
            if bateria - data['ENERGY_CONSUMPTION'] * distancia < 0:
                estacao = escolher_estacao_proxima(rota[-1], data)
                rota.append(estacao)
                bateria = data['ENERGY_CAPACITY']
            rota.append(cliente)
            bateria -= data['ENERGY_CONSUMPTION'] * distancia
    rota.append(1)
    return np.array(rota) 


###########
def mutacao_otimiza_rota(rota, data, matriz_prioridade, taxa_mutacao=0.3, num_rotas_min = 3):
    if random.random() > taxa_mutacao or len(rota) < 5:
        return rota.copy()
    
    rota_mutada = rota.copy()
    
    # 1. Extrai sub-rotas entre depósitos/estações
    subrotas = []
    subrota_atual = []
    for node in rota_mutada[1:-1]:  # Ignora o primeiro e último depósito
        if node == 1 or node in data['STATIONS_COORD_SECTION']:
            if subrota_atual:
                subrotas.append(subrota_atual)
                subrota_atual = []
        else:
            subrota_atual.append(node)
    if subrota_atual:
        subrotas.append(subrota_atual)
    
    # 2. Otimiza cada sub-rota
    for i in range(len(subrotas)):
        if len(subrotas[i]) > 2:
            subrotas[i] = aplicar_2opt(subrotas[i], data)
    
    # 3. Reconstrói a rota otimizada
    rota_otimizada = [1]
    bateria = data['ENERGY_CAPACITY']
    carga = data['CAPACITY']
    
    for subrota in subrotas:
        if not subrota:
            continue
            
        # Ordena usando matriz de prioridade
        subrota_ordenada = ordenar_por_prioridade(rota_otimizada[-1], subrota, matriz_prioridade, data)
        
        # Adiciona clientes verificando restrições
        for cliente in subrota_ordenada:
            distancia = calcular_distancia([rota_otimizada[-1], cliente], data)
            consumo = data['ENERGY_CONSUMPTION'] * distancia
            demanda = data['DEMAND_SECTION'][cliente]
            
            # Verifica se precisa recarregar antes
            if bateria - consumo < 0:
                estacao = escolher_estacao_proxima(rota_otimizada[-1], data)
                rota_otimizada.append(estacao)
                bateria = data['ENERGY_CAPACITY']
            
            # Verifica capacidade
            if carga - demanda < 0:
                rota_otimizada.append(1)  # Volta ao depósito
                carga = data['CAPACITY']
                bateria = data['ENERGY_CAPACITY']
            
            # Adiciona o cliente
            rota_otimizada.append(cliente)
            bateria -= consumo
            carga -= demanda
    
    rota_otimizada.append(1)
    rota_otimizada = aplicar_restricao(rota_otimizada, data, num_rotas_min)
    return np.array(rota_otimizada)

def aplicar_2opt(subrota, data):
    """Implementação completa do 2-opt para uma sub-rota"""
    melhor_subrota = subrota.copy()
    melhor_distancia = calcular_distancia_subrota(subrota, data)
    
    for i in range(1, len(subrota)-1):
        for j in range(i+1, len(subrota)):
            # Cria nova sub-rota invertendo o segmento i-j
            nova_subrota = subrota[:i] + subrota[i:j+1][::-1] + subrota[j+1:]
            nova_distancia = calcular_distancia_subrota(nova_subrota, data)
            
            if nova_distancia < melhor_distancia:
                melhor_subrota = nova_subrota
                melhor_distancia = nova_distancia
    
    return melhor_subrota

def precisa_recarregar(rota_parcial, data):
    """Verifica se é necessário recarregar considerando o trajeto até o depósito"""
    if len(rota_parcial) < 2:
        return False
    
    # Calcula consumo até o final da rota parcial
    consumo_total = 0
    for i in range(len(rota_parcial)-1):
        distancia = calcular_distancia([rota_parcial[i], rota_parcial[i+1]], data)
        consumo_total += data['ENERGY_CONSUMPTION'] * distancia
    
    # Calcula distância do último ponto até o depósito
    ultimo_ponto = rota_parcial[-1]
    distancia_deposito = calcular_distancia([ultimo_ponto, 1], data)
    consumo_total += data['ENERGY_CONSUMPTION'] * distancia_deposito
    
    return consumo_total > data['ENERGY_CAPACITY']

def calcular_distancia_subrota(subrota, data):
    """Calcula distância total de uma sub-rota"""
    distancia = 0
    for i in range(len(subrota)-1):
        distancia += calcular_distancia([subrota[i], subrota[i+1]], data)
    return distancia

def calcular_distancia(par_de_pontos, data):
    """Calcula distância entre dois pontos"""
    x1, y1 = data['NODE_COORD_SECTION'][par_de_pontos[0]]
    x2, y2 = data['NODE_COORD_SECTION'][par_de_pontos[1]]
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def escolher_estacao_proxima(ponto, data):
    """Encontra a estação de recarga mais próxima"""
    estações = data['STATIONS_COORD_SECTION']
    if not estações:
        return 1  # Retorna ao depósito se não houver estações
    
    return min(
        estações,
        key=lambda e: calcular_distancia([ponto, e], data)
    )

def ordenar_por_prioridade(ponto_inicial, clientes, matriz_prioridade, data):
    """Ordena clientes baseado na matriz de prioridade"""
    if ponto_inicial in matriz_prioridade:
        # Filtra clientes existentes na matriz
        clientes_validos = [c for c in clientes if c in matriz_prioridade[ponto_inicial]['nodes']]
        
        # Ordena pela prioridade (mais prováveis primeiro)
        clientes_validos.sort(
            key=lambda c: matriz_prioridade[ponto_inicial]['probs'][
                matriz_prioridade[ponto_inicial]['nodes'].index(c)
            ],
            reverse=True
        )
        return clientes_validos + [c for c in clientes if c not in clientes_validos]
    else:
        # Fallback: ordena por distância
        return sorted(
            clientes,
            key=lambda c: calcular_distancia([ponto_inicial, c], data)
        )
#####################################
def mutacao_nn(filho, data, matriz_prioridade, taxa_mutacao=0.1, num_rotas_min = 3):
    if random.random() > taxa_mutacao:
        return filho
    
    filho = filho.copy()
    bateria = data['ENERGY_CAPACITY']
    carga = data['CAPACITY']
    
    for i in range(1, len(filho) - 1):
        nó = filho[i]
        próximo_nó = filho[i+1]
        
        # Calcula consumo atual
        dist = math.sqrt(
            (data['NODE_COORD_SECTION'][nó][0] - data['NODE_COORD_SECTION'][próximo_nó][0])**2 +
            (data['NODE_COORD_SECTION'][nó][1] - data['NODE_COORD_SECTION'][próximo_nó][1])**2
        )
        consumo = data['ENERGY_CONSUMPTION'] * dist
        
        # Se a bateria ficar crítica, insere uma estação
        if (bateria - consumo) < data['ENERGY_CAPACITY'] * 0.4:  # 20% de bateria restante
            estações = data['STATIONS_COORD_SECTION'] + [1]
            estação_próxima = min(
                estações,
                key=lambda e: math.sqrt(
                    (data['NODE_COORD_SECTION'][nó][0] - data['NODE_COORD_SECTION'][e][0])**2 +
                    (data['NODE_COORD_SECTION'][nó][1] - data['NODE_COORD_SECTION'][e][1])**2
                )
            )
            filho = np.insert(filho, i+1, estação_próxima)
            bateria = data['ENERGY_CAPACITY']  # Recarrega
        
        # Troca com um cliente próximo (se viável)
        elif random.random() < 0.5:  # 50% de chance de tentar troca
            cliente_próximo = escolher_por_prioridade(nó, matriz_prioridade)
            idx_cliente = np.where(filho == cliente_próximo)[0]
            
            if len(idx_cliente) > 0:
                idx_cliente = idx_cliente[0]
                # Verifica se a troca é viável
                dist_troca = math.sqrt(
                    (data['NODE_COORD_SECTION'][nó][0] - data['NODE_COORD_SECTION'][cliente_próximo][0])**2 +
                    (data['NODE_COORD_SECTION'][nó][1] - data['NODE_COORD_SECTION'][cliente_próximo][1])**2
                )
                if (bateria - data['ENERGY_CONSUMPTION'] * dist_troca > 0):
                    filho[i], filho[idx_cliente] = filho[idx_cliente], filho[i]
        
        bateria -= consumo
    filho = aplicar_restricao(filho, data, num_rotas_min)
    return filho

# Métodos de mutação modificados para usar a matriz de prioridade
def mutacao_balanceamento_carga(rota, data, matriz_prioridade, taxa_mutacao=0.3, num_rotas_min = 3):
    if random.random() > taxa_mutacao or len(rota) < 5:
        return rota.copy()
    
    # 1. Extrai sub-rotas viáveis
    subrotas = extrair_subrotas_com_carga(rota, data)
    if len(subrotas) < 2:
        return rota
    
    # 2. Encontra candidatos a doador/receptor
    doador, receptor = encontrar_par_balanceamento(subrotas, data)
    if not doador or not receptor:
        return rota
    
    # 3. Encontra o melhor cliente para transferir
    cliente = selecionar_cliente_para_transfer(doador, receptor, data)
    if not cliente:
        return rota
    
    # 4. Realiza a transferência
    doador['clientes'].remove(cliente)
    receptor['clientes'].append(cliente)
    
    # 5. Reconstrói a rota
    return reconstruir_rota_com_estacoes([s['clientes'] for s in subrotas], data, num_rotas_min)

def extrair_subrotas_com_carga(rota, data):
    """Extrai sub-rotas com informações de carga"""
    subrotas = []
    subrota_atual = []
    carga_atual = 0
    
    for node in rota[1:-1]:  # Ignora depósitos inicial/final
        if node == 1 or node in data['STATIONS_COORD_SECTION']:
            if subrota_atual:
                subrotas.append({
                    'clientes': subrota_atual,
                    'carga': carga_atual,
                    'tamanho': len(subrota_atual)
                })
                subrota_atual = []
                carga_atual = 0
        else:
            subrota_atual.append(node)
            carga_atual += data['DEMAND_SECTION'].get(node, 0)
    
    if subrota_atual:
        subrotas.append({
            'clientes': subrota_atual,
            'carga': carga_atual,
            'tamanho': len(subrota_atual)
        })
    
    return subrotas

def encontrar_par_balanceamento(subrotas, data):
    """Seleciona doador e receptor baseado em fitness probabilístico"""
    if len(subrotas) < 2:
        return None, None
    
    # Calcula fitness para cada sub-rota (quanto maior, mais precisa doar)
    fitness = []
    capacidade = data['CAPACITY']
    
    for sub in subrotas:
        # Fator de sobrecarga (0 a 1)
        sobrecarga = min(sub['carga'] / capacidade, 1.0)
        
        # Fator de densidade (clientes/unidade de carga)
        densidade = sub['tamanho'] / (sub['carga'] + 1e-6)
        
        # Fitness final (quanto maior, melhor candidato a doador)
        fitness.append(sobrecarga * (1 - densidade))
    
    # Normaliza para probabilidades
    total_fitness = sum(fitness)
    if total_fitness < 1e-6:
        return None, None
    
    probabilidades = [f/total_fitness for f in fitness]
    
    # Seleciona doador com roleta viciada
    idx_doador = np.random.choice(len(subrotas), p=probabilidades)
    doador = subrotas[idx_doador]
    
    # Seleciona receptor inversamente proporcional ao fitness
    prob_receptor = [1-p for p in probabilidades]
    total_receptor = sum(prob_receptor)
    prob_receptor = [p/total_receptor for p in prob_receptor]
    
    idx_receptor = np.random.choice(len(subrotas), p=prob_receptor)
    receptor = subrotas[idx_receptor]
    
    # Verifica viabilidade mínima
    if (doador['tamanho'] <= 1 or 
        receptor['carga'] >= capacidade * 0.9 or
        doador == receptor):
        return None, None
    
    return doador, receptor

def selecionar_cliente_para_transfer(doador, receptor, data, alpha=1.0):
    """Seleciona cliente com probabilidade baseada na proximidade e viabilidade"""
    # 1. Calcula o centroide do receptor
    if not receptor['clientes']:
        centroide_receptor = data['NODE_COORD_SECTION'][1]  # Depósito
    else:
        centroide_receptor = calcular_centroide(receptor['clientes'], data)
    
    capacidade = data['CAPACITY']
    clientes_validos = []
    distancias = []
    
    # 2. Filtra clientes viáveis e calcula distâncias
    for cliente in doador['clientes']:
        demanda = data['DEMAND_SECTION'].get(cliente, 0)
        if receptor['carga'] + demanda <= capacidade:
            x, y = data['NODE_COORD_SECTION'][cliente]
            distancia = math.sqrt((x - centroide_receptor[0])**2 + 
                                (y - centroide_receptor[1])**2)
            clientes_validos.append(cliente)
            distancias.append(distancia)
    
    if not clientes_validos:
        return None
    
    # 3. Calcula probabilidades (roleta viciada)
    distancias = np.array(distancias)
    fitness = 1 / (distancias + 1e-6)  # Evita divisão por zero
    fitness = np.power(fitness, alpha)  # Controle de aleatoriedade
    
    # Normalização
    prob = fitness / fitness.sum()
    
    # 4. Seleção probabilística
    return np.random.choice(clientes_validos, p=prob)

def reconstruir_rota_com_estacoes(subrotas, data, num_rotas_min = 3):
    """Reconstrói a rota completa com estações de recarga"""
    rota = [1]
    bateria = data['ENERGY_CAPACITY']
    
    for sub in subrotas:
        for cliente in sub:
            distancia = calcular_distancia([rota[-1], cliente], data)
            consumo = data['ENERGY_CONSUMPTION'] * distancia
            
            if bateria - consumo < 0:
                estacao = escolher_estacao_proxima(rota[-1], data)
                rota.append(estacao)
                bateria = data['ENERGY_CAPACITY']
            
            rota.append(cliente)
            bateria -= consumo
    
    rota.append(1)
    rota = aplicar_restricao(rota, data, num_rotas_min)
    return np.array(rota)
# 17, 23, 30, 18, 16