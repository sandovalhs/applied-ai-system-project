"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile — target values for each scoring feature
    user_prefs = {
        "genre": "kpop",                  # categorical: 0.5x weight (nudge, not dominate)
        "mood": "hype",                   # categorical: 0.5x weight
        "energy": 0.85,                   # high energy tracks
        "tempo_bpm": 130,                 # upbeat tempo
        "valence": 0.50,                  # lowered: covers moody (Weeknd) and upbeat (kpop)
        "danceability": 0.87,             # weighted higher to separate rock from kpop
        "acousticness": 0.04,             # heavily produced, not acoustic
        "speechiness_range": (0.03, 0.82),# range: accepts both sung kpop and rap vocals
        "loudness_db": -4.5,              # loud master
        "instrumentalness": 0.00,         # vocal tracks only
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 50)
    print("  Top Recommendations")
    print("=" * 50)

    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{i}  {song['title']} by {song['artist']}")
        print(f"    Score : {score:.2f} / 4.0")
        print(f"    Why   : {explanation}")


if __name__ == "__main__":
    main()
