#model.py
import pandas as pd
import os

class PokemonModel:
    def __init__(self, file_path):
        self.pokemon_df = pd.read_csv(file_path)
        self.saved_teams_file = 'saved_teams.csv'
        if os.path.exists(self.saved_teams_file):
            self.saved_teams = pd.read_csv(self.saved_teams_file)
        else:
            self.saved_teams = pd.DataFrame(columns=['Team Name', 'Members'])
    
    def get_pokemon_data(self, name='', type1='', stat='', min_value=0):
        data = self.pokemon_df
        if name:
            data = data[data['Name'].str.contains(name, case=False)]
        if type1 and type1 != 'All':
            data = data[(data['Type 1'] == type1) | (data['Type 2'] == type1)]
        if stat and stat != 'All':
            data = data[data[stat] >= int(min_value)]
        return data.to_dict(orient='records') 
    
    def get_pokemon_names(self):
        return self.pokemon_df['Name'].tolist()
    
    def get_types(self):
        types = pd.concat([self.pokemon_df['Type 1'], self.pokemon_df['Type 2']]).unique()
        types = [t for t in types if t == t]  # remove NaNs
        types.sort()
        return types

    def modify_team(self, team_name, pokemon_name, action="add"):
        team = self.teams_data.loc[self.teams_data['Team Name'] == team_name]
        if team.empty:
            if action == "add":
                self.teams_data = self.teams_data.append({
                    'Team Name': team_name, 'Members': [pokemon_name]
                }, ignore_index=True)
        else:
            current_members = team['Members'].iloc[0]
            if action == "add":
                current_members.append(pokemon_name) if pokemon_name not in current_members else None
            elif action == "remove":
                current_members.remove(pokemon_name) if pokemon_name in current_members else None
            self.teams_data.loc[self.teams_data['Team Name'] == team_name, 'Members'] = [current_members]
        
        self.save_team()

    def load_teams(self):
        try:
            self.saved_teams = pd.read_csv('saved_teams.csv')
        except FileNotFoundError:
            self.saved_teams = pd.DataFrame(columns=['Team Name', 'Members'])

    def save_team(self, team_name, team_members):
        if team_name and team_members:
            new_entry = pd.DataFrame({'Team Name': [team_name], 'Members': [','.join(team_members)]})
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