''' 
Questions to Be Answered About the Japanese Animated Works Database by Kaggle:

1. What is the highest-rated work in the database?
2. How many works were released each year?
3. What is the most common genre in the database?
4. What are the 4 works with the highest number of episodes?
5. What is the average rating for each animation genre?
6. Which are the 5 studios that produced the most works?
7. Is there a relationship between rating and number of episodes in the animations?
8. What are the most popular works from each decade?
'''

# --------------------------Dowloading, Loading, Cleaning and Formating the data----------------------------------- #

import kagglehub
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Minha Página", layout="wide", initial_sidebar_state="expanded")

# dowloading the df from kaggle and loading to use.
dataset_path = kagglehub.dataset_download("crazygump/myanimelist-scrappind-a-decade-of-anime")
file_path = dataset_path + "/MAL-all-from-winter1917-to-fall2024.csv"
df = pd.read_csv(file_path, sep=",", encoding="utf-8-sig")

# Cleaning and formating the data
df = df.drop(['MAL_id', 'release-date', 'demographics', 'themes', 'members'], axis=1)
df["studio"] = df["studio"].str.replace(r"[\[\]']", "", regex=True)
df["genres"] = df["genres"].str.replace(r"[\[\]']", "", regex=True)
df["release-year"] = pd.to_datetime(df["release-year"], format="%Y", errors="coerce")
df["release-year"] = df["release-year"].dt.year
df = df.sort_values("release-year")
df["decade"] = (df["release-year"] // 10) * 10
df_score = pd.DataFrame({'score': [1,2,3,4,5,6,7,8,9,10]})

# -----------------------------------Sidebar title and filters---------------------------------------------- # 

# Sidebar title
fig_title = f"""
    <div style="width: 100%; height: 120px; background-color:#0E1117;border-radius: 30px; padding: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 30px;">
        <h1 style="font-family: serif; text-align: center; font-size: 25px; color: white;">Dashboard of Japanese Animated Works</h1>
    </div>
"""
st.sidebar.markdown(fig_title, unsafe_allow_html=True)

# Adding filters on the page
year_options = ["All"] + sorted(df['release-year'].dropna().unique().tolist())
year = st.sidebar.selectbox("Year", year_options)
season_options = ["All"] + sorted(df['release-season'].dropna().unique().tolist())
season = st.sidebar.selectbox("Season", season_options)
studio_options = ["All"] + sorted(df['studio'].str.split(", ").explode().dropna().unique().tolist())
studios = st.sidebar.selectbox("Studio", studio_options)
genres_options = ["All"] + sorted(df['genres'].str.split(", ").explode().dropna().unique().tolist())
genres = st.sidebar.selectbox("Genres", genres_options)
score_options = ["All"] + sorted(df_score['score'].dropna().unique().tolist())
score = st.sidebar.selectbox("Score", score_options)

# Applying the filters to a variable (df_filtered) to use in the graphs I want.
df_filtered = df.copy()

if year != "All":
    df_filtered = df_filtered[df_filtered['release-year'] == year]
if season != "All":
    df_filtered = df_filtered[df_filtered['release-season'] == season]
if studios != "All":
    df_filtered = df_filtered[df_filtered['studio'] == studios]
if genres != "All":
    df_filtered = df_filtered[df_filtered['genres'] == genres]
if score != "All":
    df_filtered = df_filtered[df_filtered['score'] >= score]

# -----------------------------------------Answering the Questions------------------------------------------------ # 

# Best-rated work (i won't use the variable df_filtered because I don't wanna filter).
max_score = df["score"].max()
max_title = df[df["score"] == max_score]["title"].values[0]

# Number of Releases per year (i won't use the variable df_filtered because I don't wanna filter).
df_year = df.copy()
df_year = df_year.drop_duplicates(subset=['title'])
df_grouped = df_year.groupby("release-year")["title"].count().reset_index()

# Most frequent genre, i need to explode the column (i won't use the variable df_filtered because I don't wanna filter).
df_genre = df["genres"].str.split(", ").explode().value_counts()
max_genre = df_genre.max()
max_name = df_genre[df_genre == max_genre].index[0]

# Top 4 works with the highest number of episodes (i use the variable df_filtered because I wanna filter).
df_unique_title = df_filtered.drop_duplicates(subset='title')
df_top4_ep = df_unique_title.nlargest(4, 'episodes')[['episodes', 'title']]
df_top4_ep = df_top4_ep.sort_values(by="episodes", ascending=True)

# Mean score per genre, i need to explode the column again but at this time i use the variable df_filtered
df_exploded = df_filtered.copy()
df_exploded['genres'] = df_exploded['genres'].str.split(', ')  
df_exploded = df_exploded.explode('genres')  
df_exploded = df_exploded[df_exploded['genres'].notna()]
df_mean = df_exploded.groupby('genres')['score'].mean().reset_index()
df_mean_sorted = df_mean.sort_values(by='score', ascending=False)

# Top 5 studios that produced the highest number of Releases, i need to explode the column and use df_filtered.
df_estudio = df_filtered.copy()
df_estudio['studio'] = df_estudio['studio'].str.split(', ')
df_estudio = df_estudio.explode('studio')
df_estudio = df_estudio[df_estudio['studio'].notna()]
df_estudio = df_estudio[df_estudio['studio'].str.strip() != ""]
df_estudio = df_estudio[df_estudio['studio'].str.lower() != "unknown"]
df_estudio_unique = df_estudio.drop_duplicates(subset=['title', 'studio'])
df_top5_std = df_estudio_unique.groupby("studio")["title"].count().reset_index()
df_top5_std = df_top5_std.sort_values(by="title", ascending=False).head(5)

# Episodeos VS Score (maybe it's cool to filter)
df_vs = df_filtered[['title', 'score', 'episodes']]
df_vs = df_vs.drop_duplicates(subset=['title'])
df_vs = df_vs.sort_values(by='score', ascending=False).head(10)

# Number of Releases per decade
df_decada = df.copy()
df_decada = df_decada.drop_duplicates(subset=['title'])
df_decada = df_decada.groupby("decade")["title"].count().reset_index()

# ---------------------------------------Markdown in the sidebar--------------------------------------- # 

# Work which has the highest score
fig_score1 = f"""
    <div style="width: 100%; height: 120px; border-radius: 30px; background-color:#0E1117; padding: 20px; display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 25px; margin-top: 20px;">
        <h1 style="font-family: serif; text-align: center; font-size: 20px; color: white;">Highest-Rated Work:</h1>
        <h2 style="font-family: serif; text-align: center; font-size: 20px; color: white;">{max_title} - {max_score}</h2>
    </div>
"""
st.sidebar.markdown(fig_score1, unsafe_allow_html=True)

# Work which has the highest frequency
fig_score2 = f"""
    <div style="width: 100%; height: 120px; border-radius: 30px; background-color:#0E1117; padding: 20px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <h1 style="font-family: serif; text-align: center; font-size: 20px; color: white;">Top Genre:</h1>
        <h2 style="font-family: serif; text-align: center; font-size: 20px; color: white;">{max_genre} Works - {max_name}</h2>
    </div>
"""
st.sidebar.markdown(fig_score2, unsafe_allow_html=True)

# -----------------------------------------------Graphs------------------------------------------------------- # 

# Creating columns to fit the graphs into the layout.
col3, col4, col5 = st.columns(3)
col6, col7, col8 = st.columns(3)

# Graph showing the number of works per year
fig_works_year = px.line(df_grouped, x="release-year", y="title", title="Number of Releases per Year", color_discrete_sequence=["#00FFFF"])
fig_works_year.update_traces(line=dict(width=3))
fig_works_year.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.25, xaxis_title="", yaxis_title="Number of Releases", xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col3.plotly_chart(fig_works_year, use_container_width=True)

# Graph showing the top 4 works with the highest number of episodes
fig_top4_ep = px.bar(df_top4_ep, x="title", y="episodes",text="episodes", title="Top 4 works by Number of Episodes", orientation="v", color_discrete_sequence=["#00FFFF"])
fig_top4_ep.update_traces(textfont=dict(color="black"))
fig_top4_ep.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.25, xaxis_title="", yaxis_title="Number of Episodes", xaxis=dict(showgrid=False, gridcolor="white", tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col4.plotly_chart(fig_top4_ep, use_container_width=True)

# Graph showing the mean score per genre
fig_genre_score = px.line(df_mean_sorted, x="genres", y="score", title="Mean Score per Genre", color_discrete_sequence=["#00FFFF"], markers=True)
fig_genre_score.update_traces(marker=dict(color="white", size=8),line=dict(width=3))
fig_genre_score.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.37, xaxis_title="", yaxis_title="Scores", xaxis=dict(showgrid=False, gridcolor="white", tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col5.plotly_chart(fig_genre_score, use_container_width=True)

# Graph showing the top 5 studios that produced the highest number of works
fig_std_works = px.bar(df_top5_std, x="studio", y="title",text="title", title="Top 5 Studios by Number of Works", color_discrete_sequence=["#00FFFF"])
fig_std_works.update_traces(textfont=dict(color="black"))
fig_std_works.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.25, xaxis_title="", yaxis_title="Number of Works", xaxis=dict(showgrid=False, gridcolor="white", tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col6.plotly_chart(fig_std_works)

# Graph showing the episodeos VS score
df_vs['title'] = df_vs['title'].replace('Shingeki no Kyojin Season 3 Part 2', 'Shingeki no Kyojin', regex=True)
df_vs['title'] = df_vs['title'].replace('Fullmetal Alchemist: Brotherhood', 'Fullmetal Alchemist', regex=True)
df_vs['title'] = df_vs['title'].replace('Kaguya-sama wa Kokurasetai: Ultra Romantic', 'Kaguya-sama', regex=True)
fig_std_score = px.bar(df_vs, x="title", y='score',title="Episodeos VS Score", text="episodes", color_discrete_sequence=["#00FFFF"])
fig_std_score.update_traces(textfont=dict(color="black"))
fig_std_score.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.37, xaxis_title="", yaxis_title="Scores", xaxis=dict(showgrid=False, gridcolor="white", tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col7.plotly_chart(fig_std_score)

# Graph showing the number of Releases per decade
fig_work_decade = px.bar(df_decada, x="decade", y="title",text="title", title="Number of Releases per Decade", color_discrete_sequence=["#00FFFF"])
fig_work_decade.update_traces(textfont=dict(color="black"))
fig_work_decade.update_layout(plot_bgcolor="#262730", title_font=dict(size=18, color="white", family="serif", weight="bold"), title_x=0.25, xaxis_title="", yaxis_title="Number of Releases", xaxis=dict(showgrid=False, gridcolor="white", tickangle=-45, tickfont=dict(color="white")), yaxis=dict(showgrid=True, gridcolor="white", tickfont=dict(color="white")))
col8.plotly_chart(fig_work_decade, use_container_width=True)

