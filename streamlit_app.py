import streamlit as st
import pandas as pd



# Set wide mode
st.set_page_config(layout="wide")


# Load the Excel file
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    return df


def calculate_player_averages(player_data):
    # Exclude totals and opposition team stats
    player_data = player_data[~player_data['NAMES'].str.contains("TOTALS")]

    # Calculate averages for the specified columns
    columns_to_average = ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'FLS', 'FG%', '3P%', 'FT%', 'GSC']
    averages = player_data.groupby('NAMES')[columns_to_average].mean().reset_index()

    # Count total games played for each player
    games_played = player_data.groupby('NAMES').size().reset_index(name='Games Played')

    # Merge the averages with the total games played
    player_averages = pd.merge(averages, games_played, on='NAMES')

    return player_averages


def format_and_style_dataframe(df, is_averages=False):
    # Define color mapping for player names
    color_map = {
        'Lachlan Farley': '#FF99CC',
        'Josh Huxtable': '#428a36',
        'Darcy Bishop': '#99FF66',
        'Harry Coller': '#5f99f5',
        'Adam Blain': '#be60f7',
        'Reed Coller': '#fcdb03',
        'Lachlan Farrugia': '#5cf046',
        'Daniel Monitto': '#fcd04c',
        'Riley Huxtable': '#fc9219',
        'Austin Thorney-Croft': '#5364b0',
        'Jude Milburn': '#f0823a',
        'James Norrish': '#de5647',
        'Liam Brown': '#b76bf2',
        # Add more mappings as needed
    }

    def highlight_rows(row):
        color = color_map.get(row['NAMES'], '#A6C9EC')  # Default to a light color if player not in color_map
        return [f'background-color: {color}; color: black;' for _ in row]  # Set text color to black

    # Apply custom styling to the DataFrame
    styled_df = df.style.apply(highlight_rows, axis=1).set_table_styles({
        '': [{'selector': 'td', 'props': [('padding', '12px'), ('border', '1px solid black'), ('color', 'black')]},
             # Black table lines
             {'selector': 'th',
              'props': [('padding', '12px'), ('border', '1px solid black'), ('background-color', '#007BFF'),
                        ('color', 'white'), ('text-transform', 'uppercase')]}],
        'tr:nth-child(even)': [{'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]}],
        'tr:hover': [{'selector': 'tr:hover', 'props': [('background-color', '#e0e0e0')]}]
    }).set_properties(**{'text-align': 'center', 'vertical-align': 'middle'}).set_table_attributes(
        'style="width: 100%; margin: auto; border-collapse: collapse;"')  # Added border-collapse

    return styled_df


def main():
    st.title("Basketball Stats Dashboard")

    # Load data
    file_path = 'TEST.xlsm'
    data = load_data(file_path)

    # Navigation at the top
    st.write("### Select Page")
    page = st.radio("Choose a page:", ["Game Stats", "Player Averages", "Career Highs"])

    if page == "Game Stats":
        st.write("### Select Season and Game")
        # Get unique seasons and sort them in descending order
        sorted_seasons = sorted(data['SEASON'].unique(), reverse=True)
        selected_season = st.selectbox("Select Season", sorted_seasons)

        # Ensure games are sorted with the latest game first
        games_in_season = data[data['SEASON'] == selected_season]['GAME'].unique()
        games_in_season_sorted = sorted(games_in_season, reverse=True)  # Sort games in descending order

        # Add filter for game selection
        selected_game = st.selectbox("Select Game", games_in_season_sorted)

        # Filter data based on the selected game
        filtered_data = data[(data['SEASON'] == selected_season) & (data['GAME'] == selected_game)]

        # Filtered data
        filtered_data = data[(data['SEASON'] == selected_season) & (data['GAME'] == selected_game)]

        # Get the opposition team name from the 'OPP' column
        opposition_team = filtered_data['OPP'].iloc[0]

        # Define color mapping for opposition teams
        opposition_color_map = {
            'MAGIC 1': '#3399FF',
            'MAGIC 2': '#3399FF',
            'MAGIC 3': '#3399FF',
            'MAGIC 4': '#3399FF',
            'LIGHTNING 1': '#F9CB49',
            'LIGHTNING 2': '#F9CB49',
            'LIGHTNING 3': '#F9CB49',
            'PANTHERS 3': '#000000',
            'PANTHERS 2': '#000000',
            'SAINTS': '#9A009A',
        }

        # Default color if the team name is not in the map
        default_opposition_color = '#6C757D'

        # Get the color for the opposition team
        opposition_color = opposition_color_map.get(opposition_team, default_opposition_color)

        # Exclude total stats and opposition team stats
        opposition_names = data['OPP'].unique()
        player_data = filtered_data[
            ~filtered_data['NAMES'].isin(opposition_names) & ~filtered_data['NAMES'].str.contains("TOTALS")]

        # Extract team score (assuming 'PTS' column contains points)
        team_score = filtered_data[filtered_data['NAMES'].str.contains("TOTALS")]['PTS'].sum()

        # Extract opposition score
        opposition_score = filtered_data[filtered_data['NAMES'].isin(opposition_names)]['PTS'].sum()

        # Drop the 'OPP', 'SEASON', 'GAME', and 'TYPE' columns
        player_data = player_data.drop(columns=['OPP', 'SEASON', 'GAME', 'TYPE'])

        # Format percentages for display with two decimal points
        percentage_columns = ['FG%', 'FT%', '2P%', '3P%']
        for col in percentage_columns:
            if col in player_data.columns:
                player_data[col] = (player_data[col] * 100).apply(lambda x: f"{x:.2f}%")

        # Format 'GSC' column with two decimal points
        if 'GSC' in player_data.columns:
            player_data['GSC'] = player_data['GSC'].apply(lambda x: f"{x:.2f}")

        # Identify columns to convert to numeric (excluding text columns)
        numeric_columns = [col for col in player_data.columns if
                           player_data[col].dtype != 'object' and col not in percentage_columns + ['GSC']]
        for col in numeric_columns:
            # Convert to numeric, handling errors and non-numeric values
            player_data[col] = pd.to_numeric(player_data[col], errors='coerce').fillna(0).astype(int)

        # Display team scores
        st.write(f"## Game {selected_game} Stats in Season {selected_season}")

        # Display scores in styled boxes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div style="
                    background-color: #FF5733;
                    color: white;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
                    PANTHERS 1 <br><br> <span style="font-size: 40px;">{team_score}</span> <!-- Increased font size -->
                </div>
                """, unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="
                    background-color: {opposition_color};
                    color: white;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
                    {opposition_team} <br><br> <span style="font-size: 40px;">{opposition_score}</span> <!-- Increased font size -->
                </div>
                """, unsafe_allow_html=True
            )

        # Display filtered player data with enhanced styling
        st.write("### Player Stats")

        # Apply styling to player data
        styled_player_data = format_and_style_dataframe(player_data)

        # Display the styled DataFrame
        st.write(styled_player_data.to_html(), unsafe_allow_html=True)



    elif page == "Player Averages":

        st.write("# Player Averages")

        all_time = st.checkbox('Show All-Time Averages')

        if all_time:

            st.write("### All-Time Player Averages")

            # Use the full data without filtering by season

            filtered_data = data


        else:

            # Add a filter for season at the top

            sorted_seasons = sorted(data['SEASON'].unique(), reverse=True)

            selected_season = st.selectbox("Select Season", sorted_seasons)

            st.write(f"### Player Averages for Season {selected_season}")

            # Filter the data based on the selected season

            filtered_data = data[data['SEASON'] == selected_season]

        # Player Averages

        player_data = filtered_data[~filtered_data['NAMES'].str.contains("TOTALS")]

        # Filter out rows with specific team names from player averages

        teams_to_exclude = ['LIGHTNING 1', 'LIGHTNING 2', 'LIGHTNING 3', 'MAGIC 1', 'MAGIC 2', 'MAGIC 3', 'MAGIC 4',
                            'SAINTS',

                            'PANTHERS 3', 'PANTHERS 2']

        filtered_player_data = player_data[player_data['OPP'].isin(teams_to_exclude)]

        # Calculate player averages with the filtered data

        player_averages = calculate_player_averages(filtered_player_data)

        # Format percentages as percentages

        percentage_columns = ['FG%', '3P%', 'FT%']

        for col in percentage_columns:

            if col in player_averages.columns:
                player_averages[col] = player_averages[col].apply(lambda x: f"{x * 100:.2f}%")

        # Format other numerical columns to 2 decimal places

        numeric_columns = ['PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV', 'FLS', 'GSC']

        for col in numeric_columns:

            if col in player_averages.columns:
                player_averages[col] = player_averages[col].apply(lambda x: f"{x:.2f}")


        # Sort player averages by Games Played in descending order
        player_averages = player_averages.sort_values(by='Games Played', ascending=False)

        # Apply styling to player averages

        styled_player_averages = format_and_style_dataframe(player_averages)

        # Display the styled DataFrame

        st.write(styled_player_averages.to_html(), unsafe_allow_html=True)

        # Additional Average Stats

        st.write("### Additional Average Stats")

        def calculate_and_format_additional_stats(player_data):

            # Exclude totals and opposition team stats

            player_data = player_data[~player_data['NAMES'].str.contains("TOTALS")]

            # Calculate averages for the specified columns

            columns_to_average = ['2PM', '2PA', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA',

                                  'O REB', 'D REB', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV',

                                  'FLS', '2P%', '3P%', 'FG%', 'FT%', 'GSC']

            averages = player_data.groupby('NAMES')[columns_to_average].mean().reset_index()

            # Count total games played for each player

            games_played = player_data.groupby('NAMES').size().reset_index(name='Games Played')

            # Merge the averages with the total games played and sort by games played in descending order

            player_averages = pd.merge(averages, games_played, on='NAMES').sort_values(by='Games Played',
                                                                                       ascending=False)

            return player_averages

        # Calculate additional stats

        additional_stats = calculate_and_format_additional_stats(filtered_player_data)

        # Format percentages as percentages

        percentage_columns = ['FG%', '3P%', 'FT%', '2P%']

        for col in percentage_columns:

            if col in additional_stats.columns:
                additional_stats[col] = additional_stats[col].apply(lambda x: f"{x * 100:.2f}%")

        columns_to_average = ['2PM', '2PA', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA',

                              'O REB', 'D REB', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV',

                              'FLS', 'GSC']

        for col in columns_to_average:

            if col in additional_stats.columns:
                additional_stats[col] = additional_stats[col].apply(lambda x: f"{x:.2f}")

        # Apply styling to additional stats

        styled_additional_stats = format_and_style_dataframe(additional_stats, is_averages=True)

        # Display the styled DataFrame

        st.write(styled_additional_stats.to_html(), unsafe_allow_html=True)




    elif page == "Career Highs":

        st.write("# Career Highs")

        # Add a checkbox for all-time career highs

        all_time = st.checkbox('Show All-Time Career Highs')

        if all_time:

            st.write("### All-Time Career Highs")

            # Use the full data without filtering by season

            filtered_data = data

        else:

            # Add a filter for season at the top

            sorted_seasons = sorted(data['SEASON'].unique(), reverse=True)
            selected_season = st.selectbox("Select Season", sorted_seasons)

            st.write(f"### Career Highs for Season {selected_season}")

            # Filter the data based on the selected season

            filtered_data = data[data['SEASON'] == selected_season]

        def calculate_career_highs(player_data):

            # Exclude totals and opposition team stats

            player_data = player_data[~player_data['NAMES'].str.contains("TOTALS")]

            # Exclude specific teams if necessary

            teams_to_exclude = ['LIGHTNING 1', 'LIGHTNING 2', 'LIGHTNING 3', 'MAGIC 1', 'MAGIC 2', 'SAINTS',

                                'PANTHERS 3', 'PANTHERS 2']

            player_data = player_data[player_data['OPP'].isin(teams_to_exclude)]

            # Calculate career highs and lows for the specified columns

            columns_of_interest = ['2PM', '2PA', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA',

                                   'O REB', 'D REB', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV',

                                   'FLS', 'GSC']

            career_highs = player_data.groupby('NAMES')[columns_of_interest].max().reset_index()

            career_lows = player_data.groupby('NAMES')[columns_of_interest].min().reset_index()

            # Merge highs and lows DataFrames

            career_highs = career_highs.merge(career_lows[['NAMES', 'GSC']], on='NAMES', suffixes=('', '_Lowest'))

            # Rename columns for clarity

            career_highs.rename(columns={'GSC_Lowest': 'Lowest GSC'}, inplace=True)

            # Format percentages

            percentage_columns = ['FG%', 'FT%', '2P%', '3P%']

            for col in percentage_columns:

                if col in career_highs.columns:
                    career_highs[col] = career_highs[col].apply(lambda x: f"{x * 100:.0f}%")

            # Format other numerical columns with no decimal points

            numeric_columns = ['2PM', '2PA', '3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA',

                               'O REB', 'D REB', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'TOV',

                               'FLS']

            for col in numeric_columns:

                if col in career_highs.columns:
                    career_highs[col] = career_highs[col].apply(lambda x: f"{x:.0f}")

            # Format 'GSC' and 'Lowest GSC' with 2 decimal places

            for col in ['GSC', 'Lowest GSC']:

                if col in career_highs.columns:
                    career_highs[col] = career_highs[col].apply(lambda x: f"{x:.2f}")

            return career_highs

        # Calculate career highs

        career_highs = calculate_career_highs(filtered_data)

        # Apply styling to career highs

        styled_career_highs = format_and_style_dataframe(career_highs)

        # Display the styled DataFrame

        st.write(styled_career_highs.to_html(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
