import matplotlib.pyplot as plt
import csv
import os

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

def criar_csv_vazio():
        """Cria um arquivo CSV vazio com os cabeçalhos"""
        with open('melhores_resultados.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Avaliacoes', 
                'Distancia', 
                'Onde_Foi_Encontrada', 
                'Melhor_Rota'
            ])
