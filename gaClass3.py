import numpy as np
from GA.operators.export import *
from GA.utils.export import *

class EVRP_GA:
    def __init__(self, filename, param_ga, config, estrat = "", binario=True, restricoes=True, id = None):
        self.evrp_data = read_evrp_file(filename)
        self.param_problema = parametros_problema(self.evrp_data, binario, restricoes)
        self.param_ga = param_ga
        self.config = config
        self.id = id
        self.nameEstrat = estrat
        self.best_run = []
        self.best_dist = float('inf')
        self.population = []
        self.fitness = {}
        self.pais = []
        self.filhos = []
        self.new_pop = []
        self.filename = filename
        # Contadores e histórico
        self.n_aval = 0  # Contador de avaliações
        self.historico_melhor_rota = []
        self.historico_melhor_distancia = []
        self.dist_matrix = {}

        # Configuração dos operadores
        self.evaluation_methods = {
            'distancia': avaliacao_distancia_pura, #
            'restricoes': avaliacao_com_penalidades,
            'rankeamento': avaliacao_rankeamento 
        }

        self.selection_methods = {
            'roleta': selecao_roleta,
            'torneio': selecao_torneio, #
            'rank': selecao_rank
        }
        
        self.crossover_methods = {
            'one_point': crossover_one_point,
            'two_point': crossover_two_point,
            'uniforme': crossover_uniforme
        }

        self.mutation_methods = {
            'bit_flip': mutacao_bit_flip,
            'swap': mutacao_swap,
            'inversao': mutacao_inversao,
            'scramble': mutacao_scramble,
            '': False
        }

        self.replacement_methods = {
            'completa': substituicao_completa,
            'elitimos': substituicao_elitismo, #
            'steady_state': substituicao_steady_state,
        }

    def initialize(self):
        self.dist_matrix = calcular_matriz_prioridade(self.evrp_data)
        print(self.dist_matrix)
        n_pop = self.param_ga['n_pop']
        self.population = [criar_rotas_aleatorias(self.evrp_data, self.param_problema['num_rotas_min'], self.param_problema['restricoes']) for _ in range(n_pop)]
        #self.population = [criar_rota_nn_inteligente_com_rotas_minimas(self.evrp_data, self.param_problema['num_rotas_min']) for _ in range(n_pop)]
        self.population = [aplicar_restricao(rotas, self.evrp_data, self.param_problema['num_rotas_min']) for rotas in self.population]
        #print(f"Iniciou com: {len(self.population)} rotas")
    
    def evaluate(self):
        """Avalia a população e atualiza o contador de avaliações."""
        metodo = self.evaluation_methods[self.config['evaluation']]
        self.fitness = metodo(self.population, self.evrp_data)
        self.n_aval += len(self.population)  # Incrementa o contador
        #print(f"Avaliou {len(self.fitness)} rotas (Total de avaliações: {self.n_aval})")

    def selection(self):
        metodo = self.selection_methods[self.config['selection']]
        self.pais = metodo(self.population, self.fitness, self.param_ga['n_pais'])
        #print(f"Seleciou {len(self.pais)} pais")

    #def crossover(self):
        #self.filhos = [crossover_nn(pai1, pai2, self.evrp_data, self.dist_matrix) for pai1, pai2 in zip(self.pais[::2], self.pais[1::2])]
        #self.filhos = crossover_completo(self.pais, self.evrp_data, n_filhos = self.param_ga['n_filhos'], num_rotas_min=self.param_problema['num_rotas_min'], tipo_crossover=self.config['crossover'], taxa_crossover=1, estacao=self.param_problema['restricoes'])
        #print(f"Gerou {len(self.filhos)} filhos")

    def crossover(self):
        if random.random() < 0.6:  # 60% chance de usar o balanceador
            self.filhos = []
            for i in range(0, len(self.pais), 2):
                if i+1 < len(self.pais):
                    f1, f2 = crossover_balanceador(
                        self.pais[i], self.pais[i+1],
                        self.evrp_data, self.dist_matrix, self.param_problema['num_rotas_min']
                    )
                    self.filhos.extend([f1, f2])
        else:  # 40% chance de usar o NN
            self.filhos = [
                crossover_nn(pai1, pai2, self.evrp_data, self.dist_matrix,  num_rotas_min=self.param_problema['num_rotas_min'])
                for pai1, pai2 in zip(self.pais[::2], self.pais[1::2])
            ]

    def mutation(self):
        if self.config['mutation'] == '': return
        #self.filhos = aplicar_mutacao(self.filhos, self.evrp_data, self.param_problema['num_rotas_min'], metodo=self.config['mutation'], taxa_mutacao=0.1, estacao=self.param_problema['restricoes'])
        #self.filhos = aplicar_mutacao_rest(self.filhos, self.evrp_data, self.dist_matrix, self.param_problema['num_rotas_min'], metodo=self.config['mutation'], taxa_mutacao=0.1, estacao=self.param_problema['restricoes'])
        self.filhos = [
            mutacao_balanceamento_carga(filho, self.evrp_data, self.dist_matrix, 0.7, num_rotas_min=self.param_problema['num_rotas_min'])
            for filho in self.filhos
        ]
        self.filhos = [mutacao_nn(filho, self.evrp_data, self.dist_matrix, taxa_mutacao = 0.7, num_rotas_min=self.param_problema['num_rotas_min']) 
        for filho in self.filhos
        ]
        self.filhos = [mutacao_otimiza_rota(filho, self.evrp_data, self.dist_matrix, taxa_mutacao = 0.7, num_rotas_min=self.param_problema['num_rotas_min']) 
        for filho in self.filhos
        ]
        #print(f"Mutação em {len(self.filhos)} filhos")

    def replacement(self):
        fitness_filhos = avaliacao_com_penalidades(self.filhos, self.evrp_data)
        self.new_pop = gerar_nova_populacao(self.population, self.filhos, self.fitness, fitness_filhos, metodo=self.config['replacement'], 
                         n_pop=self.param_ga['n_pop'], n_pais=self.param_ga['n_pais'], n_filhos=self.param_ga['n_filhos'], n_elite=5)
        #print(f"Finalizou com: {len(self.new_pop)} rotas")

    def registrar_melhoria_csv(self, onde):
        """Registra uma nova melhoria no CSV"""
        if self.id != None:
            with open(f'results/csvs/melhores_resultados3_{self.filename}_{self.nameEstrat}_{self.id}.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    self.n_aval,
                    self.best_dist,
                    onde,
                    self.config["crossover"],
                    self.config["mutation"],
                ])
            
    
    def run(self):
        self.initialize()
        self.evaluate()
        criar_csv_vazio()  # Cria o CSV vazio no início
        contador = 0
        while self.n_aval < self.param_ga['max_aval'] and contador < self.param_ga['max_aval']/250:
            best_rota, best_dist = melhor_rota(self.population, self.evrp_data)
            if self.best_dist > best_dist:
                print("Pop", self.n_aval, best_dist)
                self.best_dist = best_dist
                self.best_run = best_rota
                self.registrar_melhoria_csv('Populacao Atual')
                contador = 0
                
            self.historico_melhor_rota.append(best_rota)
            self.historico_melhor_distancia.append(best_dist)
            
            self.selection()
            self.crossover()
            best_rota, best_dist = melhor_rota(self.filhos, self.evrp_data)
            if self.best_dist > best_dist:
                print("Cross", self.n_aval, best_dist)
                self.best_dist = best_dist
                self.best_run = best_rota
                self.registrar_melhoria_csv('Crossover')
                contador = 0
                
            self.mutation()
            best_rota, best_dist = melhor_rota(self.filhos, self.evrp_data)
            if self.best_dist > best_dist:
                print("Mut", self.n_aval, best_dist)
                self.best_dist = best_dist
                self.best_run = best_rota
                self.registrar_melhoria_csv('Mutacao')
                contador = 0
                
            self.replacement()
            self.population = self.new_pop
            self.evaluate()
            contador =contador+1
            

        print(f"Parada atingida: {self.n_aval} avaliações realizadas.")
        return self.best_run
    

    def escolher_metodo(self,probabilidades):
        return random.choices(range(4), weights=probabilidades, k=1)[0]

    def atualizar_pesos(self,sucessos, tentativas):
        base = 0.01  # para evitar pesos zero
        pesos = [s / t + base for s, t in zip(sucessos, tentativas)]
        soma = sum(pesos)
        return [p / soma for p in pesos]

    def run_2(self):
        self.initialize()
        self.evaluate()
        criar_csv_vazio()
        

        

        # Contadores e estado para controle de convergência
        contador_estagnacao = 0
        MAX_ESTAGNACAO = 100  # Número de iterações sem melhoria para considerar convergência
        MELHORIA_MINIMA = 1.0  # Melhoria mínima para resetar contador
        
        # Listas de métodos para rotação
        crossover_methods = ['one_point', 'two_point', 'uniforme', 'OX']
        mutation_methods = ['swap', 'inversao', 'scramble', 'insercao']

        vetCross = [0.25] * 4
        vetMut =  [0.25] * 4
        sucessoCross = [1] * 4  # Começa com 1 para evitar divisão por zero
        tentativasCross = [1] * 4

        sucessoMut = [1] * 4
        tentativasMut = [1] * 4

        idx_cross = self.escolher_metodo(vetCross)
        idx_mut = self.escolher_metodo(vetMut)

        
        self.config["crossover"] = crossover_methods[idx_cross]
        self.config["mutation"] = mutation_methods[idx_mut]
        print(f"Métodos: Crossover={self.config['crossover']}, Mutação={self.config['mutation']}")
        # Histórico de melhor distância para detecção de convergência
        last_best_dist = float('inf')
        
        while self.n_aval < self.param_ga['max_aval']:
            # Etapa normal do GA
            best_rota, best_dist = melhor_rota(self.population, self.evrp_data)
            
            # Verifica melhoria
            if last_best_dist - best_dist > MELHORIA_MINIMA:
                contador_estagnacao = 0
                last_best_dist = best_dist
            else:
                contador_estagnacao += 1
            
            # Atualiza melhor global
            if self.best_dist > best_dist:
                print(f"Melhoria na iteração {self.n_aval}: {best_dist:.2f}")
                self.best_dist = best_dist
                self.best_run = best_rota
                self.registrar_melhoria_csv('Populacao')
            
            # Verifica convergência
            if contador_estagnacao >= MAX_ESTAGNACAO:
                print(f"Convergência detectada na iteração {self.n_aval}. Reiniciando população parcialmente...")
                
                # 1. Mantém os melhores indivíduos (elitismo)
                elite_size = int(0.2 * self.param_ga['n_pop'])  # 20% da população
                elite = sorted(self.population, key=lambda x: self.fitness[tuple(x)])[:elite_size]
                
                # 2. Gera nova população aleatória para o restante
                new_random = [criar_rotas_aleatorias(self.evrp_data, 
                            self.param_problema['num_rotas_min'], 
                            self.param_problema['restricoes']) 
                            for _ in range(self.param_ga['n_pop'] - elite_size)]
                
                # 3. Combina elite + novos indivíduos
                self.population = elite + new_random
                self.evaluate()
                
                # 4. Rota os métodos de crossover e mutação
                idx_cross = self.escolher_metodo(vetCross)
                idx_mut = self.escolher_metodo(vetMut)
                self.config["crossover"] = crossover_methods[idx_cross]
                self.config["mutation"] = mutation_methods[idx_mut]
                print(f"Novos métodos: Crossover={self.config['crossover']}, Mutação={self.config['mutation']}")
                
                # 5. Reseta contador de estagnação
                contador_estagnacao = 0
            
            # Processo normal do GA
            self.historico_melhor_rota.append(best_rota)
            self.historico_melhor_distancia.append(best_dist)
            
            self.selection()
            self.crossover()
            
            best_rota_filhos, best_dist_filhos = melhor_rota(self.filhos, self.evrp_data)
            if self.best_dist > best_dist_filhos:
                print(f"Melhoria na iteração {self.n_aval}: {best_dist:.2f} , Crossover")
                self.best_dist = best_dist_filhos
                self.best_run = best_rota_filhos
                sucessoCross[idx_cross] += 1
                self.registrar_melhoria_csv('Crossover')
            tentativasCross[idx_cross] += 1
    
            self.mutation()
            best_rota_filhos, best_dist_filhos = melhor_rota(self.filhos, self.evrp_data)
            if self.best_dist > best_dist_filhos:
                print(f"Melhoria na iteração {self.n_aval}: {best_dist:.2f} , Mutation")
                self.best_dist = best_dist_filhos
                self.best_run = best_rota_filhos
                self.registrar_melhoria_csv('Mutacao')
                sucessoMut[idx_mut] += 1
            tentativasMut[idx_mut] += 1
            self.replacement()
            self.population = self.new_pop
            self.evaluate()
            if self.n_aval % 100 == 0:
                vetCross = self.atualizar_pesos(sucessoCross, tentativasCross)
                vetMut = self.atualizar_pesos(sucessoMut, tentativasMut)
        print(f"Parada atingida: {self.n_aval} avaliações realizadas.")
        return self.best_run



    def mostrar_historico(self):
        """Exibe o histórico de melhores distâncias por geração."""
        import matplotlib.pyplot as plt
        plt.plot(self.historico_melhor_distancia, marker='o')
        plt.xlabel('Geração')
        plt.ylabel('Melhor Distância')
        plt.title('Convergência do Algoritmo')
        plt.grid(True)
        plt.show()
        
        # Exibe detalhes
        for geracao, distancia in enumerate(self.historico_melhor_distancia):
            print(f"Geração {geracao}: {distancia:.2f}")