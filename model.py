#model.py
"""File for Model class"""
import os
import pandas as pd


class PokemonModel:
    """Model class of program"""
    def __init__(self, file_path):
        self.pokemon_df = pd.read_csv(file_path)
        self.saved_teams_file = 'saved_teams.csv'
        if os.path.exists(self.saved_teams_file):
            self.saved_teams = pd.read_csv(self.saved_teams_file)
        else:
            self.saved_teams = pd.DataFrame(columns=['Team Name', 'Members'])

    def get_pokemon_data(self, name='', type1='', stat='', min_value=0):
        """Function to get Pokemons' data from dataset"""
        data = self.pokemon_df
        if name:
            data = data[data['Name'].str.contains(name, case=False)]
        if type1 and type1 != 'All':
            data = data[(data['Type 1'] == type1) | (data['Type 2'] == type1)]
        if stat and stat != 'All':
            data = data[data[stat] >= int(min_value)]
        return data.to_dict(orient='records')

    def get_pokemon_names(self):
        """Function to get Pokemons' names from dataset"""
        return self.pokemon_df['Name'].tolist()

    def get_types(self):
        """Function to get Pokemons' types from dataset"""
        types = pd.concat([self.pokemon_df['Type 1'], self.pokemon_df['Type 2']]).unique()
        types = [t for t in types if t == t]  # remove NaNs
        types.sort()
        return types

    def modify_team(self, team_name, pokemon_name, action="add"):
        """Function for modify team's members"""
        team = self.teams_data.loc[self.teams_data['Team Name'] == team_name]
        if team.empty:
            if action == "add":
                self.teams_data = self.teams_data.append({
                    'Team Name': team_name, 'Members': [pokemon_name]
                }, ignore_index=True)
        else:
            current_members = team['Members'].iloc[0]
            if action == "add":
                current_members.append(pokemon_name) \
                    if pokemon_name not in current_members else None
            elif action == "remove":
                current_members.remove(pokemon_name) \
                    if pokemon_name in current_members else None
            self.teams_data.loc[self.teams_data['Team Name'] == team_name, 'Members'] \
                = [current_members]
        self.save_team()

    def load_team(self, team_name):
        """Function for load team's members of selected team"""
        team_data = self.saved_teams[self.saved_teams['Team Name'].str.strip().str.lower()
                                     == team_name.strip().lower()]
        if not team_data.empty:
            members = team_data.iloc[0]['Members'].split(',')
            return members
        return []

    def save_team(self, team_name, team_members):
        """Functoin to save the seleceted team into file"""
        if team_name and team_members:
            new_entry = pd.DataFrame({'Team Name': [team_name],
                                      'Members': [','.join(team_members)]})
            self.saved_teams = pd.concat([self.saved_teams, new_entry], ignore_index=True, )
            self.saved_teams.to_csv('saved_teams.csv', index=False)

    def delete_team(self, index):
        if 0 <= index < len(self.saved_teams):
            # Drop the team at the given index and reset the DataFrame index
            self.saved_teams.drop(index, inplace=True)
            self.saved_teams.reset_index(drop=True, inplace=True)
            # Save the updated DataFrame back to the CSV to reflect changes
            self.saved_teams.to_csv(self.saved_teams_file, index=False)

    def add_pokemon_to_team(self, team_name, pokemon):
        """Function for add new member to team"""
        team_index = self.saved_teams[self.saved_teams['Team Name'] == team_name].index
        if not team_index.empty:
            team_index = team_index[0]
            existing_members = self.saved_teams.loc[team_index, 'Members'].split(',')
            if pokemon not in existing_members:
                existing_members.append(pokemon)
                self.saved_teams.at[team_index, 'Members'] = ','.join(existing_members)
                self.saved_teams.to_csv(self.saved_teams_file, index=False)
        else:
            self.save_team(team_name, [pokemon])

    def get_selected_pokemon_data(self, pokemon_names):
        """
        Retrieve data for a selected list of Pokémon by their names.
        
        :param pokemon_names: List of Pokémon names to retrieve data for.
        :return: DataFrame containing data for the selected Pokémon.
        """
        return self.pokemon_df[self.pokemon_df['Name'].isin(pokemon_names)]

    def load_all_team_names(self):
        """Load all team names from the saved teams file."""
        if os.path.exists(self.saved_teams_file):
            self.saved_teams = pd.read_csv(self.saved_teams_file)
            return self.saved_teams['Team Name'].tolist()
        return []

    def get_team_data(self, team_name):
        """
        Retrieve data for all Pokémon in a specified team by team name.
        
        Parameters:
            team_name (str): The name of the team to retrieve data for.

        Returns:
            DataFrame: A DataFrame containing all Pokémon data for the given team.
        """
        # Fetch team members' names based on the team name
        team_data = self.saved_teams[self.saved_teams['Team Name'].str.lower() == team_name.lower()]
        if team_data.empty:
            return pd.DataFrame()  # Return an empty DataFrame if the team does not exist

        # Extract member names from the team entry
        members = team_data.iloc[0]['Members'].split(',')
        members = [name.strip() for name in members]  # Clean any leading/trailing spaces

        # Retrieve Pokémon data for each member
        pokemon_data = self.pokemon_df[self.pokemon_df['Name'].isin(members)]
        return pokemon_data
