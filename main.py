import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import os

def display_graph_for_team(self, team_data):
    if not team_data.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        
        sns.histplot(team_data['HP'], kde=True, ax=ax)
        ax.set_title('HP Distribution for Selected Team')
        ax.set_xlabel('HP')
        ax.set_ylabel('Frequency')
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)  
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def plot_stat_correlations(data):
    plt.figure(figsize=(10, 8))
    corr = data[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmax=1.0, vmin=-1.0, square=True, linewidths=.5)
    plt.title('Stat Correlations')
    plt.show()

def plot_hp_distribution(data):
    plt.figure(figsize=(8, 6))
    sns.histplot(data['HP'], kde=True, bins=30, color='skyblue')
    plt.title('Distribution of HP')
    plt.xlabel('HP')
    plt.ylabel('Frequency')
    plt.show()

def plot_average_stats_by_type(data):
    plt.figure(figsize=(12, 8))
    avg_stats = data.groupby('Type 1')[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].mean()
    avg_stats.plot(kind='bar')
    plt.title('Average Stats by Type')
    plt.ylabel('Average Stat Values')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_type_composition(data):
    plt.figure(figsize=(8, 6))
    type_counts = data['Type 1'].value_counts()
    type_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('Type Composition')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

class PokeBuilderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Poké Builder")
        self.pokemon_data = pd.read_csv('Pokemon.csv')
        self.pokemon_names = self.pokemon_data['Name'].dropna().unique().tolist() 
        self.canvas = None
        self.current_team = [] 
        if os.path.exists('saved_teams.csv'):
            self.saved_teams = pd.read_csv('saved_teams.csv')
        else:
            self.saved_teams = pd.DataFrame(columns=['Team Name', 'Members'])
        self.setup_ui()
        

    def setup_ui(self):
        tabControl = ttk.Notebook(self.master)
        self.select_tab = ttk.Frame(tabControl)
        self.graph_tab = ttk.Frame(tabControl)
        self.team_tab = ttk.Frame(tabControl)

        tabControl.add(self.select_tab, text='Select Pokémon')
        tabControl.add(self.graph_tab, text='Graph View')
        tabControl.add(self.team_tab, text='Saved Team')
        tabControl.pack(expand=1, fill="both")

        self.setup_select_tab()
        self.setup_graph_tab()
        self.setup_team_tab()

    def setup_select_tab(self):
        # Create a search bar at the top of the select tab
        search_frame = ttk.Frame(self.select_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        search_label = ttk.Label(search_frame, text="Search Pokémon:")
        search_label.pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.filter_pokemon_list)

        filter_frame = ttk.LabelFrame(self.select_tab, text="Filters and Sorting", width=200)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        # Type Filter
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        types = ['All'] + sorted(self.pokemon_data['Type 1'].dropna().unique().tolist())
        self.type_combobox = ttk.Combobox(filter_frame, textvariable=self.type_var, values=types, state="readonly")
        self.type_combobox.current(0)  # set to 'All'
        self.type_combobox.pack(side=tk.LEFT, padx=5)
        self.type_combobox.bind('<<ComboboxSelected>>', self.update_pokemon_list)

        # Stat Filter
        ttk.Label(filter_frame, text="Stat:").pack(side=tk.LEFT)
        self.stat_var = tk.StringVar()
        stats = ['All', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        self.stat_combobox = ttk.Combobox(filter_frame, textvariable=self.stat_var, values=stats, state="readonly")
        self.stat_combobox.current(0)  # set to 'All'
        self.stat_combobox.pack(side=tk.LEFT, padx=5)

        # Stat Threshold
        ttk.Label(filter_frame, text="Min Value:").pack(side=tk.LEFT)
        self.stat_threshold_var = tk.IntVar()
        self.stat_threshold_entry = ttk.Entry(filter_frame, textvariable=self.stat_threshold_var)
        self.stat_threshold_entry.pack(side=tk.LEFT, padx=5)

        # Sorting Options
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="Name")
        ttk.Radiobutton(filter_frame, text="Name", variable=self.sort_var, value="Name", command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Type", variable=self.sort_var, value="Type", command=self.update_pokemon_list).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Number", variable=self.sort_var, value="Number", command=self.update_pokemon_list).pack(side=tk.LEFT)

        self.pokemon_listbox = tk.Listbox(self.select_tab, height=10)
        self.pokemon_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.select_tab, orient="vertical", command=self.pokemon_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pokemon_listbox.config(yscrollcommand=scrollbar.set)
        self.populate_pokemon_listbox()  

        self.selected_team_listbox = tk.Listbox(self.select_tab, height=5)
        self.selected_team_listbox.pack(padx=10, pady=10, fill=tk.X, expand=True)

        confirm_button = ttk.Button(self.select_tab, text="Confirm Team", command=self.confirm_team)
        confirm_button.pack(pady=5, expand=True)

        add_button = ttk.Button(self.select_tab, text="Add Pokémon", command=self.add_pokemon)
        add_button.pack(pady=5, expand=True)

        delete_button = ttk.Button(self.select_tab, text="Delete Selected Pokémon", command=self.delete_selected_pokemon)
        delete_button.pack(pady=5, expand=True)

        clear_team_button = ttk.Button(self.select_tab, text="Clear Team", command=self.clear_team)
        clear_team_button.pack(pady=5, expand=True)
        
        self.update_pokemon_list()

    def populate_pokemon_listbox(self):
        self.pokemon_listbox.delete(0, tk.END)  # Clear current list
        for name in self.pokemon_data:
            self.pokemon_listbox.insert(tk.END, name)  # Insert each name into the listbox

    def filter_pokemon_list(self, event):
        search_text = self.search_var.get().strip().lower()
        self.pokemon_listbox.delete(0, tk.END)
        if search_text:
            for name in self.pokemon_names:
                if search_text in name.lower():
                    self.pokemon_listbox.insert(tk.END, name)
        else:
            self.populate_pokemon_listbox()


    def confirm_team(self):
        if self.selected_team_listbox.size() > 0:  # Check if there are items in the team listbox
            self.team_data = self.pokemon_data[self.pokemon_data['Name'].isin(self.selected_team_listbox.get(0, tk.END))]
            messagebox.showinfo("Team Confirmed", "Your team has been successfully confirmed!")
        else:
            messagebox.showerror("No Team", "No Pokémon have been added to the team.")

    def update_pokemon_list(self, event=None):
        type_filter = self.type_var.get()
        stat = self.stat_var.get()
        stat_threshold = self.stat_threshold_var.get()
        sort_by = self.sort_var.get()
        filtered_data = self.pokemon_data

        if type_filter != "All":
            filtered_data = filtered_data[filtered_data['Type 1'] == type_filter]
        if stat != "All":
            filtered_data = filtered_data[filtered_data[stat] >= stat_threshold]

        if sort_by == "Name":
            filtered_data = filtered_data.sort_values(by="Name")
        elif sort_by == "Type":
            filtered_data = filtered_data.sort_values(by=["Type 1", "Name"])
        elif sort_by == "Number":
            filtered_data = filtered_data.sort_values(by="#")

        self.pokemon_listbox.delete(0, tk.END)
        for index, row in filtered_data.iterrows():
            self.pokemon_listbox.insert(tk.END, row['Name'])

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
        if selected_indices:
            for index in reversed(selected_indices):
                pokemon_to_remove = self.selected_team_listbox.get(index)
                self.selected_team_listbox.delete(index)
                if pokemon_to_remove in self.current_team:
                    self.current_team.remove(pokemon_to_remove)
        self.update_graph_listbox()

    def clear_team(self):
        self.selected_team_listbox.delete(0, tk.END)
        self.current_team.clear()
        self.update_graph_listbox() 

    def setup_graph_tab(self):
        self.graph_options = ttk.Combobox(self.graph_tab, values=[
        "HP Distribution", "Stat Correlations", "Average Stats by Type", "Type Composition (Pie Chart)", "Team Stats (Pie Chart)"])
        self.graph_options.pack(fill=tk.X, expand=True)
        self.graph_options.bind('<<ComboboxSelected>>', self.display_graph)

        # Setup a frame to hold the graph
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.graph_listbox = tk.Listbox(self.graph_tab, height=10)
        self.graph_listbox.pack(fill=tk.BOTH, expand=True)
        self.update_graph_listbox()

        ttk.Button(self.graph_tab, text="Save Current Team", command=self.save_current_team_from_graph).pack(pady=10)

        self.update_graph_listbox()

    def update_graph_listbox(self):
        if hasattr(self, 'graph_listbox'):  
            self.graph_listbox.delete(0, tk.END)  # Clear the listbox
            for pokemon in self.current_team:
                self.graph_listbox.insert(tk.END, pokemon)

    def plot_team_stats(self):
        if self.current_team:
            attributes = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
            team_data = self.pokemon_data[self.pokemon_data['Name'].isin(self.current_team)]
            mean_attributes = team_data[attributes].mean()

            n_rows = (len(mean_attributes) + 1) // 2
            n_cols = 2

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 22))
            axes = axes.flatten()

            for i, (attribute, value) in enumerate(mean_attributes.items()):
                ax = axes[i]
                ax.pie([value, 100 - value], labels=[attribute, 'Other Attributes'], autopct='%1.1f%%', startangle=140)
                ax.set_title(f'Mean {attribute} for Selected Team')
                ax.axis('equal')

            for i in range(len(mean_attributes), len(axes)):
                axes[i].axis('off')

            plt.tight_layout()

            # Clear previous graph
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Info", "No Pokémon team selected.")

    def display_graph(self, event=None):
        graph_type = self.graph_options.get()
        if graph_type:
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            if graph_type == "HP Distribution":
                sns.histplot(self.pokemon_data['HP'], kde=True, ax=ax)
                ax.set_title('Distribution of HP')
                ax.set_xlabel('HP')
                ax.set_ylabel('Frequency')
            elif graph_type == "Stat Correlations":
                corr = self.pokemon_data[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', vmax=1.0, vmin=-1.0, square=True, linewidths=.5, ax=ax)
                ax.set_title('Stat Correlations')
            elif graph_type == "Type Composition (Pie Chart)":
                self.plot_type_composition(self.pokemon_data)
            elif graph_type == "Team Stats (Pie Chart)":
                self.plot_team_stats()

            if self.canvas:
                self.canvas.get_tk_widget().destroy() 
            self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_figure(self, fig):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()  
        self.canvas = FigureCanvasTkAgg(fig, self.graph_tab) 
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)

    def save_current_team_from_graph(self):
        team_name = simpledialog.askstring("Team Name", "Enter a name for the current team:")
        if team_name and self.current_team:
            self.save_team(team_name, self.current_team)
            messagebox.showinfo("Success", "Team saved successfully!")
        else:
            messagebox.showerror("Error", "No team selected or no name provided.")

    def save_team(self, team_name, team_members):
        if team_name and team_members:
            new_entry = pd.DataFrame({'Team Name': [team_name], 'Members': [','.join(team_members)]})
            self.saved_teams = pd.concat([self.saved_teams, new_entry], ignore_index=True)
            
            self.saved_teams.to_csv('saved_teams.csv', index=False)
            self.update_saved_teams_tab()  
            messagebox.showinfo("Success", f"Team '{team_name}' saved successfully!")
        else:
            messagebox.showerror("Error", "Please provide a team name and select team members.")

    def setup_team_tab(self):
        self.team_listbox = tk.Listbox(self.team_tab, height=15)
        self.team_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        delete_team_button = ttk.Button(self.team_tab, text="Delete Selected Team", command=self.delete_selected_team)
        delete_team_button.pack(pady=5)
        view_graph_button = ttk.Button(self.team_tab, text="View Graph for Selected Team", command=self.view_graph_for_selected_team)
        view_graph_button.pack(pady=5)
        self.update_saved_teams_tab()

    def plot_type_composition(self, data):
        plt.figure(figsize=(8, 6))
        type_counts = data['Type 1'].value_counts()
        type_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140)
        plt.title('Type Composition')
        plt.ylabel('')
        plt.tight_layout()
        plt.show()

    def delete_selected_team(self):
        selected_indices = self.team_listbox.curselection()
        if selected_indices: 
            selected_index = selected_indices[0]
            self.saved_teams = self.saved_teams.drop(self.saved_teams.index[selected_index])
            self.saved_teams.to_csv('saved_teams.csv', index=False)
            self.update_saved_teams_tab()
        else:
            messagebox.showerror("Error", "No team selected for deletion.")

    def view_graph_for_selected_team(self):
        selected_index = self.team_listbox.curselection()
        if selected_index:
            selected_team = self.saved_teams.iloc[selected_index[0]]
            team_members = selected_team['Members'].split(',')
            team_data = self.pokemon_data[self.pokemon_data['Name'].isin(team_members)]
            self.display_graph_for_team(team_data)

    def display_graph_for_team(self, team_data):
        if not team_data.empty:
            fig, ax = plt.subplots()
            sns.histplot(team_data['HP'], kde=True, ax=ax)
            ax.set_title('HP Distribution for Selected Team')
            ax.set_xlabel('HP')
            ax.set_ylabel('Frequency')
            self.show_figure(fig)
        else:
            messagebox.showinfo("Info", "No data available for the selected team.")

    def update_saved_teams_tab(self):
        self.team_listbox.delete(0, tk.END)
        for _, row in self.saved_teams.iterrows():
            self.team_listbox.insert(tk.END, f"{row['Team Name']}: {row['Members']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PokeBuilderApp(root)
    root.mainloop()