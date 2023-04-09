from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from dataclasses import dataclass

tyler_uri = "spotify:artist:4V8LLVI7PbaPR0K2TGSxFF"
spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

results = spotify.artist_albums(tyler_uri, album_type="album")
albums = results["items"]
while results["next"]:
    results = spotify.next(results)
    albums.extend(results["items"])


artists = spotify.artist_related_artists(tyler_uri)


def create_dict_for_object(dataclass, dict):
    dict_k = {
        k: v
        for k, v in dict.items()
        if k in [field for field in dataclass.__annotations__]
    }
    return dict_k


@dataclass
class Artist:
    name: str
    uri: str
    id: str


@dataclass
class AudioFeatures:
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    type: str
    duration_ms: int
    time_signature: int


@dataclass
class Track:
    name: str
    external_urls: str
    artists: list[Artist]
    explicit: bool
    duration_ms: int
    album: str
    uri: str
    id: str
    features: AudioFeatures


def get_tracks_rec_from_artist(
    artist_uri: str, spotify: Spotify, limit: int = 5
) -> list[Track]:
    recs = spotify.recommendations(seed_artists=[artist_uri], limit=limit)
    raw_tracks = recs["tracks"]
    tracks = []
    for track_dict in raw_tracks:
        tracks.append(create_track_from_dict(track_dict))
    return tracks


def get_audio_features_from_track(track_uri: str, spotify: Spotify) -> dict:
    features = spotify.audio_features(track_uri)
    return features[0]


def create_track_from_dict(track_dict: dict) -> Track:
    dict_k = create_dict_for_object(Track, track_dict)
    artists = []
    for artist_dict in dict_k["artists"]:
        artist_obj = Artist(**create_dict_for_object(Artist, artist_dict))
        artists.append(artist_obj)
    audio_features_dict = get_audio_features_from_track(dict_k["uri"], spotify)
    audio_features_obj = AudioFeatures(
        **create_dict_for_object(AudioFeatures, audio_features_dict)
    )
    dict_k["features"] = audio_features_obj

    dict_k["artists"] = artists
    dict_k["album"] = track_dict["album"]["name"]
    track_obj = Track(**dict_k)
    return track_obj


tracks = get_tracks_rec_from_artist(tyler_uri, spotify, limit=5)
ids = [track.id for track in tracks]
print(tracks[0])


def get_artists_related_artists(artist_uri, spotify):
    artists = spotify.artist_related_artists(artist_uri)
    return artists
