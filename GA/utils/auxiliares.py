import random
import numpy as np
import math

#Cria uma rota aleatoria, baseado nos clientes e no numero de rotas
def criar_rotas_aleatorias(evrp_data, num_rotas_min, estacao=False):
    '''
    Estrutura da rota: Sempre começa e termina com 1 (depósito), podendo ter outros 1s internos representando múltiplas rotas
    Clientes: Valores de 2 até DIMENSION (nós clientes)
    Estações: Valores de STATIONS_COORD_SECTION (se estacao=True)
    Número mínimo de rotas: Controlado por num_rotas_min (quantidade de 1s internos)
    '''
    dimension = evrp_data['DIMENSION']
    clientes = list(range(2, dimension + 1))  # Todos os clientes (2 até DIMENSION)
    estacoes = evrp_data['STATIONS_COORD_SECTION'] if estacao else []
    
    elementos_disponiveis = clientes + estacoes
    random.shuffle(elementos_disponiveis)  # Embaralha clientes e estações (se aplicável)
    
    # Número total de rotas (pelo menos num_rotas_min, mas pode ter mais)
    num_rotas = random.randint(num_rotas_min, num_rotas_min + 3)  # Pode ter até 3 rotas extras
    
    # Divide os elementos em 'num_rotas' grupos
    rotas = []
    for i in range(num_rotas):
        # Divide os elementos aproximadamente igual entre as rotas
        elementos_rota = elementos_disponiveis[i::num_rotas]
        rotas.append(elementos_rota)
    
    # Constrói o array final intercalando com 1s (depósito)
    rota_final = [1]  # Começa no depósito
    for rota in rotas:
        rota_final.extend(rota)
        rota_final.append(1)  # Volta ao depósito após cada rota
    
    # Garante que não há 1s consecutivos (rotas vazias)
    i = 1
    while i < len(rota_final) - 1:
        if rota_final[i] == 1 and rota_final[i+1] == 1:
            # Remove o 1 duplicado
            rota_final.pop(i)
        else:
            i += 1
    
    return np.array(rota_final)

#Valida a rota, vendo se ela e uma rota aceita
def validar_rota(rota, evrp_data, num_rotas_min, estacao=False):
    '''
    Verificação de depósito: Confere se começa e termina com 1
    Número de rotas: Conta os 1s internos para verificar o mínimo exigido
    Elementos válidos: Checa se todos os elementos são clientes/estações permitidos
    Rotas vazias: Detecta 1s consecutivos que indicariam rotas sem clientes
    Clientes faltantes (opcional): Verifica se todos os clientes estão presentes (pode ser removido se for aceitável ter soluções parciais)
    '''
    dimension = evrp_data['DIMENSION']
    clientes_validos = set(range(2, dimension + 1))
    estacoes_validas = set(evrp_data['STATIONS_COORD_SECTION'])
    
    # Converter para array numpy se não for
    if not isinstance(rota, np.ndarray):
        rota = np.array(rota)
    
    # 1. Verifica se começa e termina no depósito
    if rota[0] != 1 or rota[-1] != 1:
        print("O array não começa/termina no depósito")
        return False
    
    # 2. Conta depósitos internos (número de rotas = depots_internos + 1)
    depots_internos = np.sum(rota[1:-1] == 1)
    
    # Verifica número mínimo de rotas
    if depots_internos + 1 < num_rotas_min:
        print(f"O array possui {depots_internos + 1} rotas, que é menor que o valor mínimo estabelecido ({num_rotas_min})")
        return False
    
    # 3. Verifica elementos inválidos
    elementos_permitidos = clientes_validos
    if estacao:
        elementos_permitidos = clientes_validos.union(estacoes_validas)
    
    elementos_unicos = set(np.unique(rota)) - {1}
    for elemento in elementos_unicos:
        if elemento not in elementos_permitidos:
            if elemento in estacoes_validas:
                print("Presença de estação não permitida")
                return False
            else:
                print(f"Cliente {elemento} não existe na lista")
                return False
    
    # 4. Verifica rotas vazias (1s consecutivos)
    if np.any(np.diff(np.where(rota == 1)[0]) == 1):
        print("Rota vazia encontrada (1s seguidos)")
        return False
    
    # 5. Verifica se todos os clientes estão presentes (opcional)
    if not estacao:
        clientes_presentes = elementos_unicos.intersection(clientes_validos)
        if len(clientes_presentes) != len(clientes_validos):
            clientes_faltantes = clientes_validos - clientes_presentes
            print(f"Clientes faltantes: {sorted(clientes_faltantes)}")
            return False
    
    return True

#Calcula a distancia total da rota
def calcular_distancia_total(data, rota):
    """
    Calcula a distância total percorrida em uma rota com múltiplos trajetos.
    
    Parâmetros:
    - data: dicionário contendo 'NODE_COORD_SECTION' com as coordenadas dos nós
    - rota: lista representando a rota completa com múltiplos trajetos (ex: [1,2,3,1,4,5,1])
    
    Retorna:
    - Distância total percorrida
    """
    coords = data['NODE_COORD_SECTION']
    distancia_total = 0.0
    
    for i in range(len(rota) - 1):
        node_atual = rota[i]
        node_proximo = rota[i+1]
        
        x1, y1 = coords[node_atual]
        x2, y2 = coords[node_proximo]
        
        distancia_total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    return distancia_total

#Codifica a rota
def codificar_rota_binaria(rota, evrp_data, bits_cidade=5, bits_deposito=1):
    """
    Codifica uma rota EVRP em representação binária
    
    Parâmetros:
    - rota: array numpy com a rota (começa/termina com 1)
    - evrp_data: dicionário com dados do problema
    - bits_cidade: número de bits para ID de clientes/estações
    - bits_deposito: número de bits para flag de depósito (default=1)
    
    Retorna:
    - Array numpy com representação binária
    """
    # Remove primeiro e último depósito
    rota_limpa = rota[1:-1]
    
    if len(rota_limpa) == 0:
        return np.array([], dtype=int)
    
    # Calcula bits necessários por elemento
    bits_por_elemento = bits_deposito + bits_cidade
    
    # Verifica capacidade de representação
    max_clientes = 2**bits_cidade - 1
    clientes_validos = set(range(2, evrp_data['DIMENSION'] + 1))
    
    if max(clientes_validos) > max_clientes:
        raise ValueError(f"bits_cidade={bits_cidade} insuficiente para {max(clientes_validos)} clientes")
    
    # Inicializa array binário
    codigo = np.zeros(len(rota_limpa) * bits_por_elemento, dtype=int)
    
    for i, elemento in enumerate(rota_limpa):
        pos = i * bits_por_elemento
        
        # Bit de depósito (próximo é depósito?)
        if i < len(rota_limpa) - 1 and rota_limpa[i+1] == 1:
            codigo[pos:pos+bits_deposito] = 1  # Ativa flag de depósito
        
        # Bits de identificação
        id_bin = [int(b) for b in bin(elemento)[2:].zfill(bits_cidade)]
        codigo[pos+bits_deposito:pos+bits_por_elemento] = id_bin
    
    # Força depósito após último elemento
    if rota_limpa[-1] != 1:
        ult_pos = (len(rota_limpa) - 1) * bits_por_elemento
        codigo[ult_pos:ult_pos+bits_deposito] = 1
    
    return codigo

#Decodifica a rota
def decodificar_rota_binaria(codigo_binario, evrp_data, bits_cidade=5, bits_deposito=1):
    """
    Decodifica uma rota binária de volta para o formato array de inteiros
    
    Parâmetros:
    - codigo_binario: array numpy com a representação binária
    - evrp_data: dicionário com dados do problema
    - bits_cidade: número de bits usados para ID de clientes/estações
    - bits_deposito: número de bits usados para flag de depósito
    
    Retorna:
    - Array numpy com a rota no formato [1, clientes, 1, clientes, ..., 1]
    """
    bits_por_elemento = bits_deposito + bits_cidade
    
    if len(codigo_binario) % bits_por_elemento != 0:
        raise ValueError("Tamanho do código incompatível com bits especificados")
    
    num_elementos = len(codigo_binario) // bits_por_elemento
    rota = [1]  # Inicia no depósito
    
    i = 0
    while i < num_elementos:
        inicio = i * bits_por_elemento
        fim = inicio + bits_por_elemento
        bloco = codigo_binario[inicio:fim]
        
        # Extrai flag de depósito
        flag_deposito = bloco[:bits_deposito]
        
        # Extrai ID (bits_cidade bits)
        id_bits = bloco[bits_deposito:bits_por_elemento]
        id_cliente = int(''.join(map(str, id_bits)), 2)
        
        # Verificação de ID válido
        if id_cliente == 1:  # Ignora depósitos codificados como cliente
            i += 1
            continue
            
        # clientes_validos = set(range(2, evrp_data['DIMENSION'] + 1))
        # estacoes_validas = set(evrp_data['STATIONS_COORD_SECTION'])
        
        # if id_cliente not in clientes_validos.union(estacoes_validas):
        #     print(f"ID {id_cliente} inválido")
        #     #raise ValueError(f"ID {id_cliente} inválido")
        # else:
        rota.append(id_cliente)
        
        # Adiciona depósito apenas se a flag estiver ativada
        if any(flag_deposito):
            rota.append(1)
        
        i += 1
    
    # Garante terminar com depósito
    if rota[-1] != 1:
        rota.append(1)
    
    return np.array(rota)

#Parametros de problema
def parametros_problema(evrp_data, binario, restricoes):
    #bits_cidade
    #bits_deposito
    #binarizacao
    #num_rotas_min
    #restricoes = Se e para ter Estações, e se e pra colocar restrição de Carga e Energia

    params_ervp = {}
    params_ervp['binario'] = binario
    params_ervp['restricoes'] = restricoes
    params_ervp['num_rotas_min'] = evrp_data['VEHICLES']
    params_ervp['bits_cidade'] = evrp_data['DIMENSION'].bit_length()
    if restricoes:
        params_ervp['bits_deposito'] = 1 + evrp_data['STATIONS'].bit_length()
    else:
        params_ervp['bits_deposito'] = 1
    return params_ervp

#Achar a melhor rota da população
def melhor_rota(populacao, data):
    """
    Encontra a melhor rota da população com base na distância total percorrida.
    
    Args:
        populacao: Lista de rotas (cada rota é um array numpy)
        data: Dicionário com os dados do problema EVRP
        
    Returns:
        tuple: (melhor_rota, distancia) onde:
            - melhor_rota: Array numpy com a rota
            - distancia: Float com a distância total da rota
    """
    melhor_dist = float('inf')
    melhor_rota = None
    
    for rota in populacao:
        # Calcula a distância total da rota atual
        dist_atual = calcular_distancia_total(data, rota)
        
        # Verifica se é a melhor encontrada até agora
        if dist_atual < melhor_dist:
            melhor_dist = dist_atual
            melhor_rota = rota
    
    return melhor_rota, melhor_dist

def gerar_log(evrp_data, historico_melhor_distancia, historico_melhor_rota, nome_arquivo='evrp_log.txt'):
    """
    Gera um arquivo de log com métricas detalhadas.
    
    Args:
        historico_melhor_distancia: Lista de melhores distâncias por geração.
        historico_melhor_rota: Lista de melhores rotas por geração.
        nome_arquivo: Nome do arquivo de log.
    """
    with open(nome_arquivo, 'w') as f:
        f.write(f"=== Log do EVRP - Instância {evrp_data.get('COMMENT', '')} ===\n")
        f.write(f"Clientes: {evrp_data['DIMENSION'] - 1}\n")
        f.write(f"Veículos mínimos: {evrp_data['VEHICLES']}\n\n")
        
        f.write("=== Histórico de Melhores Distâncias ===\n")
        for geracao, distancia in enumerate(historico_melhor_distancia):
            f.write(f"Geração {geracao}: {distancia:.2f}\n")
        
        f.write("\n=== Melhor Rota Encontrada ===\n")
        melhor_rota = historico_melhor_rota[-1]
        f.write(f"Distância: {historico_melhor_distancia[-1]:.2f}\n")
        f.write(f"Rota: {' -> '.join(map(str, melhor_rota))}\n")