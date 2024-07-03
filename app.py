import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

# Set page config
st.set_page_config(page_title="Cricket Data Analysis", layout="wide")

# Load the data
@st.cache_data
def load_data():
    matches = pd.read_csv("matches.csv")
    matches['date'] = pd.to_datetime(matches['date'])
    output = pd.read_csv("output.csv")
    return matches, output

matches, output = load_data()



# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stSelectbox {
        background-color: white;
        border-radius: 5px;
        padding: 5px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Match Overview", "Team Analysis", "Player Statistics", "Ball-by-Ball Analysis"],
        icons=["house-fill", "binoculars-fill", "trophy-fill", "person-fill", "graph-up"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

# Home page
if selected == "Home":
    st.title("Cricket World Cup 2024 Analysis")
    colored_header(
        label="Tournament Overview",
        description="Key statistics and information about the tournament",
        color_name="blue-70"
    )

    # Tournament summary
    total_matches = matches.shape[0]
    total_teams = len(set(matches['team1'].unique()) | set(matches['team2'].unique()))
    total_venues = matches['venue'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", total_matches)
    col2.metric("Participating Teams", total_teams)
    col3.metric("Venues", total_venues)
    style_metric_cards()

    # Top run-scorers widget
    st.subheader("Top Run Scorers")
    run_scorers = output.groupby('striker')['runs_off_bat'].sum().sort_values(ascending=False).head(10)
    fig_runs = px.bar(run_scorers, x=run_scorers.index, y='runs_off_bat', title="Top 10 Run Scorers")
    st.plotly_chart(fig_runs)

    # Top wicket-takers widget
    st.subheader("Top Wicket Takers")
    wicket_takers = output[output['wicket_type'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10)
    fig_wickets = px.bar(wicket_takers, x=wicket_takers.index, y=wicket_takers.values, title="Top 10 Wicket Takers")
    st.plotly_chart(fig_wickets)

    # Matches by venue
    st.subheader("Matches by Venue")
    venue_counts = matches['venue'].value_counts()
    fig_venues = px.pie(values=venue_counts.values, names=venue_counts.index, title="Distribution of Matches by Venue")
    st.plotly_chart(fig_venues)

# Match Overview
elif selected == "Match Overview":
    st.title("Match Overview")
    colored_header(
        label="Match Details",
        description="Select a match to view its details",
        color_name="blue-70"
    )
    
    # Enhanced match selector
    match_options = [f"{row['team1']} vs {row['team2']} ({row['date'].date()}) - Match {row['match_number']}" 
                     for _, row in matches.iterrows()]
    selected_match_str = st.selectbox("Select a match", match_options)
    selected_match = int(selected_match_str.split("Match ")[-1])
    
    match_data = matches[matches['match_number'] == selected_match].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Match Details")
        st.info(f"**Date:** {match_data['date'].date()}")
        st.info(f"**Venue:** {match_data['venue']}, {match_data['city']}")
        st.info(f"**Teams:** {match_data['team1']} vs {match_data['team2']}")
        st.info(f"**Toss:** {match_data['toss_winner']} chose to {match_data['toss_decision']}")
        
    with col2:
        st.subheader("Match Result")
        if pd.notna(match_data['winner']):
            st.success(f"**Winner:** {match_data['winner']}")
            if pd.notna(match_data['winner_runs']):
                st.success(f"**Margin:** Won by {match_data['winner_runs']} runs")
            elif pd.notna(match_data['winner_wickets']):
                st.success(f"**Margin:** Won by {match_data['winner_wickets']} wickets")
        else:
            st.warning("**Result:** No result")
        
        if pd.notna(match_data['player_of_match']):
            st.info(f"**Player of the Match:** {match_data['player_of_match']}")

# Team Analysis
elif selected == "Team Analysis":
    st.title("Team Analysis")
    colored_header(
        label="Team Statistics",
        description="Select a team to view its performance",
        color_name="green-70"
    )
    
    # Team selector
    all_teams = sorted(list(set(matches['team1'].unique()) | set(matches['team2'].unique())))
    selected_team = st.selectbox("Select a team", all_teams)
    
    # Calculate team statistics
    team_stats = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)]
    wins = team_stats[team_stats['winner'] == selected_team].shape[0]
    losses = team_stats[(team_stats['winner'] != selected_team) & (team_stats['winner'].notna())].shape[0]
    no_results = team_stats[team_stats['winner'].isna()].shape[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Matches Played", team_stats.shape[0])
    col2.metric("Wins", wins)
    col3.metric("Losses", losses)
    style_metric_cards()
    
    # Win percentage chart
    win_percentage = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = win_percentage,
        title = {'text': "Win Percentage"},
        gauge = {'axis': {'range': [None, 100]},
                 'steps': [
                     {'range': [0, 50], 'color': "lightgray"},
                     {'range': [50, 75], 'color': "gray"},
                     {'range': [75, 100], 'color': "darkgreen"}],
                 'threshold': {
                     'line': {'color': "red", 'width': 4},
                     'thickness': 0.75,
                     'value': win_percentage}}))
    st.plotly_chart(fig)
    
    # Toss analysis
    toss_wins = team_stats[team_stats['toss_winner'] == selected_team].shape[0]
    st.subheader("Toss Analysis")
    st.write(f"Toss Win Percentage: {toss_wins / team_stats.shape[0] * 100:.2f}%")
    
    toss_decision = team_stats[team_stats['toss_winner'] == selected_team]['toss_decision'].value_counts()
    fig = px.pie(values=toss_decision.values, names=toss_decision.index, title="Toss Decisions")
    st.plotly_chart(fig)

# Player Statistics
elif selected == "Player Statistics":
    st.title("Player Statistics")
    colored_header(
        label="Player Performance",
        description="Select a player to view their statistics",
        color_name="orange-70"
    )
    
    # Player selector
    all_players = sorted(pd.unique(output[['striker', 'non_striker', 'bowler']].values.ravel('K')))
    selected_player = st.selectbox("Select a player", all_players)
    
    # Player of the match awards
    potm_awards = matches[matches['player_of_match'] == selected_player]
    
    st.subheader("Player of the Match Awards")
    st.info(f"{selected_player} has won {potm_awards.shape[0]} Player of the Match awards.")
    
    if potm_awards.shape[0] > 0:
        st.write("Matches where they won the award:")
        for _, match in potm_awards.iterrows():
            st.success(f"- {match['date'].date()}: {match['team1']} vs {match['team2']} at {match['venue']}")
    
    # Ball-by-ball data for the player
    player_balls = output[(output['striker'] == selected_player) | (output['bowler'] == selected_player)]
    
    if player_balls.shape[0] > 0:
        st.subheader("Ball-by-Ball Performance")
        
        batting = player_balls[player_balls['striker'] == selected_player]
        bowling = player_balls[player_balls['bowler'] == selected_player]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Batting")
            st.metric("Runs scored", batting['runs_off_bat'].sum())
            st.metric("Balls faced", batting.shape[0])
            
        with col2:
            st.write("Bowling")
            st.metric("Wickets taken", bowling['wicket_type'].notna().sum())
            st.metric("Balls bowled", bowling.shape[0])
        style_metric_cards()

# Ball-by-Ball Analysis
else:
    st.title("Ball-by-Ball Analysis")
    colored_header(
        label="Detailed Match Analysis",
        description="Select a match and innings to view ball-by-ball details",
        color_name="red-70"
    )
    
    # Enhanced match selector
    match_options = [f"{row['team1']} vs {row['team2']} ({row['date'].date()}) - Match {row['match_number']}" 
                     for _, row in matches.iterrows()]
    selected_match_str = st.selectbox("Select a match", match_options)
    selected_match = int(selected_match_str.split("Match ")[-1])
    
    match_data = output[output['match_id'] == selected_match]
    
    if match_data.empty:
        st.warning("No ball-by-ball data available for this match.")
    else:
        # Innings selector
        selected_innings = st.selectbox("Select an innings", match_data['innings'].unique())
        innings_data = match_data[match_data['innings'] == selected_innings]
        
        st.subheader("Run Flow")
        cumulative_runs = innings_data['runs_off_bat'].cumsum() + innings_data['extras'].cumsum()
        fig = px.line(x=innings_data['ball'], y=cumulative_runs, title="Cumulative Runs")
        fig.update_layout(xaxis_title="Over", yaxis_title="Runs")
        st.plotly_chart(fig)
        
        st.subheader("Wickets")
        wickets = innings_data[innings_data['wicket_type'].notna()]
        fig = px.scatter(wickets, x='ball', y='runs_off_bat', title="Wickets",
                         hover_data=['player_dismissed', 'wicket_type'])
        fig.update_layout(xaxis_title="Over", yaxis_title="Runs on that ball")
        st.plotly_chart(fig)
        
        st.subheader("Batting Partnership")
        partnerships = innings_data.groupby(['striker', 'non_striker'])['runs_off_bat'].sum().reset_index()
        partnerships['partnership'] = partnerships.apply(lambda row: f"{row['striker']} & {row['non_striker']}", axis=1)
        fig = px.bar(partnerships, x='partnership', y='runs_off_bat', title="Batting Partnerships")
        fig.update_layout(xaxis_title="Partnership", yaxis_title="Runs")
        st.plotly_chart(fig)

st.sidebar.info("This app provides analysis of cricket matches data. Use the navigation menu to explore different aspects of the data.")