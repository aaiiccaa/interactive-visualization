import pandas as pd
import streamlit as st
import plotly.express as px

# Load data
data = pd.read_csv("songs_normalize.csv")

# Pisahkan genre berdasarkan delimiters koma atau titik koma
data['genre'] = data['genre'].str.split(r'[;,]\s*')

# Ekspansi genre menjadi baris terpisah hanya untuk analisis genre
data_exploded = data.explode('genre')

# UI Streamlit
st.title("Song Analysis Dashboard")

st.subheader("Dataset preview")
st.dataframe(data) 

st.sidebar.title("Dashboard Settings")

# Menu untuk Scatter Plot
numeric_columns = [
    "duration_ms", "year", "popularity", "danceability", "energy", "key", 
    "loudness", "mode", "speechiness", "acousticess", "instrumentalness", 
    "liveness", "valence", "tempo"
]
category_columns = ["artist", "song", "explicit", "genre"]

x_axis = st.sidebar.selectbox("X-axis", numeric_columns)
y_axis = st.sidebar.selectbox("Y-axis", numeric_columns)
category = st.sidebar.selectbox("Category", category_columns)

st.subheader("Scatter Plot")
scatter_fig = px.scatter(
    data, 
    x=x_axis,
    y=y_axis,
    color=category,
    title=f"Scatter Plot of {x_axis} vs {y_axis}",
    labels={x_axis: x_axis, y_axis: y_axis}
)
st.plotly_chart(scatter_fig)

st.sidebar.subheader("Filter Data")

# Filter Genre
filter_category = st.sidebar.selectbox("Filter by Category", category_columns)

#tipe kolom genre beda
if filter_category == "genre":
    unique_values = data_exploded['genre'].dropna().unique()
else:
    unique_values = data[filter_category].dropna().unique()

selected_value = st.sidebar.selectbox(f"Select {filter_category}", options=["All"] + list(unique_values))

# Tampilkan data yang difilter
if filter_category == "genre":
    if selected_value == "All":
        filtered_data = data  # Jika "All", jangan filter, gunakan data asli
    else:
        filtered_data = data_exploded[data_exploded['genre'] == selected_value]  # Filter berdasarkan genre
elif selected_value == "All":
    filtered_data = data  # Jika "All", gunakan data asli
else:
    filtered_data = data[data[filter_category] == selected_value]  # Filter untuk kategori lainnya


st.subheader(f"Filtered Data (Category: {filter_category} = {selected_value})")
st.dataframe(filtered_data)

st.subheader("Bar Chart for Filtered Data")
bar_chart = px.bar(
    filtered_data,
    x="year",
    y="popularity",
    title=f"Bar Chart for {selected_value}",
    labels={x_axis: x_axis, y_axis: y_axis}
)
st.plotly_chart(bar_chart)

# Histogram based on genre
st.subheader("Total Songs Based on Genres")

# Slider untuk memilih rentang tahun
min_year, max_year = int(data_exploded['year'].min()), int(data_exploded['year'].max())
selected_year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data berdasarkan kategori jika kategori yang dipilih adalah artis
if filter_category == "artist" and selected_value != "All":
    genre_filtered_data = data_exploded[data_exploded['artist'] == selected_value]
else:
    genre_filtered_data = data_exploded

# Filter data berdasarkan rentang tahun
genre_filtered_data = genre_filtered_data[
    (genre_filtered_data['year'] >= selected_year_range[0]) & (genre_filtered_data['year'] <= selected_year_range[1])
]

# Hitung jumlah lagu berdasarkan genre untuk filter yang dipilih
genre_count = genre_filtered_data.groupby('genre', as_index=False).size().rename(columns={'size': 'song_count'})

# Buat histogram
fig = px.histogram(
    genre_count,
    x='genre',
    y='song_count',
    color_discrete_sequence=['green'],
    template='plotly_dark',
    title=f"Total Songs Based on Genres"
)
st.plotly_chart(fig)

# Hitung rata-rata popularitas berdasarkan genre dan tahun
genre_year_popularity = genre_filtered_data.groupby(['year', 'genre'], as_index=False)['popularity'].mean()

# Line chart untuk melihat tren popularitas genre berdasarkan tahun
st.subheader("Genre Popularity Over the Years")

line_chart = px.line(
    genre_year_popularity, 
    x='year', 
    y='popularity', 
    color='genre',  # Membuat setiap genre memiliki warna sendiri
    title="Popularity of Songs by Genre Over the Years", 
    labels={"year": "Year", "popularity": "Average Popularity"}
)
st.plotly_chart(line_chart)

# Menghitung jumlah lagu berdasarkan nilai "explicit" dengan filter tahun
explicit_filtered_data = data[
    (data['year'] >= selected_year_range[0]) & (data['year'] <= selected_year_range[1])
]
explicit_count = explicit_filtered_data.groupby('explicit', as_index=False).size().rename(columns={'size': 'song_count'})

fig = px.pie(
    explicit_count,
    names='explicit',
    values='song_count',
    labels={'song_count': 'Total Songs'},
    hole=0.6,
    color_discrete_sequence=['green', 'crimson'],
    template='plotly_dark',
    title='<b>Songs Having Explicit Content (Filtered by Year)</b>'
)
st.plotly_chart(fig)

# Line chart untuk melihat tren popularitas berdasarkan tahun
st.subheader("Line Chart of Popularity Over the Years")

line_chart = px.line(
    filtered_data, 
    x='year', 
    y='popularity', 
    title="Popularity of Songs Over the Years", 
    labels={"year": "Year", "popularity": "Popularity"}
)
st.plotly_chart(line_chart)