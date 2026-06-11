import streamlit as st
st.set_page_config(page_title="Siren Music", layout="wide")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from fuzzywuzzy import process, fuzz
import numpy as np

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/vedangm/Downloads/cleaned_music_data.csv")  # Change to your path
    df = df[df['preview'].notna() & df['preview'].str.startswith("http")]
    
    # Ensure 'img' column is present and fill missing values
    df['img'] = df['img'].fillna("https://via.placeholder.com/150")  # Default image for missing data
    
    return df.reset_index(drop=True)

df = load_data()

# Session state initialization
if "now_playing" not in st.session_state:
    st.session_state["now_playing"] = None
if "page" not in st.session_state:
    st.session_state.page = 0

st.title("🎶 Siren Music Streamer")

# Search Bar
search_input = st.text_input("Search for a song or artist:")

if search_input:
    name_matches = process.extract(search_input, df['name'], scorer=fuzz.token_sort_ratio, limit=10)
    artist_matches = process.extract(search_input, df['artist'], scorer=fuzz.token_sort_ratio, limit=10)
    matched_names = [match[0] for match in name_matches + artist_matches]
    search_df = df[df['name'].isin(matched_names) | df['artist'].isin(matched_names)].copy()
else:
    search_df = df.head(10).copy()

# Pagination logic
songs_per_page = 5
total_pages = (len(search_df) // songs_per_page) + (1 if len(search_df) % songs_per_page else 0)

# Navigation for pages
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Previous", disabled=st.session_state.page == 0):
        st.session_state.page -= 1
with col2:
    st.markdown(f"<div style='text-align: center;'>Page {st.session_state.page + 1} of {total_pages}</div>", 
               unsafe_allow_html=True)
with col3:
    if st.button("Next ➡️", disabled=st.session_state.page == total_pages - 1 or total_pages == 0):
        st.session_state.page += 1

# Display current page results
start_idx = st.session_state.page * songs_per_page
end_idx = start_idx + songs_per_page
current_page_results = search_df.iloc[start_idx:end_idx]

# Display search results (5 songs horizontally)
search_cols = st.columns(5)
for idx, row in enumerate(current_page_results.itertuples()):
    with search_cols[idx]:
        # Ensure that 'img' column exists and handle missing values
        img_url = row.img if pd.notna(row.img) and row.img != 'no' else "https://via.placeholder.com/150"
        
        # Clickable image that selects the song
        st.image(img_url, width=150, use_container_width=False)
        
        if st.button("▶️", key=f"play_{row.Index}"):
            st.session_state["now_playing"] = {
                "name": row.name,
                "artist": row.artist,
                "preview": row.preview
            }
        st.caption(f"**{row.name}**")
        if row.artist:
            st.caption(row.artist)
            
# Recommendation Engine
# Top 5 feature selection
top_features = ['loudness', 'energy', 'acousticness', 'danceability', 'valence']
scaler = StandardScaler()
feature_matrix = scaler.fit_transform(df[top_features]).astype(np.float32)

# Recommendation function
def get_recommendations(song_name, top_n=5):
    if song_name not in df['name'].values:
        return f"'{song_name}' not found in dataset."
    
    idx = df[df['name'] == song_name].index[0]
    song_vector = feature_matrix[idx].reshape(1, -1)
    similarity_scores = cosine_similarity(song_vector, feature_matrix)[0]
    similar_indices = similarity_scores.argsort()[::-1][1:top_n+1]
    
    recommendations = df.iloc[similar_indices][['name', 'artist', 'img', 'preview']]
    return recommendations

# Recommendations Section
if st.session_state["now_playing"]:
    st.subheader("🎯 Recommended for You")
    rec_df = get_recommendations(st.session_state["now_playing"]["name"])
    rec_cols = st.columns(5)
    
    for i, row in enumerate(rec_df.itertuples()):
        with rec_cols[i]:
            st.image(row.img, width=150)
            st.caption(f"**{row.name}**\n{row.artist}")
            if st.button("▶️ Play", key=f"rec_{row.Index}"):
                st.session_state["now_playing"] = {
                    "name": row.name,
                    "artist": row.artist,
                    "preview": row.preview
                }

# Now Playing Section
if st.session_state["now_playing"]:
    song = st.session_state["now_playing"]
    st.markdown("---")
    st.markdown(f"### 🔊 Now Playing: **{song['name']}** by *{song['artist']}*")
    st.audio(song["preview"], format="audio/mp3")
    st.info("Click the ▶️ button on the player above to start playback. Autoplay is blocked by your browser.")
