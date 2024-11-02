import pandas as pd
import streamlit as st
import numpy as np

# Load datasets
ipl = pd.read_csv(r"C:\Users\ADMIN\Downloads\IPL_Matches_2008_2022.csv")
deliveries = pd.read_csv(r"C:\Users\ADMIN\Downloads\ipl_deliveries.csv")

# Set up Streamlit app title and sidebar
st.title("IPL Data Analysis and Prediction")
st.sidebar.header("IPL Data Analysis Sections")
section = st.sidebar.selectbox("Select Section", ["Team Analysis", "Player Analysis", "Season Analysis"])

def matches_no_result(df, team):
    return df[((df.Team1 == team) | (df.Team2 == team)) & (df.WinningTeam.isnull())].shape[0]  # Fixed missing parenthesis

# Season Analysis section
if section == "Season Analysis":

    st.write("Teams Analysis by Season")

    season_selected = st.selectbox(
        'Choose the IPL season:',
        options=list(ipl['Season'].unique())
    )
    
    # Filter data for the selected season
    temp_df = ipl[ipl['Season'] == season_selected]

    # Prepare DataFrame for team statistics
    team_names = temp_df['Team1'].unique()  # Get unique team names
    new_df = pd.DataFrame({'Team Name': team_names})

    # Total matches per team
    match_count = (temp_df['Team1'].value_counts() + temp_df['Team2'].value_counts()).sort_index()
    new_df['Matches Played'] = match_count.values

    # Wins per team
    matches_win = temp_df['WinningTeam'].value_counts().sort_index()
    new_df['Matches Won'] = matches_win.reindex(new_df['Team Name'], fill_value=0).values

    # No result calculation
    new_df["No Result"] = new_df["Team Name"].apply(lambda x: matches_no_result(temp_df, x))
    
    # Calculate Matches Lost
    new_df['Matches Lost'] = new_df['Matches Played'] - (new_df['Matches Won'] + new_df['No Result'])
    
    # Calculate Points
    new_df["Points"] = new_df["Matches Won"] * 2 + new_df["No Result"]
    new_df['Final Position'] = new_df['Points'].rank(method = 'first', ascending=False)
    new_df['Final Position'] = new_df['Final Position'].astype(int)
    new_df['Final Position'].replace({1: 'Winner', 2: 'Runner'}, inplace=True)

    st.dataframe(new_df.set_index('Team Name').sort_values(by = 'Points', ascending=False))


#B. Player Analysis
elif section == "Player Analysis":

    st.write("## Top Run Scorers in IPL History")

    top_batsmen = deliveries.groupby("batter")["batsman_run"].sum().sort_values(ascending=False).head(5)
    st.write(top_batsmen)

    st.write("## Top Wicket Takers in IPL History")

    top_bowlers = deliveries[deliveries["kind"].notnull()]
    top_bowlers = top_bowlers.groupby("bowler")["kind"].count().sort_values(ascending=False).head(5)
    st.write(top_bowlers)

    st.write("## Top 5 individual score")

    top_batsmen_df = deliveries.groupby(["ID", "batter"]).sum().sort_values(by = "batsman_run", ascending = False)['batsman_run'].head(5)
    top_batsmen_df = top_batsmen_df.reset_index()
    top_batsmen_df.index += 1

    # Rename columns
    top_batsmen_df.columns = ['Match', 'Batsman', 'Individual Scores']
    st.write(top_batsmen_df.drop(columns = 'Match'))


    st.write("## Best Strike rate player")
    temp_df = deliveries[~(deliveries.extra_type == "wides")]
    temp_df = temp_df.groupby("batter").agg(
    {
        "batsman_run": "sum",
        "ballnumber": "count"
    })
    temp_df["strike_rate"] = temp_df["batsman_run"] / temp_df["ballnumber"] * 100
    st.write(temp_df[temp_df["ballnumber"] >= 100].sort_values("strike_rate", ascending = False).reset_index().set_index('batter').head(5))


    st.write("## Most Successful bowler against any batsman")

    batter_bowler = deliveries.groupby(['bowler','batter'])[['isWicketDelivery','batsman_run']].sum().sort_values(by = ['isWicketDelivery', 'batsman_run'], ascending = [False, True]).head(5)
    batter_bowler = batter_bowler.reset_index()


    batter_bowler.columns = ['Bowler', 'Batsman', 'Number of dismissal', 'Runs Scored']
    st.write(batter_bowler.set_index('Bowler'))


# C.Team Analysis
elif section == "Team Analysis":

    team_names = np.sort(ipl['Team1'].unique())
    total_matches_by_teams = ipl['Team1'].value_counts() + ipl['Team2'].value_counts()
    winning_team = ipl['WinningTeam'].value_counts().sort_index()
    home_win = (ipl[ipl["WinningTeam"] == ipl['Team1']]['Team1'].value_counts().sort_index() / winning_team) * 100
    away_win = (ipl[(ipl["WinningTeam"] != ipl['Team1'])]['Team2'].value_counts().sort_index() / winning_team) * 100
    
    lists = {'Team': team_names,'Total matches played': total_matches_by_teams.values, 'No of winning matches': winning_team.values, 'Home win %': home_win.values, 'Away win %': away_win.values}

    ipl_df = pd.DataFrame(columns=['Team','Total matches played', 'No of winning matches', 'Home win %', 'Away win %'], data = lists)
    ipl_df = ipl_df.sort_values('No of winning matches', ascending = False, ignore_index = True)
    ipl_df.index += 1

    st.dataframe(ipl_df)

    
