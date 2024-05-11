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

    # UI Setup
    def setup_ui(self):
        """Creates the different UI elements like tabs"""
        self.tab_control = ttk.Notebook(self.master)

        self.select_tab = ttk.Frame(self.tab_control)
        self.graph_tab = ttk.Frame(self.tab_control)
        self.team_tab = ttk.Frame(self.tab_control)
        self.team_graph_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.select_tab, text='Select Pokémon')
        self.tab_control.add(self.graph_tab, text='Graph View')
        self.tab_control.add(self.team_graph_tab, text='Team Graph View')
        self.tab_control.add(self.team_tab, text='Saved Team')

        self.main_frame = ttk.Frame(self.select_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_select_tab()
        self.setup_graph_tab()
        self.setup_team_graph_tab()
        self.setup_team_tab()

        self.main_frame = ttk.Frame(self.select_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.controller.setup_bindings()

        self.tab_control.pack(expand=1, fill="both")

    def setup_select_tab(self):
        """Sets up the UI elements specific to the "Select Pokémon" tab"""
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
        self.type_combobox = ttk.Combobox(filter_frame,textvariable=self.type_var,
                                          values=types, state="readonly")
        self.type_combobox.current(0)  # set to 'All'
        self.type_combobox.pack(side=tk.LEFT, padx=5)
        self.type_combobox.bind('<<ComboboxSelected>>', self.update_pokemon_list)

        ttk.Label(filter_frame, text="Stat:").pack(side=tk.LEFT)
        self.stat_var = tk.StringVar()
        stats = ['All', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        self.stat_combobox = ttk.Combobox(filter_frame, textvariable=self.stat_var,
                                          values=stats, state="readonly")
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
        ttk.Radiobutton(filter_frame, text="Name", variable=self.sort_var,
                        value="Name", command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Type", variable=self.sort_var, value="Type",
                        command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Number", variable=self.sort_var, value="Number",
                        command=self.update_pokemon_list).pack(side=tk.LEFT)

        # Pokémon listbox with scrollbar
        listbox_frame = ttk.Frame(self.select_tab)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.pokemon_listbox = tk.Listbox(listbox_frame, height=20)
        self.pokemon_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical",
                                 command=self.pokemon_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pokemon_listbox.config(yscrollcommand=scrollbar.set)
        self.populate_pokemon_listbox()

        # Frame for selected Pokémon list and management buttons
        management_frame = ttk.Frame(self.select_tab)
        management_frame.pack(fill=tk.X, expand=True, padx=15, pady=10)

        self.selected_team_listbox = tk.Listbox(management_frame, height=5, width=10)
        self.selected_team_listbox.pack(fill=tk.X, expand=True)

        confirm_team_button = ttk.Button(self.select_tab, text="Confirm Team",
                                         command=self.confirm_team)
        confirm_team_button.pack(expand=True, pady=2)

        add_button = ttk.Button(self.select_tab, text="Add Pokémon", command=self.add_pokemon)
        add_button.pack(expand=True, pady=2)

        delete_button = ttk.Button(self.select_tab, text="Delete Selected Pokémon",
                                   command=self.delete_selected_pokemon)
        delete_button.pack(expand=True, pady=2)

        clear_team_button = ttk.Button(self.select_tab, text="Clear Team", command=self.clear_team)
        clear_team_button.pack(expand=True, pady=2)

        quit_button = ttk.Button(self.select_tab, text="Quit", command=self.master.quit)
        quit_button.pack(expand=True, pady=2)

        self.update_pokemon_list()

    def setup_graph_tab(self):
        """Sets up the UI elements for the "Graph View" tab"""
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.graph_tab)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

        # Graph Type Selection
        ttk.Label(self.button_frame, text="Graph Type:").pack(side=tk.LEFT, padx=5)
        self.graph_type_var = tk.StringVar(value="Pie")
        graph_types = ["Pie", "Bar", "Stats by Type", "Correlation Matrix", "Hp Distribution"]
        self.graph_type_combobox = ttk.Combobox(self.button_frame, textvariable=self.graph_type_var,
                                                values=graph_types, state="readonly")
        self.graph_type_combobox.pack(side=tk.LEFT, padx=5, pady=5)

        # Attribute Selection
        ttk.Label(self.button_frame, text="Attribute for Graph:").pack(side=tk.LEFT, padx=5)
        self.graph_attribute_var = tk.StringVar()
        attributes = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        self.graph_attribute_combobox = ttk.Combobox(self.button_frame,
                textvariable=self.graph_attribute_var, values=attributes, state="readonly")
        self.graph_attribute_combobox.current(0)
        self.graph_attribute_combobox.pack(side=tk.LEFT, padx=5)

        # Type selection for stats plotting (only enabled for certain graph types)
        ttk.Label(self.button_frame, text="Type for Stats:").pack(side=tk.LEFT, padx=5)
        self.stats_type_var = tk.StringVar()
        types = ['All'] + sorted(self.pokemon_data['Type 1'].dropna().unique().tolist())
        self.stats_type_combobox = ttk.Combobox(self.button_frame, textvariable=self.stats_type_var,
                                                values=types, state="readonly")
        self.stats_type_combobox.current(0)
        self.stats_type_combobox.pack(side=tk.LEFT, padx=5)

        self.prepare_plot_area()

        self.graph_listbox = tk.Listbox(self.graph_tab, height=10)
        self.graph_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_graph_listbox()

        self.low_button_frame = ttk.Frame(self.graph_tab)
        self.low_button_frame.pack(fill=tk.BOTH, expand=True)

        save_team_button = ttk.Button(self.low_button_frame, text="Save Current Team",
                                      command=self.save_team)
        save_team_button.pack(side=tk.LEFT, padx=3, pady=5, expand=True)

        quit_button = ttk.Button(self.low_button_frame, text="Quit", command=self.master.quit)
        quit_button.pack(side=tk.LEFT, padx=3, pady=5, expand=True)

    def setup_team_graph_tab(self):
        """Setup UI components for the team graph tab."""
        frame = ttk.Frame(self.team_graph_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Dropdown to select a team
        self.team_selection_var = tk.StringVar()
        teams = self.model.load_all_team_names()
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

    def setup_team_tab(self):
        """Sets up the UI elements for the "Saved Team" tab"""
        default_data = self.controller.initialize_pokemon_list()
        self.update_pokemon_list(default_data)

        # Create a frame inside the team tab for layout
        team_frame = ttk.Frame(self.team_tab)
        team_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a listbox to display current team members
        self.team_listbox = tk.Listbox(team_frame, height=10)
        self.team_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.update_saved_teams_tab()

        # Create a frame for buttons
        button_frame = ttk.Frame(team_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Add button to confirm the selection of the team
        self.confirm_team_button = ttk.Button(button_frame, text="Delete Selected Team",
                                                command=self.on_delete_button_clicked)
        self.confirm_team_button.pack(padx=5, pady=5)

        self.quit_button = ttk.Button(button_frame, text="Quit", command=self.master.quit)
        self.quit_button.pack(padx=5, pady=5)

    # Data Visualization

    def plot_pie_chart(self, data, attribute):
        """Draws a pie chart of the given attribute for the selected Pokémon."""
        self.prepare_plot_area()
        total = data[attribute].sum()

        if total > 0:
            sizes = data[attribute].replace(0, np.nan).dropna()
            labels = data.loc[sizes.index, 'Name']

            # Check if there's valid data after filtering out zeros
            if sizes.empty:
                self.ax.text(0.5, 0.5, 'No valid data to display', horizontalalignment='center',
                            verticalalignment='center', transform=self.ax.transAxes)
                self.ax.set_title(f'No data available for {attribute}')
            else:
                # Draw the pie chart
                wedges, texts, autotexts = self.ax.pie(sizes, labels=labels,
                                                    autopct=lambda p: f'{p:.1f}% \
                                                        \n({p/100 * total:.1f})',
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

    def plot_bar_chart(self, data, attribute):
        """Creates and displays a bar chart for the specified 
            attribute of the selected Pokémon"""
        self.ax.bar(data['Name'], data[attribute], color='skyblue')
        self.ax.set_title(f'{attribute} Distribution')
        self.ax.set_ylabel(attribute)
        self.ax.set_xticklabels(data['Name'], rotation=45, ha="right")

    def plot_hp_distribution(self, data):
        """Plot the distribution of HP among Pokémon using a histogram."""
        self.prepare_plot_area()
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
        """Plot bar graphs for Pokémon stats by their type using seaborn."""
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
        """Displays statistical correlations as a heatmap."""
        self.prepare_plot_area()  # Make sure plotting area is clear

        # Calculate the correlation matrix.
        corr = data[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].corr()

        # Create the heatmap with annotations and no colorbar.
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', ax=self.ax, cbar=False)

        # Set the title and refresh the canvas.
        self.ax.set_title('Stat Correlations')
        self.canvas.draw()

    def prepare_plot_area(self):
        """Prepare the graph area by clearing any existing graphs."""
        if hasattr(self, 'canvas'):
            self.ax.clear()
        else:
            self.figure = Figure(figsize=(6, 4), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, self.graph_tab)
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas.draw()

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

    def prepare_plot_area_team(self):
        """Prepare the graph area for the team graph view"""
        if hasattr(self, 'team_canvas'):
            self.team_canvas.get_tk_widget().destroy()  # Remove old canvas

        # Create a new figure for team graphs
        self.team_figure = Figure(figsize=(6, 4), dpi=100)
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

    # User Interaction

    def add_pokemon(self):
        """Adds a selected Pokémon to the current team and updates the team listbox"""
        selected_indices = self.pokemon_listbox.curselection()
        for index in selected_indices:
            pokemon = self.pokemon_listbox.get(index)
            if pokemon not in self.current_team:
                self.current_team.append(pokemon)
                self.selected_team_listbox.insert(tk.END, pokemon)
                self.update_graph_listbox()

    def delete_selected_pokemon(self):
        """Removes the selected Pokémon from the current team and updates the team listbox"""
        selected_indices = self.selected_team_listbox.curselection()
        for index in reversed(selected_indices):  # Start from end to avoid index shifting
            pokemon_to_remove = self.selected_team_listbox.get(index)
            self.selected_team_listbox.delete(index)
            if pokemon_to_remove in self.current_team:
                self.current_team.remove(pokemon_to_remove)
                self.update_graph_listbox()

    def clear_team(self):
        """Clears the current team selection and listbox"""
        self.selected_team_listbox.delete(0, tk.END)
        self.current_team = []  # Reset the current team list
        self.update_graph_listbox()  # Refresh related UI components

    def confirm_team(self):
        """Prompts the user for confirmation of the selected team"""
        if not self.current_team:
            messagebox.showerror("No Team", "No Pokémon have been added to the team.")
            return
        messagebox.showinfo("Team Confirmed", f"Your team with \
                            {len(self.current_team)} Pokémon has been confirmed.")

    def update_graph_listbox(self):
        """Updates the listbox in the "Graph View" tab
        to show information about the Pokémon in the current team"""
        self.graph_listbox.delete(0, tk.END)
        for pokemon_name in self.current_team:
            pokemon_data = self.pokemon_data[self.pokemon_data['Name'] == pokemon_name]
            if not pokemon_data.empty:
                entry = f"{pokemon_name} - Type: {pokemon_data['Type 1'].values[0]}, " \
                        f"Stats: HP {pokemon_data['HP'].values[0]}," \
                        f"Atk {pokemon_data['Attack'].values[0]}"
                self.graph_listbox.insert(tk.END, entry)

    def save_team(self):
        """Save team with team's name"""
        team_name = simpledialog.askstring("Team Name", "Enter a name for the current team:")
        if team_name:
            self.controller.save_current_team(team_name, self.current_team)
            self.update_saved_teams_tab()

    def update_pokemon_list(self, event=None):
        """Filter the pokemons' name list"""
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
            filtered_data = filtered_data[filtered_data['Name'].str.lower() \
                                            .str.contains(search_term)]

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

    def populate_pokemon_listbox(self):
        """Make pokemons' name list into original list"""
        pokemon_names = self.controller.model.get_pokemon_names()
        self.pokemon_listbox.delete(0, 'end')
        for name in pokemon_names:
            self.pokemon_listbox.insert('end', name)

    def update_saved_teams_tab(self):
        """Add saved team into saved tesm tab"""
        self.team_listbox.delete(0, tk.END)
        for _, row in self.model.saved_teams.iterrows():
            team_info = f"{row['Team Name']} - {row['Members']}"
            self.team_listbox.insert(tk.END, team_info)

    def delete_selected_team(self):
        """Deleted the selected saved team"""
        selected_index = self.team_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]  # Get the actual index as an integer
            self.controller.delete_team(selected_index)  # Pass this index to the controller
            self.update_saved_teams_tab()
        else:
            messagebox.showerror("Error", "No team selected.")

    def on_delete_button_clicked(self):
        """Click for deletion"""
        selected_index = self.team_listbox.curselection()
        if selected_index:
            self.controller.delete_team(selected_index[0])
            self.update_saved_teams_tab()
        else:
            messagebox.showerror("Error", "Please select a team to delete.")

    def trigger_graph_drawing(self):
        """Draw graph from provided attribute"""
        attribute = self.graph_attribute_var.get()  # This should be a single string
        graph_type = self.graph_type_var.get()
        pokemon_type = self.stats_type_var.get()
        current_team = self.get_current_team()

        self.prepare_plot_area()

        if not current_team and graph_type not in ["Stats by Type",
                                                   "Correlation Matrix", "Hp Distribution"]:
            messagebox.showinfo("No Data", "No Pokémon in the current team to draw a graph.")
            return

        if graph_type == "Stats by Type" or graph_type == "Correlation Matrix" \
                                        or graph_type == "Hp Distribution":
            team_data = self.pokemon_data if pokemon_type == "All" else \
            self.pokemon_data[self.pokemon_data['Type 1'] == pokemon_type]
            if team_data.empty:
                messagebox.showinfo("No Data", "No Pokémon data available.")
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
                self.plot_pie_chart(team_data, attribute)
            elif graph_type == "Bar":
                self.plot_bar_chart(team_data, attribute)

        self.canvas.draw()

    def get_current_team(self):
        """Return list of current team"""
        if isinstance(self.current_team, str):
            return [self.current_team]
        return self.current_team

    def update_team_graph(self, event=None):
        """Create fraph from selected team"""
        team_name = self.team_selection_var.get()
        self.prepare_plot_area_team()
        if team_name:
            team_data = self.model.get_team_data(team_name)
            self.plot_attribute_distribution_for_selected_pokemon(team_data)
