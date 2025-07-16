from itertools import product
from gaClass import *

import pandas as pd
import matplotlib.pyplot as plt
import glob

# # Valores possíveis para cada parâmetro
# evaluation_methods = ['distancia', 'rankeamento']  # Só 'dist' no seu exemplo, mas pode ter mais
# selection_methods = ['roleta', 'torneio']
# crossover_methods = ['two_point', 'uniforme']
# mutation_methods = ['swap', 'inversao', 'scramble']
# replacement_methods = ['elitismo']  # Fixo

# # Lista para armazenar as combinações
# configs = []

# # Produto cartesiano de todos os parâmetros
# for evaluation, selection, crossover, mutation, replacement in product(
#         evaluation_methods, selection_methods, crossover_methods, mutation_methods, replacement_methods):

#     config = {
#         'evaluation': evaluation,
#         'selection': selection,
#         'tamanho_torneio': 5 if selection == 'torneio' else None,
#         'crossover': crossover,
#         'mutation': mutation,
#         'replacement': replacement
#     }

#     configs.append(config)


# # Configuração base
# base_params_ga = {
#     'n_pop': 50,
#     'n_geracoes': 500,
#     'max_aval': 25000*32,
#     'taxa_crossover': 1,
#     'taxa_mutacao': 0.7,
#     'n_pais': 30,
#     'n_filhos': 100,
#     'n_elite': 10,
#     'num_rotas_min': 3,
#     'limite_convergencia': 20,
#     'bits_por_cidade': None,
# }

# # Possíveis valores alternativos para cada parâmetro
# taxas_crossover = [1 , 0.9]
# taxas_mutacao = [0.3 , 0.1]
# n_elite_options = [10 , 20]

# # Lista para armazenar as combinações
# params_list = []

# for crossover, mutacao, elite in zip(taxas_crossover, taxas_mutacao, n_elite_options):
#     params = base_params_ga.copy()
#     params['taxa_crossover'] = crossover
#     params['taxa_mutacao'] = mutacao
#     params['n_elite'] = elite
#     params_list.append(params)





# import random

# # Vamos supor que você já tenha:
# # - configs = [ ... ]  -> lista de dicionários com configs de seleção/crossover/mutation/etc.
# # - params_list = [ ... ] -> lista de dicionários com params_ga diferentes
# # - EVRP_GA é sua classe de GA

# # Configura semente para reprodutibilidade
# random.seed(1)

# # Aqui será salvo tudo
# results = {}
# table_data = [] 
# # 1) Executar todas as combinações e armazenar os resultados
# for i_config, config in enumerate(configs):
#     for i_params, params_ga in enumerate(params_list):
#         key = f'config_{i_config}_params_{i_params}'

#         print(f'Executando {key}...')

#         # Instancia e roda o GA
#         ga = EVRP_GA('E-n51-k5.evrp', params_ga, config)
#         best_solution = ga.run()  # Assuma que isso retorna a melhor rota/fitness/obj

#         # Armazena resultado
#         results[key] = {
#             'config': config,
#             'params_ga': params_ga,
#             'best_solution': calcular_distancia_total(ga.evrp_data, best_solution)
#         }
#         row = {
        
#         'evaluation': config['evaluation'],
#         'selection': config['selection'],
#         'crossover': config['crossover'],
#         'mutation': config['mutation'],
#         'replacement': config['replacement'],
#         # params_ga info
#         'taxa_crossover': params_ga['taxa_crossover'],
#         'taxa_mutacao': params_ga['taxa_mutacao'],
#         'n_elite': params_ga['n_elite'],
#         # resultado info
#         'fitness': calcular_distancia_total(ga.evrp_data, best_solution),  # ajuste conforme seu objeto
#         'rota': best_solution
#         }
#         table_data.append(row)

# df_results = pd.DataFrame(table_data)
# df_results.to_csv('results/resultados_ga2_inicial.csv', index=False)
# # 2) Encontrar a melhor combinação com base no melhor custo/fitness
# # Suponha que best_solution tenha um atributo 'fitness' (troque conforme seu retorno)
# best_key = None
# best_fitness = float('inf')
# for key, result in results.items():
#     fitness = result['best_solution']  # ajuste isso para seu atributo real
#     if fitness < best_fitness:
#         best_fitness = fitness
#         best_key = key

# print(f'\nMelhor combinação encontrada: {best_key} com fitness {best_fitness}')

# # 3) Executar a melhor combinação 20 vezes e salvar as melhores rotas
# best_config = results[best_key]['config']
# best_params = results[best_key]['params_ga']

# random.seed(1)

# best_routes = []
# table_data = []
# # distancia,torneio,two_point,inversao,elitismo
params_ga = {
    'n_pop': 50,
    'n_geracoes': 500,
    'max_aval': 25000*32,
    'taxa_crossover': 0.9,
    'taxa_mutacao': 0.1,
    'n_pais': 30,
    'n_filhos': 100,
    'n_elite': 20,
    'num_rotas_min': 3,
    'limite_convergencia': 20,
    'bits_por_cidade': None,
}

config = {
        'evaluation': "distancia",
        'selection': "torneio",
        'tamanho_torneio': 5,
        'crossover': "uniforme",
        'mutation': "inversao",
        'replacement': "elitismo"
    }
# for run_idx in range(20):
#     print(f'Rodando melhor config novamente #{run_idx+1}...')
#     ga = EVRP_GA('E-n51-k5.evrp', params_ga, config, id = run_idx+1)
#     best_solution = ga.run()

#     best_routes.append(best_solution)

#     row = {
#         'id': run_idx + 1,
#         'distancia': calcular_distancia_total(ga.evrp_data, best_solution),
#         'rota':best_solution
#     }
#     table_data.append(row)  # <-- estava faltando adicionar aqui!

# # Cria DataFrame
# df_results = pd.DataFrame(table_data)
# df_results.to_csv('results/resultados_ga2_final.csv', index=False)
# import ast


df_results = pd.read_csv('results/resultados_ga2_final.csv')
df_results
# 4) Agora results tem todos os resultados + best_routes tem as 20 melhores rotas repetidas
# print(f'\nTotal de execuções salvas: {48} combinações + {len(best_routes)} rodadas da melhor.')

# Se quiser salvar em arquivo, pode usar pickle, JSON ou CSV dependendo do formato

# Calcula estatísticas
media = df_results['distancia'].mean()
minimo = df_results['distancia'].min()
maximo = df_results['distancia'].max()
desvio = df_results['distancia'].std()

print(f'\nEstatísticas das 20 execuções:')
print(f'  Média: {media:.4f}')
print(f'  Mínimo: {minimo:.4f}')
print(f'  Máximo: {maximo:.4f}')
print(f'  Desvio padrão: {desvio:.4f}')

rotas_minimas = df_results[df_results['distancia'] == minimo]
ga = EVRP_GA('E-n51-k5.evrp',params_ga, config)
for idx, linha in rotas_minimas.iterrows():
    aux = linha['rota'].replace("[","").replace("]","").replace("  "," ").replace(" ",",").replace(",","",1).replace("\n","").split(",")  # Pega a rota com menor distância
    rota_minima = []
    for i in aux:
        rota_minima.append(int(i))
    np.array(rota_minima)
    print(type(rota_minima[0]))
    idRota = linha['id']  # Pega a rota com menor distância

    plot_single_route_with_trips(ga.evrp_data, rota_minima,idRota)
# Salva CSV se quiser



# Parâmetros gerais
melhor_meta = 570.17
max_aval = 32 * 25000  # 800.000 avaliações

# Pega todos os arquivos CSV no padrão desejado
arquivos = glob.glob('results/csvs/melhores2_resultados*.csv')

for arquivo in arquivos:
    # Extrai id do nome do arquivo
    id_tentativa = arquivo.split('resultados')[-1].split('.csv')[0]
    
    print(f'Processando tentativa {id_tentativa}...')
    # Lê CSV, ignora a coluna Melhor_Rota
    df = pd.read_csv(arquivo,header=None, names=['Avaliacoes', 'Distancia', 'Tipo'])
    # ============= Gráfico de Progressão ==============
    plt.figure(figsize=(10, 6))
    plt.plot(df['Avaliacoes'], df['Distancia'], marker='o', label='Distância')
    plt.axhline(y=melhor_meta, color='red', linestyle='--', label=f'Melhor Meta ({melhor_meta})')

    plt.title(f'Gráfico de Progressão de Resultados Tentativa {id_tentativa}')
    plt.xlabel('Avaliações')
    plt.ylabel('Distância')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'results/pngs/2progressao{id_tentativa}.png')
    plt.close()

    # ============= Gráfico de Pizza (Concentração) ==============
    plt.figure(figsize=(8, 8))
    counts = df['Tipo'].value_counts()
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
    plt.title(f'Gráfico de Concentração de Alterações Tentativa {id_tentativa}')
    plt.tight_layout()
    plt.savefig(f'results/pngs/2concentracao{id_tentativa}.png')
    plt.close()

    print(f'Gráficos salvos para tentativa {id_tentativa}.')
