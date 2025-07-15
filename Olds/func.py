import matplotlib.pyplot as plt
import random
import numpy as np
import math
#Le o arquivo EVRP, e armazena suas informações em um dicionario data
def read_evrp_file(file_path):
    data = {
        'COMMENT': '',
        'OPTIMAL_VALUE': 0,
        'VEHICLES': 0,
        'DIMENSION': 0,
        'STATIONS': 0,
        'CAPACITY': 0,
        'ENERGY_CAPACITY': 0,
        'ENERGY_CONSUMPTION': 0,
        'NODE_COORD_SECTION': {},
        'DEMAND_SECTION': {},
        'STATIONS_COORD_SECTION': [],
        'DEPOT_SECTION': None
    }
    
    current_section = None
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.startswith('COMMENT'):
                data['COMMENT'] = line.split(':', 1)[1].strip()
                current_section = None
            elif line.startswith('OPTIMAL_VALUE'):
                data['OPTIMAL_VALUE'] = float(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('VEHICLES'):
                data['VEHICLES'] = int(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('DIMENSION'):
                data['DIMENSION'] = int(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('STATIONS_COORD_SECTION'):
                current_section = 'STATIONS_COORD_SECTION'
            elif line.startswith('STATIONS'):
                data['STATIONS'] = int(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('CAPACITY'):
                data['CAPACITY'] = int(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('ENERGY_CAPACITY'):
                data['ENERGY_CAPACITY'] = float(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('ENERGY_CONSUMPTION'):
                data['ENERGY_CONSUMPTION'] = float(line.split(':', 1)[1].strip())
                current_section = None
            elif line.startswith('NODE_COORD_SECTION'):
                current_section = 'NODE_COORD_SECTION'
            elif line.startswith('DEMAND_SECTION'):
                current_section = 'DEMAND_SECTION'
            elif line.startswith('DEPOT_SECTION'):
                current_section = 'DEPOT_SECTION'
            elif line == 'EOF':
                break
            else:
                if current_section == 'NODE_COORD_SECTION':
                    parts = line.split()
                    node_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    data['NODE_COORD_SECTION'][node_id] = (x, y)
                elif current_section == 'DEMAND_SECTION':
                    parts = line.split()
                    node_id = int(parts[0])
                    demand = int(parts[1])
                    data['DEMAND_SECTION'][node_id] = demand
                elif current_section == 'STATIONS_COORD_SECTION':
                    if line.strip() and line != '-1':
                        station_id = int(line.strip())
                        data['STATIONS_COORD_SECTION'].append(station_id)
                elif current_section == 'DEPOT_SECTION':
                    if line.strip() != '-1':
                        data['DEPOT_SECTION'] = int(line.strip())
    
    return data

#Gera o grafico padrão do dataset
def plot_evrp_instance(data):
    # Extract coordinates
    coords = data['NODE_COORD_SECTION']
    depot_id = data['DEPOT_SECTION']
    station_ids = data['STATIONS_COORD_SECTION']
    
    # Separate customers, depot, and stations
    customer_ids = [node_id for node_id in coords.keys() 
                   if node_id != depot_id and node_id not in station_ids]
    
    # Plotting
    plt.figure(figsize=(10, 8))
    
    # Plot customers
    customer_x = [coords[node_id][0] for node_id in customer_ids]
    customer_y = [coords[node_id][1] for node_id in customer_ids]
    plt.scatter(customer_x, customer_y, c='blue', label='Customers', s=50)
    
    # Plot depot
    depot_x, depot_y = coords[depot_id]
    plt.scatter(depot_x, depot_y, c='red', label='Depot', s=100, marker='s')
    
    # Plot stations
    station_x = [coords[node_id][0] for node_id in station_ids]
    station_y = [coords[node_id][1] for node_id in station_ids]
    plt.scatter(station_x, station_y, c='green', label='Stations', s=75, marker='^')
    
    # Annotate node IDs
    for node_id, (x, y) in coords.items():
        plt.annotate(str(node_id), (x, y), textcoords="offset points", xytext=(0,5), ha='center')
    
    plt.title('EVRP Instance Visualization')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()

#Plota a rota atual
def plot_single_route_with_trips(data, single_route):
    """
    Plota uma única rota com múltiplos trajetos separados por depósitos (1).
    Cada segmento entre dois '1's é considerado um trajeto diferente.
    
    Parâmetros:
    - data: dicionário com os dados do problema
    - single_route: lista contendo uma única rota com múltiplos trajetos (ex: [1,2,3,1,4,5,1])
    """
    # Extrai coordenadas
    coords = data['NODE_COORD_SECTION']
    depot_id = data['DEPOT_SECTION']
    station_ids = data['STATIONS_COORD_SECTION']
    
    # Divide a rota única em trajetos separados
    trips = []
    current_trip = []
    
    for node in single_route:
        if node == 1 and current_trip:
            current_trip.append(1)  # Fecha o trajeto
            trips.append(current_trip)
            current_trip = [1]  # Começa novo trajeto
        else:
            current_trip.append(node)
    
    # Adiciona o último trajeto se necessário
    if len(current_trip) > 1:
        current_trip.append(1)
        trips.append(current_trip)
    
    # Separa clientes visitados/não visitados
    all_customers = [node_id for node_id in coords.keys() 
                    if node_id != depot_id and node_id not in station_ids]
    visited_customers = [node for trip in trips for node in trip[1:-1]]
    unvisited_customers = list(set(all_customers) - set(visited_customers))
    
    # Configuração do plot
    plt.figure(figsize=(12, 8))
    
    # Plot de clientes não visitados (cinza)
    unvisited_x = [coords[node_id][0] for node_id in unvisited_customers]
    unvisited_y = [coords[node_id][1] for node_id in unvisited_customers]
    plt.scatter(unvisited_x, unvisited_y, c='gray', label='Unvisited customers', s=50, alpha=0.5)
    
    # Plot de estações (verde)
    station_x = [coords[node_id][0] for node_id in station_ids]
    station_y = [coords[node_id][1] for node_id in station_ids]
    plt.scatter(station_x, station_y, c='green', label='Stations', s=75, marker='^', alpha=0.7)
    
    # Plot do depósito (vermelho)
    depot_x, depot_y = coords[depot_id]
    plt.scatter(depot_x, depot_y, c='red', label='Depot', s=150, marker='s')
    
    # Cores para os trajetos
    colors = plt.cm.tab10.colors
    
    # Plot cada trajeto com cor diferente
    for i, trip in enumerate(trips):
        color = colors[i % len(colors)]
        trip_x = [coords[node_id][0] for node_id in trip]
        trip_y = [coords[node_id][1] for node_id in trip]
        
        # Linha do trajeto
        plt.plot(trip_x, trip_y, 'o-', color=color, linewidth=2, markersize=8,
                label=f'Trip {i+1}')
        
        # Setas para direção
        for j in range(len(trip)-1):
            plt.annotate('', xy=(trip_x[j+1], trip_y[j+1]), xytext=(trip_x[j], trip_y[j]),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Anotações dos IDs
    for node_id, (x, y) in coords.items():
        plt.annotate(str(node_id), (x, y), textcoords="offset points", 
                    xytext=(0,5), ha='center', fontsize=8)
    
    plt.title(f'EVRP Route Visualization\nTotal Trips: {len(trips)}', fontsize=14)
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Y Coordinate', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

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


