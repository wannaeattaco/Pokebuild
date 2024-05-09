# controller.py
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
class PokeBuilderController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.saved_teams = pd.read_csv('saved_teams.csv') if os.path.exists('saved_teams.csv') else pd.DataFrame(columns=['Team Name', 'Members'])

    def initialize(self):
        if self.view:  # Check that view is not None
            self.setup_bindings()
            self.initialize_pokemon_list()

    def setup_bindings(self):
        if self.view:  # Check if view is not None
            self.view.type_combobox.bind('<<ComboboxSelected>>', self.apply_filters)
            self.view.stat_combobox.bind('<<ComboboxSelected>>', self.apply_filters)
            self.view.search_entry.bind('<KeyRelease>', self.apply_filters)
            self.view.min_value_entry.bind('<Return>', self.apply_filters)
            self.view.confirm_team_button.bind('<Button-1>', self.confirm_team)

    def initialize_pokemon_list(self):
        pokemon_data = self.model.get_pokemon_data()  # Get initial data
        self.view.update_pokemon_list(pokemon_data)

    def filter_pokemon(self, event=None):
        self.apply_filters()

    def apply_filters(self, event=None):
        name = self.view.search_entry.get()
        type1 = self.view.type_combobox.get()
        stat = self.view.stat_combobox.get()
        min_value = self.view.min_value_entry.get() or 0
        filtered_data = self.model.get_pokemon_data(name=name, type1=type1, stat=stat, min_value=min_value)
        self.view.update_pokemon_list(filtered_data)

    def confirm_team(self, event):
        selected_items = self.view.selected_team_listbox.get(0, tk.END)
        for item in selected_items:
            self.model.add_pokemon_to_team("Default Team", item)
        self.save_teams_data()
        self.view.update_team_list()

    def display_pokemon_details(self, event):
        # Implement display logic for selected Pokémon details
        pass
    
    def load_teams(self):
        try:
            self.saved_teams = pd.read_csv('saved_teams.csv')
        except FileNotFoundError:
            self.saved_teams = pd.DataFrame(columns=['Team Name', 'Members'])

    def get_saved_teams(self):
        return self.model.get_saved_teams if self.model.get_saved_teams is not None else pd.DataFrame(columns=['Team Name', 'Members'])

    def save_current_team(self, team_name, current_team):
        self.model.save_team(team_name, current_team)

    def delete_team(self, index):
        if index is not None:
            try:
                self.model.delete_team(index)
                self.view.update_saved_teams_tab()  # Update the view to reflect the deletion
                messagebox.showinfo("Success", "Team deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "No team selected for deletion.")
    def save_teams_data(self):
        # Assuming saved_teams is a DataFrame holding all team data
        self.model.saved_teams.to_csv('saved_teams.csv', index=False)
