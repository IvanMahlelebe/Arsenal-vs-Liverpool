import pandas as pd
import itertools
import matplotlib.pyplot as plt

def double_digits(number):
    """
        Description: Turns single-digit numbers into double digits

        Parameters
        ------------
        number: str (required)
            Number as a string

        Returns
        ------------
        new_number: str
            Double digit version of "number" variable
    """
    new_number = '%02d' % (int(number),)
    return new_number

# Thanks to stackoverflow I got this:
# print("%02d" % (10,))

def create_dfs(start_season, end_season):
    """
        Description
        ------------
        Creates data file names and reads those names as pd.Dataframes

        Parameters
        ------------
        start_season: str (required)
            The last 1 or 2 digits of a year a season starts
        end_season: string(optional)
            The last 1 or 2 digits of a year a season ends

        Returns
        ------------
        dataframes: pandas.DataFrames
            Data on a range of seasons you would like to analyze
    """
    # Error-checking for correct input of dates/seasons
    if (int(end_season) < int(start_season)):
        return "Invalid input"

    try:
        names_list = []
        for year in range(int(start_season), int(end_season)):
            start_year = int(year)
            end_year = int(start_year) + 1
            path = "../../Datasets/raw_data/"
            file_name = '20' + double_digits(start_year) + '-' + double_digits(end_year) + '.csv'
            names_list.append(pd.read_csv(path + file_name))
        return names_list
    except FileNotFoundError:
        return 'Unmatched scope! Some or all files you\'ve requested aren\'t available'


def disjoint_columns(df_files):
    """
        Description
        ------------
        Finds and return columns that in other dataframes but not in others

        Parameters
        ------------
        df_files: pd.DataFrame (required)
            A list of dataframe objects

        Returns
        ------------
        final_list: list object
            A list of columns that are symmetrically different
    """
    uncommon_cols = []

    for index in range(len(df_files)):
        if index < len(df_files) - 1:
            columns = df_files[index].columns.difference(df_files[index + 1].columns)
            uncommon_cols.append(list(columns))

        # Joining a list of lists into one list
        final_list = list(itertools.chain.from_iterable(uncommon_cols))

    return final_list


def subset_columns(start_col, end_col, files):
    """
        Description
        ------------
        Subsets all files into columns of choice

        Parameters
        ------------
        start_col: column name to start at
        end_col: column name to end with
        files: list of DataFrame files

        Returns
        ------------
        required_files: list object. Elements of type pd.DataFrame
            A list of dataFrames with the desired columns only
    """
    required_files = []
    for file in files:
        file = file.loc[:, start_col:end_col]
        required_files.append(pd.DataFrame(file))

    return required_files


def subset_teams(team_1, team_2, dataFrame):
    """
        Description
        ------------
        Subsets 2 teams you would like to compare in your analyses

        Parameters
        ------------
        team_1: Name of team (str)
        team_2: Name of team (str)
        dataFrame: A dataframe with all teams and all seasons (pd.DataFrame)

        Returns
        ------------
        data: dataframe (pd.DataFrame)
            data with only the 2 teams you're interested in
    """
    data = (dataFrame.loc[(dataFrame['HomeTeam'] == team_1) |
                (dataFrame['HomeTeam'] == team_2) |
                (dataFrame['AwayTeam'] == team_1) |
                (dataFrame['AwayTeam'] == team_2)])
    return data


def check_scores(row):

    if row['Final_Result'] == 'H':
        assert (row['Final_HomeGoals'] > row['Final_AwayGoals'])
    elif row['Final_Result'] == 'A':
        assert row['Final_AwayGoals'] > row['Final_HomeGoals']
    elif row['Final_Result'] == 'D':
        assert row['Final_AwayGoals'] == row['Final_HomeGoals']

    # This is the kind of spaghetti that happens when you're sleepy
    if row['Half_Result'] == 'H':
        assert (row['Half_HomeGoals'] > row['Half_AwayGoals'])
    elif row['Half_Result'] == 'A':
        assert row['Half_AwayGoals'] > row['Half_HomeGoals']
    elif row['Half_Result'] == 'D':
        assert row['Half_AwayGoals'] == row['Half_HomeGoals']

    assert row['Half_AwayGoals'] <= row['Final_AwayGoals']


def check_shots(row, count = 0):
    try:
        assert row['Home_Shots'] >= row['HomeShots_Target']
        assert row['Away_Shots'] >= row['AwayShots_Target']
    except AssertionError:
        count += 1

    return count


def head_to_head(team_1, team_2, df):
    """
        Description
        ------------
        Retrieves head-to-head matches of 2 teams

        Parameters
        ------------
        team_1: Name of team (str)
        team_2: Name of team (str)
        dataFrame: A dataframe with all teams and all seasons (pd.DataFrame)

        Returns
        ------------
        data: dataframe (pd.DataFrame)
            head-to-head matches of the above 2 teams
    """
    data = df.loc[((df['HomeTeam'] == team_1) & (df['AwayTeam'] == team_2)) |
                          ((df['HomeTeam'] == team_2) & (df['AwayTeam'] == team_1))]
    return data


def add_winners_col(row):
    if row['Final_Result'] == 'A':
        return row['AwayTeam']
    elif row['Final_Result'] == 'H':
        return row['HomeTeam']
    elif row['Final_Result'] == 'D':
        return 'Draw'


def goal_diff(row):
    if row['Final_Result'] == 'A':
        return row['Final_AwayGoals'] - row['Final_HomeGoals']
    elif row['Final_Result'] == 'H':
        return row['Final_HomeGoals'] - row['Final_AwayGoals']
    elif row['Final_Result'] == 'D':
        return 0


def extract_team_data(df, team_name):
    """
        Description
        ------------
        Draws data for only one team, rename the columns and build a dataframe

        Parameters
        ------------
        df: All data (pd.DataFrame)
        team_name: Name of team (str)

        Returns
        ------------
        data: dataframe (pd.DataFrame)
            data for a selected team
    """

    ft_result = {
        'A': ['Won', 'Lost'],
        'H': ['Lost', 'Won'],
        'D': ['Drew', 'Drew']
    }
    ht_result = {
        'A': ['Winning', 'Losing'],
        'H': ['Losing', 'Winning'],
        'D': ['Draw', 'Draw']
    }

    col_names = [
        'rival', 'ft_result', 'ft_goals', 'ft_goal_diff', 'ht_result', 'ht_goals',
        'ht_goal_diff', 'mr_ref', 'shots', 'shots_target', 'fouls',
        'corners', 'yellows', 'reds', 'season', 'venue', 'shots_diff',
        'shots_targ_diff']

    team_df = pd.DataFrame(columns=col_names)

    for index, row in df.iterrows():
        if row['AwayTeam'] == team_name:
            input_row = pd.Series([
                row['HomeTeam'],
                ft_result[row['Final_Result']][0],
                row['Final_AwayGoals'],
                row['Final_AwayGoals'] - row['Final_HomeGoals'],
                ht_result[row['Half_Result']][0],
                row['Half_AwayGoals'],
                row['Half_AwayGoals'] - row['Half_HomeGoals'],
                row['Referee'],
                row['Away_Shots'],
                row['AwayShots_Target'],
                row['Away_Fouls'],
                row['Away_Corner'],
                row['Away_Yellows'],
                row['Away_Reds'],
                row['Season'],
                'Away',
                row['Away_Shots'] - row['Home_Shots'],
                row['AwayShots_Target'] - row['HomeShots_Target']
            ], index=team_df.columns)

            team_df = team_df.append(input_row, ignore_index=True)

        elif row['HomeTeam'] == team_name:
            input_row = pd.Series([
                row['AwayTeam'],
                ft_result[row['Final_Result']][1],
                row['Final_HomeGoals'],
                row['Final_HomeGoals'] - row['Final_AwayGoals'],
                ht_result[row['Half_Result']][1],
                row['Half_HomeGoals'],
                row['Half_HomeGoals'] - row['Half_AwayGoals'],
                row['Referee'],
                row['Home_Shots'],
                row['HomeShots_Target'],
                row['Home_Fouls'],
                row['Home_Corner'],
                row['Home_Yellows'],
                row['Home_Reds'],
                row['Season'],
                'Home',
                row['Home_Shots'] - row['Away_Shots'],
                row['HomeShots_Target'] - row['AwayShots_Target']
            ], index=team_df.columns)

            team_df = team_df.append(input_row, ignore_index=True)

    return team_df


def get_ratio(row, var1, var2):
    try:
        result = row[var1] / row[var2]
        return result
    except ZeroDivisionError:
        return 0


def venue_shots(venue, team, df):
    """
        Description
        ------------
        Aggregates number of shots and shots-on-target of a team based on the venue of the match

        Parameters
        ------------
        venue: Home or Away (str)
        team: Name of team (str)
        df: Data of a team (pd.DataFrame)

        Returns
        ------------
        data: dataframe (pd.DataFrame)
            Small dataframe showing shots and shots-on-target
    """

    venue_shots = (df[(df['venue'] == venue)][['shots', 'shots_target']])
    venue_shots['team'] = team
    venue_shots = venue_shots.groupby('team').agg({'shots': 'sum', 'shots_target': 'sum'})
    return venue_shots


def view_gameStats(team1, team2, team1_label, team2_label, ylabel, fig_name, title):
    """
        Description
        ------------
        Visualize statistics of games between 2 teams over time

        Parameters
        ------------
        team1: Name of team (str)
        team2: Name of team (str)
        team1_label: Team label (str)
        team2_label: Team label (str)
        ylabel: Label on the y-axis (str)
        fig_name: Name of a generated jpeg file (str)
        title: Title of a generated plot (str)

        Returns
        ------------
        plot: Line plot (Unknown)
    """

    fig_name = fig_name + '.jpeg'
    game_ticks = [x for x in range(0, team1.shape[0], 4)] # Just pick any team really

    MIDSIZE = (10, 8)
    fig, ax = plt.subplots(figsize=MIDSIZE)

    plt.plot(team1, label=team1_label)
    plt.plot(team2, label=team2_label)
    plt.xticks(game_ticks)
    plt.ylabel(ylabel)
    plt.xlabel('Games in succession')
    plt.title(team1_label + ' vs ' + team2_label + '\n' + title)
    plt.legend(loc='upper left', fontsize='medium')
    plt.savefig(fig_name)
    fig.tight_layout()


def view_seasonStats(team1, t1_label, team2, t2_label, variable, var_label):
    """
        Description
        ------------
        Visualize statistics of games between 2 teams per season

        Parameters
        ------------
        team1: Name of team (str)
        team1_label: Team label (str)
        team2: Name of team (str)
        team2_label: Team label (str)
        variable: Variable on the y-axis (str)
        var_label: Name of variable (str)

        Returns
        ------------
        plot: Line plot (Unknown)
    """

    team1 = (team1.groupby('season')
                  .agg({variable: 'sum'})
                  .rename(columns=({variable: var_label})))

    team2 = (team2.groupby('season')
                      .agg({variable: 'sum'})
                      .rename(columns=({variable: var_label})))

    _ = fig, ax = plt.subplots(figsize=(10,6))
    _ = team1.plot(y=var_label, ax=ax, label=t1_label)
    _ = team2.plot(y=var_label, ax=ax, label=t2_label)
    _ = ax.set_ylabel('Total ' + var_label)
    _ = ax.set_title('Total ' + var_label + ' per Season')
    _ = ax.legend(fontsize='medium')
