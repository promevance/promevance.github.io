"""
Reproduce the headline figures behind "Widening the Spotlight" in pandas.

The dashboard itself was built in Tableau (see tableau/). This script re-creates the same
field logic that lives in the Tableau Prep flow so that every number quoted in the case study
can be checked without opening Tableau.

Usage (from this folder):
    pip install pandas
    python reproduce_key_figures.py

Notes
-----
* Input is data/spotify_data_clean.csv (8,582 rows).
* Rows with no artist name are dropped, exactly like the Tableau Prep step "Drop bad rows".
  That leaves 8,579 rows here; the published dashboard reports 8,577 tracks, so this script
  can differ from the dashboard by about two rows. Every percentage matches to the rounding
  used in the dashboard (differences are well under one percentage point).
* A "hit" is a track with a Spotify popularity score of 70 or more (out of 100).
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data" / "spotify_data_clean.csv"
HIT_THRESHOLD = 70


# --------------------------------------------------------------------------- field logic
def artist_tier(followers: float) -> str:
    """Mirror of the Tableau Prep calculation `Artist Tier`."""
    if followers >= 10_000_000:
        return "Superstar (10M+)"
    if followers >= 1_000_000:
        return "Established (1M-10M)"
    if followers >= 100_000:
        return "Developing (100K-1M)"
    return "Emerging (<100K)"


# Order matters: the first matching family wins, exactly as in the Tableau IF / ELSEIF chain.
GENRE_FAMILIES = [
    ("Latin", ["latin", "reggaeton", "urbano", "corrido", "bachata", "cumbia", "salsa", "dembow"]),
    ("K-pop", ["k-pop", "k-rap"]),
    ("Hip-Hop & Rap", ["hip hop", "rap", "trap", "drill", "grime", "phonk"]),
    ("R&B & Soul", ["r&b", "soul"]),
    ("Rock & Metal", ["rock", "metal", "grunge", "punk", "emo"]),
    ("Country & Folk", ["country", "folk"]),
    ("Soundtrack & Classical", ["soundtrack", "anime", "medieval", "classical", "children"]),
    ("Pop", ["pop"]),
    ("Electronic & Dance", ["edm", "house", "techno", "electro", "dance", "dubstep"]),
]


def genre_family(primary_genre: str) -> str:
    """Mirror of the Tableau Prep calculation `Genre Family`."""
    if primary_genre == "Unknown":
        return "Unknown"
    g = primary_genre.lower()
    for family, keywords in GENRE_FAMILIES:
        if any(k in g for k in keywords):
            return family
    return "Other"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df = df[df["artist_name"].notna()].copy()  # "Drop bad rows"

    df["Release Year"] = pd.to_datetime(df["album_release_date"], errors="coerce").dt.year
    df["Content"] = df["explicit"].map({True: "Explicit", False: "Clean"})
    df["Genres"] = df["artist_genres"].fillna("Unknown").str.replace('"', "").str.strip()
    df["Primary Genre"] = df["Genres"].str.split(",").str[0].str.strip()
    df["Artist Tier"] = df["artist_followers"].apply(artist_tier)
    df["Genre Family"] = df["Primary Genre"].apply(genre_family)
    df["Hit"] = df["track_popularity"] >= HIT_THRESHOLD
    return df


# --------------------------------------------------------------------------- report
def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> None:
    df = load()
    hits = df[df["Hit"]]

    print("== The stage ==")
    print(f"Tracks: {len(df):,} | artists: {df['artist_name'].nunique():,} | albums: {df['album_id'].nunique():,}")
    print(f"Average popularity: {df['track_popularity'].mean():.1f} | hit rate: {pct(df['Hit'].mean())} "
          f"| explicit: {pct(df['explicit'].mean())} | avg length: {df['track_duration_min'].mean():.2f} min")
    print(f"Released after 2015: {pct((df['Release Year'] > 2015).mean())} | tracks from 2025: {(df['Release Year'] == 2025).sum()}")

    print("\n== Who holds the spotlight (by artist tier) ==")
    artists = df.drop_duplicates("artist_name")
    tier = df.groupby("Artist Tier").agg(tracks=("Hit", "size"), hits=("Hit", "sum"), hit_rate=("Hit", "mean"))
    tier["share_of_artists"] = artists["Artist Tier"].value_counts(normalize=True)
    tier["share_of_tracks"] = tier["tracks"] / tier["tracks"].sum()
    tier["share_of_hits"] = tier["hits"] / tier["hits"].sum()
    print(tier.sort_values("hit_rate", ascending=False).round(3).to_string())

    print("\n== Hit rate by genre family (top-level view) ==")
    fam = df.groupby("Genre Family").agg(tracks=("Hit", "size"), hit_rate=("Hit", "mean"))
    fam["share_of_tracks"] = fam["tracks"] / len(df)
    print(fam.sort_values("hit_rate", ascending=False).round(3).to_string())

    print("\n== Where tastes are widening (share of hits by release period) ==")
    df["Period"] = pd.cut(df["Release Year"], [2009, 2015, 2020, 2025], labels=["2010-15", "2016-20", "2021-25"])
    hits = df[df["Hit"]]
    rows = []
    for period, grp in hits.groupby("Period", observed=True):
        lk = grp["Genre Family"].isin(["Latin", "K-pop"])
        rows.append({
            "period": period,
            "hits": len(grp),
            "latin_kpop_share": lk.mean(),
            "superstar_share": (grp["Artist Tier"] == "Superstar (10M+)").mean(),
            "latin_kpop_artists_with_a_hit": grp.loc[lk, "artist_name"].nunique(),
        })
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    print("\n== Shifting habits ==")
    df["Single"] = df["album_type"] == "single"
    habits = df[df["Release Year"].isin([2010, 2025])].groupby("Release Year").agg(
        singles_share=("Single", "mean"), avg_length_min=("track_duration_min", "mean"))
    print(habits.round(3).to_string())


if __name__ == "__main__":
    main()
