# view.py
"""File for View class"""
import tkinter as tk
from tkinter import ttk, messagebox,  simpledialog
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np

class PokeBuilderView:
    """View class for this program"""
    def __init__(self, master, model, pokemon_data, controller):
        self.controller = controller
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
        self.team_graph_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.select_tab, text='Select Pokémon')
        self.tab_control.add(self.graph_tab, text='Graph View')
        self.tab_control.add(self.team_tab, text='Saved Team')
        self.tab_control.add(self.team_graph_tab, text='Team Graph View') 

        self.main_frame = ttk.Frame(self.select_tab)  # Creating a main frame in the select_tab
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_select_tab()
        self.setup_graph_tab()
        self.setup_team_tab()
        self.setup_team_graph_tab()

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

        quit_button = ttk.Button(self.select_tab, text="Quit", command=self.master.quit)
        quit_button.pack(expand=True)

        self.update_pokemon_list()  # Initial update to populate list

    def add_pokemon(self):
        selected_indices = self.pokemon_listbox.curselection()
        print(f"Selected indices: {selected_indices}")
        for index in selected_indices:
            pokemon = self.pokemon_listbox.get(index)
            print(f"Adding Pokémon: {pokemon}")
            if pokemon not in self.current_team:
                self.current_team.append(pokemon)
                self.selected_team_listbox.insert(tk.END, pokemon)
                self.update_graph_listbox() 

        print("Current Team after adding:", self.current_team)  # Debugging to check the current team list

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
        if not self.current_team:
            messagebox.showerror("No Team", "No Pokémon have been added to the team.")
            return
        print("Team Confirmed with:", self.current_team)
        messagebox.showinfo("Team Confirmed", f"Your team with {len(self.current_team)} Pokémon has been confirmed.")
    def update_graph_listbox(self):
        self.graph_listbox.delete(0, tk.END)  # Clear the list box first
        for pokemon_name in self.current_team:
            pokemon_data = self.pokemon_data[self.pokemon_data['Name'] == pokemon_name]
            if not pokemon_data.empty:
                entry = f"{pokemon_name} - Type: {pokemon_data['Type 1'].values[0]}, Stats: HP {pokemon_data['HP'].values[0]}, Atk {pokemon_data['Attack'].values[0]}"
                self.graph_listbox.insert(tk.END, entry)

    def setup_graph_tab(self):
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.graph_tab)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

        # Graph Type Selection
        ttk.Label(self.button_frame, text="Graph Type:").pack(side=tk.LEFT, padx=5)
        self.graph_type_var = tk.StringVar(value="Pie")
        graph_types = ["Pie", "Bar", "Stats by Type", "Correlation Matrix", "Hp Distribution"]
        self.graph_type_combobox = ttk.Combobox(self.button_frame, textvariable=self.graph_type_var, values=graph_types, state="readonly")
        self.graph_type_combobox.pack(side=tk.LEFT, padx=5, pady=5)

        # Attribute Selection
        ttk.Label(self.button_frame, text="Attribute for Graph:").pack(side=tk.LEFT, padx=5)
        self.graph_attribute_var = tk.StringVar()
        attributes = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        self.graph_attribute_combobox = ttk.Combobox(self.button_frame, textvariable=self.graph_attribute_var, values=attributes, state="readonly")
        self.graph_attribute_combobox.current(0)
        self.graph_attribute_combobox.pack(side=tk.LEFT, padx=5)

        # Type selection for stats plotting (only enabled for certain graph types)
        ttk.Label(self.button_frame, text="Type for Stats:").pack(side=tk.LEFT, padx=5)
        self.stats_type_var = tk.StringVar()
        types = ['All'] + sorted(self.pokemon_data['Type 1'].dropna().unique().tolist())
        self.stats_type_combobox = ttk.Combobox(self.button_frame, textvariable=self.stats_type_var, values=types, state="readonly")
        self.stats_type_combobox.current(0)
        self.stats_type_combobox.pack(side=tk.LEFT, padx=5)

        # Button to trigger graph drawing
        draw_graph_button = ttk.Button(self.button_frame, text="Draw Graph", command=self.trigger_graph_drawing)
        draw_graph_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.prepare_plot_area()

        self.graph_listbox = tk.Listbox(self.graph_tab, height=10)
        self.graph_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_graph_listbox()

        self.low_button_frame = ttk.Frame(self.graph_tab)
        self.low_button_frame.pack(fill=tk.BOTH, expand=True)

        save_team_button = ttk.Button(self.low_button_frame, text="Save Current Team", command=self.save_team)
        save_team_button.pack(side=tk.LEFT, padx=3, pady=5, expand=True)

        quit_button = ttk.Button(self.low_button_frame, text="Quit", command=self.master.quit)
        quit_button.pack(side=tk.LEFT, padx=3, pady=5, expand=True)


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

        view_graph_button = ttk.Button(button_frame, text="Load Selected Team", command=self.load_selected_team)
        view_graph_button.pack(padx=5, pady=5)

        self.quit_button = ttk.Button(button_frame, text="Quit", command=self.master.quit)
        self.quit_button.pack(padx=5, pady=5)

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
            search_term = self.search_entry.get().strip().lower()

            filtered_data = self.pokemon_data.copy()

            # Filter by type if not 'All'
            if type_filter != "All":
                filtered_data = filtered_data[(filtered_data['Type 1'] == type_filter)
                    | (filtered_data['Type 2'] == type_filter)]

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

    def trigger_graph_drawing(self):
        self.prepare_plot_area()

        attribute = self.graph_attribute_var.get()  # This should be a single string
        graph_type = self.graph_type_var.get()
        pokemon_type = self.stats_type_var.get()
        current_team = self.get_current_team()

        if not current_team and graph_type not in ["Stats by Type", "Correlation Matrix", "Hp Distribution"]:
            messagebox.showinfo("No Data", "No Pokémon in the current team to draw a graph.")
            return

        if graph_type == "Stats by Type" or graph_type == "Correlation Matrix" or graph_type == "Hp Distribution":
            team_data = self.pokemon_data if pokemon_type == "All" else self.pokemon_data[self.pokemon_data['Type 1'] == pokemon_type]
            if team_data.empty:
                messagebox.showinfo("No Data", "No Pokémon data available for the selected options.")
                return
            if graph_type == "Stats by Type":
                self.plot_stats_by_type(team_data, attribute)  # Pass attribute directly
            elif graph_type == "Correlation Matrix":
                self.plot_correlations(team_data)
            elif graph_type == "Hp Distribution":
                self.plot_hp_distribution(team_data)
        else:
            team_data = self.model.get_selected_pokemon_data(current_team)
            if team_data.empty:
                messagebox.showinfo("No Data", "No Pokémon data available to draw the graph.")
                return
            if graph_type == "Pie":
                self.draw_pie_chart(team_data, attribute)
            elif graph_type == "Bar":
                self.draw_bar_chart(team_data, attribute)

        self.canvas.draw()

    def get_current_team(self):
        # Ensure this always returns a list
        if isinstance(self.current_team, str):
            return [self.current_team]  # Convert string to list if needed
        return self.current_team

    def draw_pie_chart(self, data, attribute):
        """Draws a pie chart of the given attribute for the selected Pokémon."""
        # Prepare the plot area first
        self.prepare_plot_area()
        
        # Sum up the total for the specified attribute to use in percentage calculations
        total = data[attribute].sum()
        
        if total > 0:
            # Extract non-zero sizes and corresponding labels
            sizes = data[attribute].replace(0, np.nan).dropna()  # Remove zeros to avoid issues in pie chart
            labels = data.loc[sizes.index, 'Name']

            # Check if there's valid data after filtering out zeros
            if sizes.empty:
                self.ax.text(0.5, 0.5, 'No valid data to display', horizontalalignment='center',
                            verticalalignment='center', transform=self.ax.transAxes)
                self.ax.set_title(f'No data available for {attribute}')
            else:
                # Draw the pie chart
                wedges, texts, autotexts = self.ax.pie(sizes, labels=labels,
                                                    autopct=lambda p: f'{p:.1f}%\n({p/100 * total:.1f})',
                                                    startangle=140, colors=plt.cm.tab20.colors)

                # Ensure the pie chart is drawn as a circle
                self.ax.axis('equal')
                self.ax.set_title(f'Proportion of {attribute.capitalize()} among Selected Pokémon')
        else:
            self.ax.text(0.5, 0.5, 'All values are zero', horizontalalignment='center',
                        verticalalignment='center', transform=self.ax.transAxes)
            self.ax.set_title(f'No valid data for {attribute}')

        # Redraw the canvas with the updated plot
        self.canvas.draw()


    def draw_bar_chart(self, data, attribute):
        self.ax.bar(data['Name'], data[attribute], color='skyblue')
        self.ax.set_title(f'{attribute} Distribution')
        self.ax.set_ylabel(attribute)
        self.ax.set_xticklabels(data['Name'], rotation=45, ha="right")

    def prepare_plot_area(self):
            """Prepare the graph area by clearing any existing graphs and setting up for new plots, reusing the canvas if it already exists."""
            if hasattr(self, 'canvas'):
                # If the canvas exists, clear the existing axes for new drawings
                self.ax.clear()
            else:
                # Create a new figure for general graphs if the canvas does not exist
                self.figure = Figure(figsize=(8, 6), dpi=100)
                self.ax = self.figure.add_subplot(111)

                # Create a new canvas specifically for the graph view tab
                self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Placeholder text or initial graph setup
            self.ax.text(0.5, 0.5, 'Select graph type and attribute, then click "Draw Graph"',
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes,
                        color='gray', alpha=0.5)

            # Redraw the canvas to reflect changes
            self.canvas.draw()

    def plot_hp_distribution(self, data):
        """
        Plot the distribution of HP among Pokémon using a 
        histogram and density plot within the app's canvas.

        Parameters:
            data (DataFrame): The dataset containing Pokémon information.
        """
        self.prepare_plot_area()  # Prepare the plotting area, ensuring it's clear and ready for a new plot
        if not data.empty:
            sns.histplot(data['HP'], kde=True, color='skyblue', bins=30, ax=self.ax)
            self.ax.set_title('Distribution of HP Among Pokémon')
            self.ax.set_xlabel('HP')
            self.ax.set_ylabel('Frequency')
        else:
            self.ax.text(0.5, 0.5, 'No data to display', ha='center',
                    va='center', transform=self.ax.transAxes)
            self.ax.set_title('No data available')

        self.canvas.draw()  # Update the canvas to show the new plot

    def plot_stats_by_type(self, data, attribute):
        """
        Plot bar graphs for Pokémon stats by their type using seaborn.

        Parameters:
            data (DataFrame): Filtered data based on selected type.
            attribute (str): Stat to plot.
        """
        self.prepare_plot_area()
        data_grouped = data.groupby('Type 1')[attribute].mean().reset_index()

        if not data_grouped.empty:
            sns.barplot(x='Type 1', y=attribute, data=data_grouped, ax=self.ax, palette='tab10')
            self.ax.set_title(f'{attribute.capitalize()} Distribution by Type')
            self.ax.set_ylabel(f'Mean {attribute.capitalize()}')
            self.ax.set_xticklabels(data_grouped['Type 1'], rotation=45, ha="right")
        else:
            self.ax.text(0.5, 0.5, 'No data to display', ha='center',
                         va='center', transform=self.ax.transAxes)
            self.ax.set_title(f'No data available for {attribute.capitalize()}')

        self.canvas.draw()

    def plot_correlations(self, data):
        corr_matrix = data[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=self.ax)
        self.ax.set_title('Correlation Matrix of Pokémon Stats')
        self.canvas.draw()

    def show_figure(self, fig):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_selected_team(self):
        selected_indices = self.team_listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_team_name = self.model.get_team_name_by_index(selected_index)
            self.current_team = self.model.load_team(selected_team_name)
            if self.current_team:
                team_data = self.model.get_pokemon_data_by_names(self.current_team)
                self.plot_attribute_distribution_for_selected_pokemon(team_data)
            else:
                self.display_message("Info", "No team members found for the selected team.")
        else:
            self.display_error("Please select a team first.")

    def display_message(self, title, message):
        messagebox.showinfo(title, message)

    def display_error(self, message):
        messagebox.showerror("Error", message)

    def plot_attribute_distribution_for_selected_pokemon(self, team_data):
        """Plot attribute distribution for the selected Pokémons' team using pie charts."""
        # Prepare the plot area specifically for the team graph view tab
        self.prepare_plot_area_team()

        attributes = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']

        # Create subplots within the team figure
        self.team_figure.clear()  # Clear the figure to avoid overlap of plots
        axes = self.team_figure.subplots(2, 3)
        axes = axes.flatten()  # Flatten the axes array for easy iteration

        for i, attribute in enumerate(attributes):
            if attribute in team_data.columns:
                pokemon_max = team_data.set_index('Name')[attribute]
                total_max = pokemon_max.sum()

                if total_max > 0:
                    # Calculate percentages for pie slices
                    axes[i].pie(pokemon_max, labels=pokemon_max.index,
                                autopct=lambda p: f'{p:.1f}%\n{p/100 * total_max:.1f}',
                                startangle=140)
                    axes[i].set_title(f'{attribute.capitalize()} Distribution')
                    axes[i].axis('equal')  # Ensure pie chart is drawn as a circle
                else:
                    axes[i].text(0.5, 0.5, 'No data available',
                                horizontalalignment='center', verticalalignment='center')
                    axes[i].set_title(f'{attribute.capitalize()} Distribution')
            else:
                axes[i].text(0.5, 0.5, 'Attribute not found', ha='center')
                axes[i].set_title(f'{attribute.capitalize()} Distribution')

        # Tighten layout and redraw the canvas with the new plots
        self.team_figure.tight_layout()
        self.team_canvas.draw()

    def setup_team_graph_tab(self):
        """Setup UI components for the team graph tab."""
        frame = ttk.Frame(self.team_graph_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dropdown to select a team
        self.team_selection_var = tk.StringVar()
        teams = self.model.load_all_team_names()  # Correctly use the new method
        ttk.Label(frame, text="Select Team:").pack(side=tk.LEFT, padx=5)
        self.team_combobox = ttk.Combobox(frame, textvariable=self.team_selection_var,
                                          values=teams, state="readonly")
        self.team_combobox.pack(side=tk.LEFT, padx=5)
        self.team_combobox.bind('<<ComboboxSelected>>', self.update_team_graph)

        # Button to trigger graph update
        draw_button = ttk.Button(frame, text="Draw Graph", command=self.update_team_graph)
        draw_button.pack(side=tk.LEFT, padx=10)

        # Quit button
        quit_button = ttk.Button(frame, text="Quit", command=self.master.quit)
        quit_button.pack(side=tk.RIGHT, padx=10)

        # Placeholder for graphs
        self.team_graph_frame = ttk.Frame(self.team_graph_tab)
        self.team_graph_frame.pack(fill=tk.BOTH, expand=True)
        self.prepare_plot_area_team()

    def prepare_plot_area_team(self):
        """Prepare the graph area for the team graph view by clearing any existing graphs and setting up for new plots."""
        if hasattr(self, 'team_canvas'):
            self.team_canvas.get_tk_widget().destroy()  # Remove old canvas

        # Create a new figure for team graphs
        self.team_figure = Figure(figsize=(8, 6), dpi=100)
        self.team_ax = self.team_figure.add_subplot(111)
        self.team_ax.clear()  # Clear the subplot to ensure it's empty

        # Create a new canvas specifically for the team graph view tab
        self.team_canvas = FigureCanvasTkAgg(self.team_figure, self.team_graph_frame)
        self.team_canvas.draw()
        self.team_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Placeholder text or initial graph setup
        self.team_ax.text(0.5, 0.5, 'Select a team and draw graph',
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.team_ax.transAxes, color='gray', alpha=0.5)
        self.team_canvas.draw()

    def update_team_graph(self, event=None):
        team_name = self.team_selection_var.get()
        self.prepare_plot_area_team()
        if team_name:
            team_data = self.model.get_team_data(team_name)
            # Draw using the specific team graph function
            self.plot_attribute_distribution_for_selected_pokemon(team_data)
