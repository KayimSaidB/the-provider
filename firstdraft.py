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
class Artist:
    name: str
    uri: str
    id: str


@dataclass
class Track:
    name: str
    external_urls: str
    artists: list[Artist]
    explicit: bool
    duration_ms: int
    # album: str
    uri: str
    id: str


def get_tracks_rec_from_artist(
    artist_uri: str, spotify: Spotify, limit: int = 5
) -> list[Track]:
    recs = spotify.recommendations(seed_artists=[artist_uri], limit=limit)
    raw_tracks = recs["tracks"]
    tracks = []
    for track_dict in raw_tracks:
        tracks.append(create_track_from_dict(track_dict))
    return tracks


def create_track_from_dict(track_dict: dict) -> Track:
    print(track_dict["album"])
    dict_k = {
        k: v
        for k, v in track_dict.items()
        if k in [field.name for field in fields(Track)]
    }
    artists = []
    for artist in dict_k["artists"]:
        dict_artist = {
            k: v
            for k, v in artist.items()
            if k in [field.name for field in fields(Artist)]
        }
        artist_obj = Artist(**dict_artist)
        artists.append(artist_obj)
    dict_k["artists"] = artists
    track_obj = Track(**dict_k)
    return track_obj


# TODO: factorize the creation

tracks = get_tracks_rec_from_artist(tyler_uri, spotify, limit=5)
# print(tracks)


def get_artists_related_artists(artist_uri, spotify):
    artists = spotify.artist_related_artists(artist_uri)
    return artists
