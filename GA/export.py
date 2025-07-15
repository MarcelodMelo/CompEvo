"""
Pacote principal do Algoritmo Genético para EVRP

Importe a classe principal diretamente:
from evrp_ga import EVRP_GA
"""

from .ga import EVRP_GA  # Expõe a classe principal

__version__ = "1.0.0"
__all__ = ['EVRP_GA']  # Controla o que é exportado