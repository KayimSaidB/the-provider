from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from dataclasses import dataclass, fields

tyler_uri = "spotify:artist:4V8LLVI7PbaPR0K2TGSxFF"
spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

results = spotify.artist_albums(tyler_uri, album_type="album")
albums = results["items"]
while results["next"]:
    results = spotify.next(results)
    albums.extend(results["items"])


artists = spotify.artist_related_artists(tyler_uri)


@dataclass
class Track:
    name: str
    external_urls: str
    artists: list[str]
    explicit: bool
    duration_ms: int
    album: str
    uri: str


def get_tracks_rec_from_artist(
    artist_uri: str, spotify: Spotify, limit: int = 5
) -> list[Track]:
    recs = spotify.recommendations(seed_artists=[artist_uri], limit=limit)
    raw_tracks = recs["tracks"]
    tracks = []
    for track in raw_tracks:
        track_obj = Track(**{k: v for k, v in track.items() if k in fields(Track)})
        tracks.append(track_obj)

    return tracks


tracks = get_tracks_rec_from_artist(tyler_uri, spotify, limit=5)


def get_artists_related_artists(artist_uri, spotify):
    artists = spotify.artist_related_artists(artist_uri)
    return artists
