import streamlit as st
import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go

# --- Load and Clean Data ---
@st.cache_data
def load_data():
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')

    credits.rename(columns={'movie_id': 'id'}, inplace=True)
    df = movies.merge(credits, on='id')

    def extract_country(x):
        try:
            countries = ast.literal_eval(x)
            return [country['name'] for country in countries if 'name' in country]
        except:
            return []

    df['country_list'] = df['production_countries'].apply(extract_country)
    df = df.explode('country_list')

    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df = df.dropna(subset=['country_list', 'popularity', 'original_title', 'release_date'])

    return df

# --- Load Data ---
df = load_data()

# --- Sidebar ---
st.sidebar.title("🎯 Country Selection")

countries = sorted(df['country_list'].unique())
primary_country = st.sidebar.selectbox("🌍 Select a Country", countries)

compare = st.sidebar.checkbox("➕ Compare with another country?")
secondary_country = None
if compare:
    remaining = [c for c in countries if c != primary_country]
    secondary_country = st.sidebar.selectbox("🆚 Select Country to Compare", remaining)

# --- Utility for top 10 data ---
def get_top10_data(country):
    data = df[df['country_list'] == country]
    return data.sort_values(by='popularity', ascending=False).head(10).copy()

# --- Utility for genre extraction ---
def extract_genres(x):
    try:
        return [g['name'] for g in ast.literal_eval(x)]
    except:
        return []

# --- Utility to plot charts ---
def get_popularity_chart(top10, country):
    return px.bar(top10, x='original_title', y='popularity',
                  title=f"Top 10 Popular Movies in {country}",
                  labels={'original_title': 'Movie', 'popularity': 'Popularity'},
                  height=400)

def get_genre_pie_chart(top10, country):
    top10['genre_list'] = top10['genres'].apply(extract_genres)
    genre_counts = top10.explode('genre_list')['genre_list'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=genre_counts.index,
        values=genre_counts.values,
        pull=[0.1]*len(genre_counts),
        hoverinfo='label+percent',
        textinfo='label+value',
        marker=dict(line=dict(color='#000000', width=2))
    )])
    fig.update_layout(title=f"Genre Distribution in {country}", height=400)
    return fig

# --- Main Section ---
st.title("🎬 Movie Popularity Dashboard")

if not compare:
    # ✅ Single Country Full Mode
    st.header(f"📍 {primary_country}")
    top10 = get_top10_data(primary_country)

    if top10.empty:
        st.warning("No movies found.")
    else:
        # Movie List
        for _, row in top10.iterrows():
            st.markdown(f"**🎥 {row['original_title']}**")
            st.markdown(f"🔥 Popularity: {row['popularity']:.2f} &nbsp;&nbsp; ⭐ Rating: {row['vote_average']}")
            st.caption(row['overview'] if pd.notna(row['overview']) else "No overview available.")
            if pd.notna(row['homepage']):
                st.markdown(f"[🌐 Visit Homepage]({row['homepage']})", unsafe_allow_html=True)
            st.markdown("---")

        # Graphs
        st.subheader("📊 Visual Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(get_popularity_chart(top10, primary_country), use_container_width=True)
        with col2:
            st.plotly_chart(get_genre_pie_chart(top10, primary_country), use_container_width=True)

        # Download
        st.download_button(
            label=f"⬇️ Download CSV for {primary_country}",
            data=top10.to_csv(index=False),
            file_name=f"top10_{primary_country}.csv",
            mime="text/csv"
        )

else:
    # ✅ Two Country Compare Mode
    st.subheader(f"🆚 {primary_country} vs {secondary_country}")
    col1, col2 = st.columns(2)

    with col1:
        top10_1 = get_top10_data(primary_country)
        st.plotly_chart(get_popularity_chart(top10_1, primary_country), use_container_width=True)
        st.plotly_chart(get_genre_pie_chart(top10_1, primary_country), use_container_width=True)

    with col2:
        top10_2 = get_top10_data(secondary_country)
        st.plotly_chart(get_popularity_chart(top10_2, secondary_country), use_container_width=True)
        st.plotly_chart(get_genre_pie_chart(top10_2, secondary_country), use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + TMDb 5000 Dataset")
