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
        if self.view:  # Check that view is not None
            self.setup_bindings()
            self.initialize_pokemon_list()

    def setup_bindings(self):
        """Function for set button and combobox in usinf filter"""
        if self.view:  # Check if view is not None
            self.view.type_combobox.bind('<<ComboboxSelected>>', self.apply_filters)
            self.view.stat_combobox.bind('<<ComboboxSelected>>', self.apply_filters)
            self.view.search_entry.bind('<KeyRelease>', self.apply_filters)
            self.view.min_value_entry.bind('<Return>', self.apply_filters)
            self.view.confirm_team_button.bind('<Button-1>', self.confirm_team)

    def initialize_pokemon_list(self):
        """Get pokemons' data from dataset"""
        pokemon_data = self.model.get_pokemon_data()  # Get initial data
        self.view.update_pokemon_list(pokemon_data)

    # Team Building and Confirmation
    def filter_pokemon(self):
        """Function for filter pokemon list"""
        self.apply_filters()

    def apply_filters(self):
        """Function for apply filter into pokemon list"""
        name = self.view.search_entry.get()
        type1 = self.view.type_combobox.get()
        stat = self.view.stat_combobox.get()
        min_value = self.view.min_value_entry.get() or 0
        filtered_data = self.model.get_pokemon_data(name=name, type1=type1,
                                                    stat=stat, min_value=min_value)
        self.view.update_pokemon_list(filtered_data)

    def confirm_team(self):
        """Function to confirm the selected pokemon team"""
        selected_items = self.view.selected_team_listbox.get(0, tk.END)
        team_name = "Default Team"

        # Clear existing team members if reusing the same team name
        self.model.clear_team_members(team_name)

        # Add new members
        for item in selected_items:
            self.model.add_pokemon_to_team(team_name, item)

        # Save the current state of teams to the data file
        self.save_teams_data()

        # Update the team list in the UI
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
            self.view.update_saved_teams_tab()  # Update the view to reflect the deletion
            messagebox.showinfo("Success", "Team deleted successfully!")

        else:
            messagebox.showerror("Error", "No team selected for deletion.")

    # Data Persistence
    def save_teams_data(self):
        """Function for save team into file"""
        self.model.saved_teams.to_csv('saved_teams.csv', index=False)
