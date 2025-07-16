import numpy as np
from GA.operators.export import *
from GA.utils.export import *

class EVRP_GA:
    def __init__(self, filename, param_ga, config, binario=True, restricoes=False, id = None):
        self.evrp_data = read_evrp_file(filename)
        self.param_problema = parametros_problema(self.evrp_data, binario, restricoes)
        self.param_ga = param_ga
        self.config = config
        self.id = id
        self.best_run = []
        self.best_dist = float('inf')
        self.population = []
        self.fitness = {}
        self.pais = []
        self.filhos = []
        self.new_pop = []
        
        # Contadores e histórico
        self.n_aval = 0  # Contador de avaliações
        self.historico_melhor_rota = []
        self.historico_melhor_distancia = []

        # Configuração dos operadores
        self.evaluation_methods = {
            'distancia': avaliacao_distancia_pura,
            'restricoes': avaliacao_distancia_restricoes,
            'rankeamento': avaliacao_rankeamento
        }

        self.selection_methods = {
            'roleta': selecao_roleta,
            'torneio': selecao_torneio,
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
            'elitimos': substituicao_elitismo,
            'steady_state': substituicao_steady_state,
        }

    def initialize(self):
        n_pop = self.param_ga['n_pop']
        self.population = [criar_rotas_aleatorias(self.evrp_data, self.param_problema['num_rotas_min'], self.param_problema['restricoes']) for _ in range(n_pop)]
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

    def crossover(self):
        self.filhos = crossover_completo(self.pais, self.evrp_data, n_filhos = self.param_ga['n_filhos'], num_rotas_min=self.param_problema['num_rotas_min'], tipo_crossover=self.config['crossover'], taxa_crossover=1, estacao=self.param_problema['restricoes'])
        #print(f"Gerou {len(self.filhos)} filhos")

    def mutation(self):
        if self.config['mutation'] == '': return
        self.filhos = aplicar_mutacao(self.filhos, self.evrp_data, self.param_problema['num_rotas_min'], metodo=self.config['mutation'], taxa_mutacao=0.1, estacao=self.param_problema['restricoes'])
        #print(f"Mutação em {len(self.filhos)} filhos")

    def replacement(self):
        fitness_filhos = avaliacao_rankeamento(self.filhos, self.evrp_data)
        self.new_pop = gerar_nova_populacao(self.population, self.filhos, self.fitness, fitness_filhos, metodo=self.config['replacement'], 
                         n_pop=self.param_ga['n_pop'], n_pais=self.param_ga['n_pais'], n_filhos=self.param_ga['n_filhos'], n_elite=5)
        #print(f"Finalizou com: {len(self.new_pop)} rotas")

    def registrar_melhoria_csv(self, onde):
        """Registra uma nova melhoria no CSV"""
        if self.id != None:
            with open(f'results/csvs/melhores2_resultados{self.id}.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    self.n_aval,
                    self.best_dist,
                    onde,
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