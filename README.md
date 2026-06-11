# Siren Music Streamer

A web-based music discovery and preview app built with **Streamlit**. Search songs and artists, play 30-second previews, and get personalized recommendations powered by audio feature similarity.

---

## Features

- **Fuzzy search** — Find songs and artists using approximate string matching (`fuzzywuzzy`)
- **Paginated browsing** — Browse results five songs at a time with Previous/Next navigation
- **Audio previews** — Stream 30-second preview clips via an embedded player
- **Smart recommendations** — Discover similar tracks using cosine similarity on audio features (loudness, energy, acousticness, danceability, valence)
- **Album art display** — Show cover images with a fallback placeholder for missing artwork

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| Data handling | [Pandas](https://pandas.pydata.org/) |
| Machine learning | [scikit-learn](https://scikit-learn.org/) (StandardScaler, cosine similarity) |
| Fuzzy matching | [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) |
| Numerical computing | [NumPy](https://numpy.org/) |

---

## Project Structure

```
Desktop/
├── Syren.py              # Main Streamlit application
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── .venv/                # Python virtual environment (created during setup)
└── cleaned_music_data.csv  # Dataset (place in Downloads or update path in Syren.py)
```

---

## Dataset

The app reads from a CSV file with the following key columns:

| Column | Description |
|--------|-------------|
| `name` | Song title |
| `artist` | Artist name |
| `preview` | URL to a 30-second audio preview (must start with `http`) |
| `img` | Album cover image URL |
| `loudness`, `energy`, `acousticness`, `danceability`, `valence` | Audio features used for recommendations |

By default, the data path is set in `Syren.py`:

```python
df = pd.read_csv("/Users/vedangm/Downloads/cleaned_music_data.csv")
```

Update this path to match your local CSV location before running.

---

## Installation

### Prerequisites

- Python 3.10+
- macOS users: use a **virtual environment** (Homebrew Python blocks system-wide `pip install`)

### 1. Create and activate a virtual environment

```bash
cd /Users/vedangm/Desktop
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Verify imports

```bash
python -c "import numpy, pandas, sklearn; print('all imports OK')"
```

---

## Running the App

With the virtual environment activated, run:

```bash
python -m streamlit run Syren.py
```

> **Note:** Use `python -m streamlit` instead of bare `streamlit run` if your shell resolves `streamlit` to a global install outside the venv.

The app opens at **http://localhost:8501**.

---

## How It Works

### Search

When you type in the search bar, the app uses fuzzy string matching against song names and artist names, returning the top matches. With no search query, the first 10 songs in the dataset are shown.

### Playback

Click the ▶️ button on any song card to set it as **Now Playing**. The audio player appears at the bottom of the page. Browsers block autoplay, so you must click play on the player manually.

### Recommendations

When a song is playing, the app:

1. Selects five audio features: `loudness`, `energy`, `acousticness`, `danceability`, `valence`
2. Standardizes features with `StandardScaler`
3. Computes cosine similarity between the current song and all others in the dataset
4. Returns the top 5 most similar tracks (excluding the current song)

---

## Object-Oriented Programming (OOP) Concepts

The current application is written in a procedural, script-based style using functions and Streamlit session state. However, **OOP principles can be applied or extended** to create a more modular and reusable architecture.

### 1. Encapsulation

**Encapsulation** bundles data and the methods that operate on that data within a single unit (a class), keeping internal details organized and controlled.

**Application in this project:**

A `Song` class could encapsulate all attributes related to a track — `name`, `artist`, `preview`, `img` — along with methods such as `play_preview()` and `get_recommendations()`. This keeps song-related logic in one place instead of scattered across dictionaries and session state.

```python
class Song:
    def __init__(self, name, artist, preview, img):
        self.name = name
        self.artist = artist
        self.preview = preview
        self.img = img

    def play_preview(self):
        return self.preview

    def get_recommendations(self, engine, top_n=5):
        return engine.recommend(self.name, top_n)
```

---

### 2. Abstraction

**Abstraction** hides complex implementation details and exposes only what the user (or calling code) needs.

**Application in this project:**

The recommendation logic — feature scaling, similarity scoring, and ranking — could be abstracted into a `RecommendationEngine` class. The main app would simply call `engine.recommend(song_name)` without needing to know how similarity is calculated internally.

```python
class RecommendationEngine:
    def __init__(self, df, features):
        self._df = df
        self._features = features
        self._matrix = self._build_feature_matrix()

    def recommend(self, song_name, top_n=5):
        # Internal: scaling, cosine similarity, ranking
        ...
```

---

### 3. Inheritance

**Inheritance** allows a class to inherit attributes and methods from a parent class, reducing redundancy and making the codebase easier to extend.

**Potential application in this project:**

If the app grows to support user accounts and admin features:

- A base `Account` class holds shared attributes (`username`, `email`) and methods (`login()`, `logout()`)
- A `User` class inherits from `Account` and adds user-specific behavior (playlists, favorites)
- An `Admin` class inherits from `User` and adds privileges (manage songs, users, settings)

```python
class Account:
    def login(self): ...
    def logout(self): ...

class User(Account):
    def create_playlist(self): ...

class Admin(User):
    def manage_catalog(self): ...
```

---

### 4. Polymorphism

**Polymorphism** allows methods with the same name to behave differently depending on the object type, enabling flexible and interchangeable interfaces.

**Application in this project:**

If the app supports multiple media types (songs, podcasts, albums), a base `Media` class could define a `play()` method that each subclass overrides:

```python
class Media:
    def play(self):
        raise NotImplementedError

class Song(Media):
    def play(self):
        return self.preview_url

class Podcast(Media):
    def play(self):
        return self.episode_url
```

The UI could call `media.play()` on any object without checking its type explicitly.

---

### 5. Composition

**Composition** builds complex behavior by combining simpler objects, where one class holds references to instances of other classes rather than inheriting from them.

**Application in this project:**

A `Song` object could **contain** an `Artist` object instead of storing the artist name as a plain string. This separates artist-specific data (bio, genre, discography) from song-specific data while still allowing the song to access artist information.

```python
class Artist:
    def __init__(self, name, genre):
        self.name = name
        self.genre = genre

class Song:
    def __init__(self, name, artist: Artist, preview, img):
        self.name = name
        self.artist = artist
        self.preview = preview
        self.img = img
```

---

## Current vs. Proposed Architecture

| Aspect | Current implementation | OOP-enhanced approach |
|--------|------------------------|------------------------|
| Song data | Dictionaries in `st.session_state` | `Song` class with encapsulated attributes |
| Recommendations | Standalone `get_recommendations()` function | `RecommendationEngine` class |
| Search | Inline fuzzy matching logic | `SearchService` class |
| User roles | Not implemented | `Account` → `User` → `Admin` inheritance hierarchy |
| Media types | Songs only | `Media` base class with `Song`, `Podcast` subclasses |

---

## Known Limitations

- Pagination does not reset when the search query changes
- Duplicate song names in the dataset may return incorrect recommendations (lookup uses song name only)
- The CSV path is hardcoded and must be updated per machine
- Audio feature matrix is rebuilt on every app rerun (could be cached for better performance)

---

## Future Enhancements

- Refactor into OOP classes (`Song`, `RecommendationEngine`, `SearchService`)
- Add user accounts with playlists and favorites
- Support additional media types (podcasts, albums) via polymorphism
- Reset pagination on new searches
- Use `spotify_id` for unique song identification in recommendations
- Add configurable data path via environment variables

---

## License

This project is for educational and personal use.
