# main.py
"""File for run the application"""
import tkinter as tk
import pandas as pd
from model import PokemonModel
from view import PokeBuilderView
from controller import PokeBuilderController

if __name__ == "__main__":
    root = tk.Tk()
    model = PokemonModel('Pokemon.csv')
    controller = PokeBuilderController(None, model)
    pokemon_data = model.get_pokemon_data()
    if isinstance(pokemon_data, list):
        pokemon_data = pd.DataFrame(pokemon_data)

    view = PokeBuilderView(root, model, pokemon_data, controller)
    controller.view = view
    root.mainloop()
