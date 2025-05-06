import sys
import os
import setuptools
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.test import *
from src.process_data import *
from src.train_model import *

# Fonction d'exemple de test unitaire
def test_total():
    #Les use cases :
    """La somme de plusieurs éléments d'une liste doit être correcte"""
    assert(total([1.0, 2.0, 3.0])) == 6.0

    """1 - 1 = 0"""
    assert total([1,-1]) == 0

    """-1 -1 = -2"""
    assert total([-1,-1]) == -2

    #Les edge cases :
    """La somme doit être égal à l'unique élément"""
    assert(total([1.0])) == 1.0

    """La somme d'une liste vide doit être 0"""
    assert total([]) == 0

# Encodage du type de tir
def test_encode_shot_type():
    assert encode_shot_type(None) == 0
    assert encode_shot_type('2PT Field Goal') == 2
    assert encode_shot_type('3PT Field Goal') == 3