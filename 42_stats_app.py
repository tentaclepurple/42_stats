import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

load_dotenv()

st.set_page_config(
    page_title="42 Students Leaderboard",
    page_icon="🏆",
    layout="wide"
)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        padding-right: 1rem;
        padding-left: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
    }
    .stTabs [aria-selected="true"]
    .stTabs [data-baseweb="tab-highlight"]

    .block-container {
        max-width: 9000px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        margin: 0 auto;
    }

    h1 {
        text-align: center;
    }
    div.row-widget.stSelectbox {
        width: 90%;
        margin: 0 auto;
    }
    div.search-container > div > div > input {
        border-radius: 5px;
        width: 100% !important; /* Ocupa todo el ancho de la columna */
    }

    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_mongo_client():
    ATLAS_URI = os.getenv('ATLAS_URI')
    DB_NAME = os.getenv('DB_NAME')
    return MongoClient(ATLAS_URI), DB_NAME

@st.cache_data(ttl=0)
def get_data():
    client, db_name = get_mongo_client()
    db = client[db_name]
    collection = db['users']

    cursor = collection.find(
        {},
        {
            '_id': 1,
            'login': 1,
            'level': 1,
            'campus': 1,
            'country': 1,
            'coalition': 1
        }
    )

    data = list(cursor)
    client.close()

    df = pd.DataFrame(data)
    df['coalition'] = df['coalition'].fillna('Unknown')
    return df


tab1, tab2 = st.tabs(["🏆 Leaderboard", "📊 Statistics"])

with tab1:
    st.title("42 Students Leaderboard")

    df = get_data()

    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
    with col2:
        campus_options = ["All"] + sorted(df['campus'].unique().tolist())
        selected_campus = st.selectbox("Campus", campus_options)

    with col3:
        country_options = ["All"] + sorted(df['country'].unique().tolist())
        selected_country = st.selectbox("Country", country_options)

    filtered_df = df.copy()
    if selected_campus != "All":
        filtered_df = filtered_df[filtered_df['campus'] == selected_campus]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]

    filtered_df = filtered_df.sort_values('level', ascending=False).reset_index(drop=True)
    filtered_df.insert(0, 'rank', range(1, len(filtered_df) + 1))

    col_search1, col_search2, col_search3 = st.columns([3, 1, 3])
    with col_search2:
        with st.container():
            search_login = st.text_input("Login search:", placeholder="Introduce a login", key="search_box")

    if search_login:
        filtered_df = filtered_df[filtered_df['login'].str.contains(search_login, case=False)]
    st.divider()

    col_df1, col_df2, col_df3 = st.columns([6.7, 9, 2])
    with col_df2:
        st.dataframe(
            filtered_df[['rank', 'login', 'level', 'campus', 'country']],
            column_config={
                'rank': st.column_config.NumberColumn(format="%d"),
                'level': st.column_config.NumberColumn(format="%.2f"),
                'login': st.column_config.TextColumn()
            },
            hide_index=True
        )

with tab2:
    st.title("Statistics")

    df = get_data()

    fig1 = px.histogram(df, x="level", nbins=50,
                       title="Distribution of Student Levels",
                       color_discrete_sequence=["#2ecc71"])
    fig1.update_layout(xaxis_title="Level", yaxis_title="Number of Students")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    campus_counts = df['campus'].value_counts().nlargest(10)
    fig2 = px.bar(x=campus_counts.index, y=campus_counts.values,
                  title="Top 10 Campuses by Number of Students",
                  color_discrete_sequence=["#2ecc71"],
                  labels={'x': 'Campus', 'y': 'Number of Students'})
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']

    fig3 = px.choropleth(country_counts,
                        locations="country",
                        color="count",
                        locationmode="country names",
                        color_continuous_scale=px.colors.sequential.Greens,
                        title="Distribution of Students by Country")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    campus_avg_level = df.groupby('campus')['level'].mean().sort_values(ascending=False)
    fig4 = px.bar(x=campus_avg_level.index, y=campus_avg_level.values,
                  title="Average Level by Campus",
                  color_discrete_sequence=["#2ecc71"],
                  labels={'x': 'Campus', 'y': 'Average Level'})
    st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    campus_avg = df.groupby('campus')['level'].mean().reset_index()
    campus_avg.columns = ['campus', 'average_level']

    campus_avg = pd.merge(campus_avg, df[['campus', 'country']].drop_duplicates(), on='campus')

    fig5 = px.choropleth(campus_avg,
                        locations="country",
                        color="average_level",
                        locationmode="country names",
                        color_continuous_scale=px.colors.sequential.Greens,
                        hover_data=['campus', 'average_level'],  # Mostrar campus y nivel promedio en hover
                        title="Average Level by Campus (Map)")
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    fig6 = px.density_heatmap(df, x="level", y="campus",
                             marginal_x="histogram", marginal_y="box",
                             color_continuous_scale=px.colors.sequential.Greens,
                             title="Student Level Density by Campus")
    st.plotly_chart(fig6, use_container_width=True)
