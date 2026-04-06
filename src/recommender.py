import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    speechiness: float = 0.0
    loudness_db: float = 0.0
    instrumentalness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Returns a numeric score and a list of reasons explaining it."""
        score = 0.0
        reasons = []

        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append(f"genre match ({song.genre}, +2.0)")

        if song.mood == user.favorite_mood:
            score += 1.0
            reasons.append(f"mood match ({song.mood}, +1.0)")

        energy_pts = 1.0 - abs(song.energy - user.target_energy)
        score += energy_pts
        reasons.append(f"energy similarity {energy_pts:.2f}/1.0")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score(user, song)
        return ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "speechiness":      float(row["speechiness"]),
                "loudness_db":      float(row["loudness_db"]),
                "instrumentalness": float(row["instrumentalness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Returns a numeric score and a list of reasons explaining it."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre", ""):
        score += 2.0
        reasons.append(f"genre match ({song['genre']}, +2.0)")

    if song["mood"] == user_prefs.get("mood", ""):
        score += 1.0
        reasons.append(f"mood match ({song['mood']}, +1.0)")

    energy_pts = 1.0 - abs(song["energy"] - float(user_prefs.get("energy", 0.5)))
    score += energy_pts
    reasons.append(f"energy similarity {energy_pts:.2f}/1.0")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Recommending is ranking: score_song judges every song in the catalog,
    then we sort the full scored list and return the top k.
    """
    # Step 1: judge every song in the catalog
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    # Step 2: sort highest score first
    scored.sort(key=lambda x: x[1], reverse=True)

    # Step 3: return the top k
    return scored[:k]
