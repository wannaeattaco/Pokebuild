# view.py
import tkinter as tk
from tkinter import ttk, messagebox,  simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class PokeBuilderView:
    def __init__(self, master, model, pokemon_data, controller):
        self.controller = controller  # Store the controller reference
        self.master = master
        self.model = model
        self.pokemon_data = pokemon_data 
        self.master.title("Poké Builder")
        self.current_team = []
        self.controller.view = self 
        self.setup_ui()

    def setup_ui(self):
        self.tab_control = ttk.Notebook(self.master)

        self.select_tab = ttk.Frame(self.tab_control)
        self.graph_tab = ttk.Frame(self.tab_control)
        self.team_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.select_tab, text='Select Pokémon')
        self.tab_control.add(self.graph_tab, text='Graph View')
        self.tab_control.add(self.team_tab, text='Saved Team')

        self.main_frame = ttk.Frame(self.select_tab)  # Creating a main frame in the select_tab
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_select_tab()
        self.setup_graph_tab()
        self.setup_team_tab()

        self.main_frame = ttk.Frame(self.select_tab)  # Assuming you want this in the select_tab for now
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Make sure to setup bindings after all components are initialized
        self.controller.setup_bindings()

        self.tab_control.pack(expand=1, fill="both") 


    def setup_select_tab(self):
        # Organize layout with frames for different sections
        top_frame = ttk.Frame(self.select_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # Search Bar at the top
        ttk.Label(top_frame, text="Search Pokémon:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(top_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>')

        filter_frame = ttk.Frame(self.select_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Type Filter
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        types = ['All'] + sorted(self.pokemon_data['Type 1'].dropna().unique().tolist())
        self.type_combobox = ttk.Combobox(filter_frame, textvariable=self.type_var, values=types, state="readonly")
        self.type_combobox.current(0)  # set to 'All'
        self.type_combobox.pack(side=tk.LEFT, padx=5)
        self.type_combobox.bind('<<ComboboxSelected>>', self.update_pokemon_list)

        ttk.Label(filter_frame, text="Stat:").pack(side=tk.LEFT)
        self.stat_var = tk.StringVar()
        stats = ['All', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        self.stat_combobox = ttk.Combobox(filter_frame, textvariable=self.stat_var, values=stats, state="readonly")
        self.stat_combobox.current(0)  # set to 'All'
        self.stat_combobox.pack(side=tk.LEFT, padx=5)

        # Stat Threshold
        ttk.Label(filter_frame, text="Min Value:").pack(side=tk.LEFT)
        self.stat_threshold_var = tk.IntVar()
        self.min_value_entry = ttk.Entry(filter_frame, textvariable=self.stat_threshold_var)
        self.min_value_entry.pack(side=tk.LEFT, padx=5)


        # Sorting options
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="Name")
        ttk.Radiobutton(filter_frame, text="Name", variable=self.sort_var, value="Name", command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Type", variable=self.sort_var, value="Type", command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Number", variable=self.sort_var, value="Number", command=self.update_pokemon_list).pack(side=tk.LEFT)

        # Pokémon listbox with scrollbar
        listbox_frame = ttk.Frame(self.select_tab)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.pokemon_listbox = tk.Listbox(listbox_frame, height=20)
        self.pokemon_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.pokemon_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pokemon_listbox.config(yscrollcommand=scrollbar.set)
        self.populate_pokemon_listbox()

        # Frame for selected Pokémon list and management buttons
        management_frame = ttk.Frame(self.select_tab)
        management_frame.pack(fill=tk.X, expand=True, padx=15, pady=10)

        self.selected_team_listbox = tk.Listbox(management_frame, height=5, width = 10)
        self.selected_team_listbox.pack(fill=tk.X, expand=True)

        confirm_team_button = ttk.Button(self.select_tab, text="Confirm Team", command=self.confirm_team)
        confirm_team_button.pack(expand=True)

        add_button = ttk.Button(self.select_tab, text="Add Pokémon", command=self.add_pokemon)
        add_button.pack(expand=True)

        delete_button = ttk.Button(self.select_tab, text="Delete Selected Pokémon", command=self.delete_selected_pokemon)
        delete_button.pack(expand=True)

        clear_team_button = ttk.Button(self.select_tab, text="Clear Team", command=self.clear_team)
        clear_team_button.pack(expand=True)

        self.update_pokemon_list()  # Initial update to populate list

    def add_pokemon(self):
        selected_indices = self.pokemon_listbox.curselection()
        for index in selected_indices:
            pokemon = self.pokemon_listbox.get(index)
            if pokemon not in self.current_team:
                self.current_team.append(pokemon)
                self.selected_team_listbox.insert(tk.END, pokemon)
                self.update_graph_listbox() 
    def delete_selected_pokemon(self):
        selected_indices = self.selected_team_listbox.curselection()
        for index in reversed(selected_indices):  # Start from end to avoid index shifting
            pokemon_to_remove = self.selected_team_listbox.get(index)
            self.selected_team_listbox.delete(index)
            if pokemon_to_remove in self.current_team:
                self.current_team.remove(pokemon_to_remove)
                self.update_graph_listbox() 

    def clear_team(self):
        self.selected_team_listbox.delete(0, tk.END)
        self.current_team = []  # Reset the current team list
        self.update_graph_listbox()  # Refresh related UI components

    def confirm_team(self):
        if self.current_team:
            details = [(pokemon, self.pokemon_data[pokemon]['Type 1'], self.pokemon_data[pokemon]['Type 2'], self.pokemon_data[pokemon]['Total'])
                       for pokemon in self.current_team if pokemon in self.pokemon_data]
            self.update_graph_listbox(details)
            messagebox.showinfo("Team Confirmed", f"Your team with {len(self.current_team)} Pokémon has been confirmed.")
        else:
            messagebox.showerror("No Team", "No Pokémon have been added to the team.")
    def update_graph_listbox(self):
        self.graph_listbox.delete(0, tk.END)  # Clear the list box first
        for pokemon_name in self.current_team:
            pokemon_data = self.pokemon_data[self.pokemon_data['Name'] == pokemon_name]
            if not pokemon_data.empty:
                entry = f"{pokemon_name} - Type: {pokemon_data['Type 1'].values[0]}, Stats: HP {pokemon_data['HP'].values[0]}, Atk {pokemon_data['Attack'].values[0]}"
                self.graph_listbox.insert(tk.END, entry)

    def setup_graph_tab(self):
        self.canvas = None
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Statistical Data')
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.graph_listbox = tk.Listbox(self.graph_tab, height=10)
        self.graph_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_graph_listbox()

        save_team_button = ttk.Button(self.graph_tab, text="Save Current Team", command=self.save_team)
        save_team_button.pack(pady=5, expand=True)

    def display_hp_distribution(self, data):
        self.ax.clear()
        sns.histplot(data['HP'], kde=True, ax=self.ax)
        self.ax.set_title('HP Distribution')
        self.ax.set_xlabel('HP')
        self.ax.set_ylabel('Frequency')
        self.canvas.draw()

    def setup_team_tab(self):
        default_data = self.controller.initialize_pokemon_list()  # Ensure this method exists and returns the initial full list
        self.update_pokemon_list(default_data)

        # Create a frame inside the team tab for layout
        team_frame = ttk.Frame(self.team_tab)
        team_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a listbox to display current team members
        self.team_listbox = tk.Listbox(team_frame, height=10)
        self.team_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.update_saved_teams_tab()

        # Add a scrollbar to the listbox
        scrollbar = tk.Scrollbar(team_frame, orient="vertical", command=self.team_listbox.yview)
        self.team_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a frame for buttons
        button_frame = ttk.Frame(team_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Add button to confirm the selection of the team
        self.confirm_team_button = ttk.Button(button_frame, text="Delete Selected Team", command=self.on_delete_button_clicked)
        self.confirm_team_button.pack(padx=5, pady=5)

        view_graph_button = ttk.Button(button_frame, text="View Graph for Selected Team")
        view_graph_button.pack(padx=5, pady=5)

    def save_team(self):
        team_name = simpledialog.askstring("Team Name", "Enter a name for the current team:")
        if team_name:
            self.controller.save_current_team(team_name, self.current_team)
            self.update_saved_teams_tab()

    def display_stat_correlations(self, data):
        self.ax.clear()
        corr = data[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].corr()
        sns.heatmap(corr, annot=True, ax=self.ax)
        self.ax.set_title('Stat Correlations')
        self.canvas.draw()

    def update_pokemon_list(self, event=None):
        try:
            type_filter = self.type_var.get()
            stat = self.stat_combobox.get()
            stat_threshold = self.stat_threshold_var.get()
            sort_by = self.sort_var.get()
            search_term = self.search_entry.get().strip().lower()  # Retrieve current text from search entry

            filtered_data = self.pokemon_data.copy()

            # Filter by type if not 'All'
            if type_filter != "All":
                filtered_data = filtered_data[(filtered_data['Type 1'] == type_filter) | (filtered_data['Type 2'] == type_filter)]

            # Filter by stat if not 'All' and threshold is set
            if stat != "All" and stat_threshold > 0:
                filtered_data = filtered_data[filtered_data[stat] >= stat_threshold]

            # Apply search filter
            if search_term:
                filtered_data = filtered_data[filtered_data['Name'].str.lower().str.contains(search_term)]

            # Sorting
            if sort_by == "Name":
                filtered_data = filtered_data.sort_values(by="Name")
            elif sort_by == "Type":
                filtered_data = filtered_data.sort_values(by=["Type 1", "Type 2", "Name"])
            elif sort_by == "Number":
                filtered_data = filtered_data.sort_values(by="#")

            self.pokemon_listbox.delete(0, tk.END)  # Clear existing entries
            if filtered_data.empty:
                self.pokemon_listbox.insert(tk.END, "No results found.")
            else:
                for _, row in filtered_data.iterrows():
                    self.pokemon_listbox.insert(tk.END, row['Name'])

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def populate_pokemon_listbox(self):
        pokemon_names = self.controller.model.get_pokemon_names()
        self.pokemon_listbox.delete(0, 'end')
        for name in pokemon_names:
            self.pokemon_listbox.insert('end', name) 

    def update_saved_teams_tab(self):
        self.team_listbox.delete(0, tk.END)  # Clear all current entries
        for _, row in self.model.saved_teams.iterrows():
            team_info = f"{row['Team Name']} - {row['Members']}"
            self.team_listbox.insert(tk.END, team_info)  # Insert updated info

    def delete_selected_team(self):
        selected_index = self.team_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]  # Get the actual index as an integer
            self.controller.delete_team(selected_index)  # Pass this index to the controller
            self.update_saved_teams_tab()
        else:
            messagebox.showerror("Error", "No team selected.")

    def on_delete_button_clicked(self):
        selected_index = self.team_listbox.curselection()
        if selected_index:
            self.controller.delete_team(selected_index[0])
            self.update_saved_teams_tab()  
        else:
            messagebox.showerror("Error", "Please select a team to delete.")

    def refresh_view(self):
        self.update_saved_teams_tab() 