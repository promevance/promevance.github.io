# Data dictionary

## Source columns (`data/spotify_data_clean.csv`)

8,582 rows, 15 columns. One row per track.

| Column | Type | Description |
|---|---|---|
| `track_id` | text | Spotify track identifier (unique) |
| `track_name` | text | Track title |
| `track_number` | integer | Position of the track on its album |
| `track_popularity` | integer, 0–100 | Spotify popularity score, based on recent plays |
| `explicit` | boolean | Whether the track is flagged explicit |
| `artist_name` | text | Primary artist (3 rows are blank and removed in preparation) |
| `artist_popularity` | integer, 0–100 | Spotify popularity score for the artist |
| `artist_followers` | integer | Number of Spotify followers of the artist |
| `artist_genres` | text | Comma-separated genre tags for the artist (blank for about 39% of tracks) |
| `album_id` | text | Spotify album identifier |
| `album_name` | text | Album title |
| `album_release_date` | date | Album release date (1952 to 2025) |
| `album_total_tracks` | integer | Number of tracks on the album |
| `album_type` | text | `album`, `single` or `compilation` |
| `track_duration_min` | decimal | Track length in minutes |

`data/track_data_final.csv` is the earlier extract (8,778 rows). It is identical in structure except it holds `track_duration_ms` (milliseconds) instead of `track_duration_min`.

## Derived fields (created in Tableau Prep)

| Field | Type | Logic |
|---|---|---|
| `Release Year` | integer | `YEAR(album_release_date)` |
| `Content` | text | "Explicit" if `explicit` is true, otherwise "Clean" |
| `Genres` | text | `artist_genres` with quote marks removed; "Unknown" when blank |
| `Primary Genre` | text | First genre in `Genres` |
| `Artist Tier` | text | Superstar (10M+), Established (1M–10M), Developing (100K–1M) or Emerging (<100K) followers |
| `Genre Family` | text | One of 11 families from keyword rules on `Primary Genre` (see [methodology](methodology.md)) |

## Metrics used in the dashboard

| Metric | Definition |
|---|---|
| Hit | `track_popularity >= 70` |
| Hit rate | Share of tracks that are hits |
| Average popularity | Mean of `track_popularity` |
| Explicit share | Share of tracks where `explicit` is true |
| Share of new hits | Share of hits released in a period belonging to a group |

## Data quality notes

- Track IDs are unique in both files.
- Missing values in the cleaned file: `artist_genres` (3,361 rows) and `artist_name` (3 rows). Rows with no artist are dropped by the Prep flow.
- A few artists show 0 followers in the source data.
