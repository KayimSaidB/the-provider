from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from dataclasses import dataclass
import lyricsgenius
from sentiment_analysis import text_similarity
from similarity import compute_similarity_score
import numpy as np
import logging

LOGGER = logging.getLogger(__name__)
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
    duration_ms: int
    time_signature: int

    def to_vec(self) -> np.ndarray:
        return np.array(
            [
                self.danceability,
                self.energy,
                self.key,
                self.loudness,
                self.mode,
                self.speechiness,
                self.acousticness,
                self.instrumentalness,
                self.liveness,
                self.valence,
                self.tempo,
            ]
        )


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
    lyrics: str = None


def get_tracks_rec(
    spotify: Spotify,
    artist_uri: str = None,
    track_uri: str = None,
    limit: int = 5,
) -> list[Track]:
    recs = spotify.recommendations(
        seed_artists=[artist_uri] if artist_uri else None,
        seed_tracks=[track_uri] if track_uri else None,
        limit=limit,
    )
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


def set_lyrics_for_track(track: Track, genius: lyricsgenius.Genius) -> None:
    song = genius.search_song(title=track.name, artist=track.artists[0].name)
    if song:
        track.lyrics = song.lyrics
    else:
        LOGGER.warn("No lyrics found for this song")


def get_artist_from_name(name: str, spotify: Spotify) -> Artist:
    results = spotify.search(q="artist:" + name, type="artist")
    items = results["artists"]["items"]
    if len(items) > 0:
        artist = items[0]
        return Artist(**create_dict_for_object(Artist, artist))
    else:
        return None


def get_track_from_names(spotify: Spotify, track_name: str, artist_name: str) -> Track:
    results = spotify.search(
        q="track:" + track_name + " artist:" + artist_name, type="track"
    )
    items = results["tracks"]["items"]
    if len(items) > 0:
        track = items[0]
        return create_track_from_dict(track)
    else:
        return None


artist = get_artist_from_name("alpha wann", spotify)
luther_uri = artist.uri
print(luther_uri)
tracks = get_tracks_rec(spotify, artist_uri=luther_uri, limit=5)
ids = [track.id for track in tracks]
genius = lyricsgenius.Genius()
# set_lyrics_for_track(tracks[0], genius)

# set_lyrics_for_track(tracks[1], genius)

#


def get_artists_related_artists(artist_uri, spotify):
    artists = spotify.artist_related_artists(artist_uri)
    return artists


artist = get_artist_from_name("alpha wann", spotify)
track_tiako = get_track_from_names(spotify, "coucher de soleil", "tiakola")
set_lyrics_for_track(track_tiako, genius)
gun_salute = get_track_from_names(spotify, "gun salute", "kaaris")
set_lyrics_for_track(gun_salute, genius)
bosseur = get_track_from_names(spotify, "bosseur", "rsko")
set_lyrics_for_track(bosseur, genius)


print(track_tiako.features)
print(gun_salute.features)
print(bosseur.features)
"""tracks = get_tracks_rec(spotify, track_uri=track_tiako.uri, limit=20)

for track in tracks:
    set_lyrics_for_track(track, genius)
# compute distance between two arrays
distance_dict = {}
for track in tracks:
    if track.lyrics is None:
        continue
    distance_dict[track.name] = (
        text_similarity(track_tiako.lyrics, track.lyrics),
        np.linalg.norm(track.features.to_vec() - track_tiako.features.to_vec()),
    )

# print the 10 closest tracks
for key, value in sorted(distance_dict.items(), key=lambda item: item[1][1])[:10]:
    print(key, value[0], value[1])
"""
