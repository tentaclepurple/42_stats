import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

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

    /* Centrado de contenido */
    .block-container {
        max-width: 9000px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        margin: 0 auto;
    }

    /* Centrado del título */
    h1 {
        text-align: center;
    }
    /* Ajuste de los selectbox */
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

@st.cache_data
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
        selected_country = st.selectbox("País", country_options)

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
    st.write("Work in progress...")
