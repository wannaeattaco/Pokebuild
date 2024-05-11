#control.py
"""File for Control class"""

import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd


class PokeBuilderController:
    """Controller class of the application"""

    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.saved_teams = pd.read_csv('saved_teams.csv') if os.path.exists('saved_teams.csv') \
            else pd.DataFrame(columns=['Team Name', 'Members'])

    def initialize(self):
        """Function for View Initialization and Data Retrieval"""
        if self.view:
            self.setup_bindings()
            self.initialize_pokemon_list()

    def setup_bindings(self):
        """Setup event bindings for the UI elements."""
        if self.view:
            self.view.type_combobox.bind('<<ComboboxSelected>>', self.apply_filters)
            self.view.search_entry.bind('<KeyRelease>', self.apply_filters)
            self.view.confirm_team_button.bind('<Button-1>', lambda event: self.confirm_team())

    def initialize_pokemon_list(self):
        """Get pokemons' data from dataset"""
        pokemon_data = self.model.get_pokemon_data()
        self.view.update_pokemon_list(pokemon_data)

    # Team Building and Confirmation
    def filter_pokemon(self):
        """Function for filter pokemon list"""
        self.apply_filters()

    def apply_filters(self):
        """Function to apply filters to the pokemon list."""
        name = self.view.search_entry.get()
        type1 = self.view.type_combobox.get()
        filtered_data = self.model.get_pokemon_data(name=name, type1=type1)
        self.view.update_pokemon_list(filtered_data)

    def confirm_team(self):
        """Function to confirm the selected pokemon team"""
        selected_items = self.view.selected_team_listbox.get(0, tk.END)
        team_name = "Default Team"

        self.model.clear_team_members(team_name)
        for item in selected_items:
            self.model.add_pokemon_to_team(team_name, item)
        self.save_teams_data()
        self.view.update_saved_teams_tab()

    # Team Display and Management
    def load_team(self, team_name):
        """Function for load team's members of selected team"""
        members = self.model.load_team(team_name)
        if members:
            team_data = self.model.get_pokemon_data_by_names(members)
            self.view.display_graph_for_team(team_data)
        else:
            self.view.display_error("No team members found for the selected team.")

    def save_current_team(self, team_name, current_team):
        """Save current team into file"""
        self.model.save_team(team_name, current_team)

    def delete_team(self, index):
        """Function for delete selected team from file"""
        if index is not None:
            self.model.delete_team(index)
            self.view.update_saved_teams_tab()
            messagebox.showinfo("Success", "Team deleted successfully!")

        else:
            messagebox.showerror("Error", "No team selected for deletion.")

    # Data Persistence
    def save_teams_data(self):
        """Function for save team into file"""
        self.model.saved_teams.to_csv('saved_teams.csv', index=False)
