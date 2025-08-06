import ast
from itertools import product
#from gaClass import *
from gaClass3 import *

import pandas as pd
import matplotlib.pyplot as plt
import glob

random.seed(1)

param_gaDict = {
    'params_ga' : {
        'n_pop': 100,                # População maior para mais diversidade
        'n_geracoes': 500,
        'max_aval': 25000*5,
        'taxa_crossover': 1,
        'taxa_mutacao': 0.9,        # Mutação baixa para evitar perturbações excessivas
        'n_pais': 20,
        'n_filhos': 80,
        'n_elite': 15,
        'num_rotas_min': 3,          # Definido pelo problema
        'limite_convergencia': 20    # Parar se não houver melhoria em 20 gerações
    },
    }
config = {
        'evaluation': 'restricoes',  # Usar penalidades para restrições distancia/restricoes
        'selection': 'torneio',      # Torneio é mais eficiente para evitar convergência prematura
        'tamanho_torneio': 5,
        'crossover': 'two_point',    # Combinação mais equilibrada
        'mutation': 'swap',          # Mutação simples para preservar estrutura
        'replacement': 'elitismo'    # Mantém as melhores soluções
    }
listparams = ["params_ga"]
ervps = ['E-n23-k3.evrp','E-n51-k5.evrp']
ervpdict = {ervps[0]: [573.14, 32 * 25000, 3], ervps[1]: [570.17,60 * 25000,5]}
best_routes = []
table_data = []
for arq in ervps:
    for params in listparams:
        params_ga = param_gaDict[params]
        params_ga["max_aval"] = ervpdict[arq][1]
        params_ga['num_rotas_min'] = ervpdict[arq][2]
        
        for run_idx in range(20):
            print(f'Rodando melhor config novamente #{run_idx+1}...')
            ga = EVRP_GA(arq, params_ga, config,estrat=params, id = run_idx+1)
            best_solution = ga.run_2()

            best_routes.append(best_solution)

            row = {
                'id': run_idx + 1,
                'distancia': calcular_distancia_total(ga.evrp_data, best_solution),
                'rota':best_solution
            }
            table_data.append(row)  # <-- estava faltando adicionar aqui!

        # Cria DataFrame
        df_results = pd.DataFrame(table_data)
        df_results.to_csv(f'results/resultados_ga_{arq}_{params}_trabalho3.csv', index=False)

# Pega todos os arquivos CSV no padrão desejado
for params in listparams:
    for arq in ervps:
        arquivos = glob.glob(f'results/csvs/melhores_resultados3_{arq}_{params}_*.csv')

        for arquivo in arquivos:
            # Extrai id do nome do arquivo
            id_tentativa = arquivo.split('resultados')[-1].split('.csv')[0]
            
            print(f'Processando tentativa {id_tentativa}...')
            # Lê CSV, ignora a coluna Melhor_Rota
            df = pd.read_csv(arquivo,header=None, names=['Avaliacoes', 'Distancia', 'Tipo', 'crossover', 'mutation'])
            # ============= Gráfico de Progressão ==============
            plt.figure(figsize=(10, 6))
            plt.plot(df['Avaliacoes'], df['Distancia'], marker='o', label='Distância')
            plt.axhline(y=ervpdict[arq][0], color='red', linestyle='--', label=f'Melhor Meta ({ervpdict[arq][0]})')

            plt.title(f'Gráfico de Progressão de Resultados Tentativa {id_tentativa}')
            plt.xlabel('Avaliações')
            plt.ylabel('Distância')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'results/pngs/progressao{id_tentativa}_{arq}_trab3.png')
            plt.close()

            # ============= Gráfico de Pizza (Concentração) ==============
            plt.figure(figsize=(8, 8))
            counts = df['Tipo'].value_counts()
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
            plt.title(f'Gráfico de Concentração de Alterações Tentativa {id_tentativa}')
            plt.tight_layout()
            plt.savefig(f'results/pngs/concentracao{id_tentativa}_{arq}_trab3.png')
            plt.close()

            print(f'Gráficos salvos para tentativa {id_tentativa}.')



for arq in ervps:
    for params in listparams: 
        params_ga = param_gaDict[params]
        params_ga["max_aval"] = ervpdict[arq][1]
        params_ga['num_rotas_min'] = ervpdict[arq][2]

        df_results = pd.read_csv(f'results/resultados_ga_{arq}_{params}_trabalho3.csv')
        media = df_results['distancia'].mean()
        minimo = df_results['distancia'].min()
        maximo = df_results['distancia'].max()
        desvio = df_results['distancia'].std()

        print(f'\nEstatísticas das 20 execuções {arq} com parametros {params}:')
        print(f'  Média: {media:.4f}')
        print(f'  Mínimo: {minimo:.4f}')
        print(f'  Máximo: {maximo:.4f}')
        print(f'  Desvio padrão: {desvio:.4f}')
        rotas_minimas = df_results[df_results['distancia'] == minimo]
        ga = EVRP_GA(arq,params_ga, config)
        for idx, linha in rotas_minimas.iterrows():
            aux = linha['rota'].replace("[","").replace("]","").replace("  "," ").replace(" ",",").replace(",","",1).replace("\n","").split(",")  # Pega a rota com menor distância
            rota_minima = []
            for i in aux:
                rota_minima.append(int(i))
            np.array(rota_minima)
            print(type(rota_minima[0]))
            idRota = linha['id']  # Pega a rota com menor distância

            plot_single_route_with_trips(ga.evrp_data, rota_minima,idRota,arq,params)


import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

# Supondo que você tenha essas listas e dicionário definidos
# listparams = [...]
# ervps = [...]
# ervpdict = {...}

for params in listparams:
    for arq in ervps:
        arquivos = glob.glob(f'results/csvs/melhores_resultados3_{arq}_{params}_*.csv')
        
        if not arquivos:
            print(f'Nenhum arquivo encontrado para {arq} com parâmetros {params}')
            continue

        # Lista para armazenar os DataFrames de cada tentativa
        dfs = []

        for arquivo in arquivos:
            df = pd.read_csv(arquivo, header=None, names=['Avaliacoes', 'Distancia', 'Tipo', 'crossover', 'mutation'])
            dfs.append(df)

        # Concatena todos os DataFrames
        df_concat = pd.concat(dfs, ignore_index=True)

        # Gráfico de Dispersão (scatter)
        plt.figure(figsize=(10, 6))
        plt.scatter(df_concat['Avaliacoes'], df_concat['Distancia'], alpha=0.6, c='blue', edgecolor='k')
        plt.axhline(y=ervpdict[arq][0], color='red', linestyle='--', label=f'Melhor Meta ({ervpdict[arq][0]})')
        plt.axvline(x=ervpdict[arq][1], color='green', linestyle='--', linewidth=1.5, label=f'x max = {ervpdict[arq][1]}')

        plt.title(f'Gráfico de Dispersão de Resultados\n{arq} - {params}')
        plt.xlabel('Avaliações')
        plt.ylabel('Distância')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        scatter_path = f'results/pngs/dispersao_{arq}_{params}.png'
        plt.savefig(scatter_path)
        plt.close()
        print(f'Salvo: {scatter_path}')

        # Gráfico de Pizza (Concentração de Tipos)
        plt.figure(figsize=(8, 8))
        counts = df_concat['Tipo'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.title(f'Concentração de Alterações\n{arq} - {params}')
        plt.tight_layout()
        pizza_path = f'results/pngs/concentracao_{arq}_{params}.png'
        plt.savefig(pizza_path)
        plt.close()
        print(f'Salvo: {pizza_path}')

        # Gráfico de Pizza (Concentração de Tipos)
        plt.figure(figsize=(8, 8))
        counts = df_concat['crossover'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.title(f'Concentração de Alterações\n{arq} - {params}')
        plt.tight_layout()
        pizza_path = f'results/pngs/concentracao_cross_{arq}_{params}.png'
        plt.savefig(pizza_path)
        plt.close()
        print(f'Salvo: {pizza_path}')

        # Gráfico de Pizza (Concentração de Tipos)
        plt.figure(figsize=(8, 8))
        counts = df_concat['mutation'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.title(f'Concentração de Alterações\n{arq} - {params}')
        plt.tight_layout()
        pizza_path = f'results/pngs/concentracao_mut_{arq}_{params}.png'
        plt.savefig(pizza_path)
        plt.close()
        print(f'Salvo: {pizza_path}')
