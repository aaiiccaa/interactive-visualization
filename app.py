# Load data
import pandas as pd
import streamlit as st
import plotly.express as px

data = pd.read_csv("songs_normalize.csv")

# Pisahkan genre berdasarkan delimiters koma atau titik koma
data['genre'] = data['genre'].str.split(r'[;,]\s*')

# Ekspansi genre menjadi baris terpisah hanya untuk analisis genre
data_exploded = data.explode('genre')

# UI Streamlit
st.title("Song Analysis Dashboard")

st.subheader("Dataset preview")
st.dataframe(data)  # Tetap gunakan data asli untuk preview\

st.sidebar.title("Dashboard Setting")

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
    data,  # Gunakan data asli tanpa eksplorasi
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
unique_values = data[filter_category].dropna().unique()
selected_value = st.sidebar.selectbox(f"Select {filter_category}", options=["All"] + list(unique_values))

# Tampilkan data yang difilter
if selected_value == "All":
    filtered_data = data
else:
    filtered_data = data[data[filter_category] == selected_value]

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

# Filter data untuk histogram berdasarkan kategori dan tahun
if selected_value == "All":
    genre_filtered_data = data_exploded
else:
    genre_filtered_data = data_exploded[data_exploded[filter_category] == selected_value]

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
    title=f"Total Songs Based on Genres ({filter_category}: {selected_value})"
)
st.plotly_chart(fig)

# Menghitung jumlah lagu berdasarkan nilai "explicit" dengan filter tahun
st.subheader("Songs Having Explicit Content (Filtered by Year)")
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
    template='plotly_dark'
)
st.plotly_chart(fig)
