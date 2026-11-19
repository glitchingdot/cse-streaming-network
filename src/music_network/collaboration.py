import pandas as pd

import api
import data
import history


def make_collaboration_df(artist_id: str, token: str):
    """
    Takes in an artist ID as a string and a Spotify API token as a
    string and returns a pandas DataFrame containing the artist's
    collaborations.

    Contains the columns collaborator_id, collaborator_name, track_id,
    track_name, play_count, artist_id, and artist_name.
    """
    artist_json = api.get_artist_from_id(artist_id, token)
    if artist_json:
        artist_name = artist_json["name"]
    else:
        return pd.DataFrame()

    # Get albums
    albums: list[data.Album] = api.get_albums_from_artist_id(artist_id, token)

    # Get tracks
    tracks: list[data.Track] = []
    for album in albums:
        new_tracks = api.get_album_tracks(album, token)
        for new_track in new_tracks:
            track_artists = new_track.get_artists()
            if len(track_artists) > 1 and new_track.is_artist_id_in_track(
                artist_id
            ):
                tracks.append(new_track)

    rows = []

    hist_df = history.load_history("Spotify Extended Streaming History")
    track_container_id = "spotify_track_uri"
    sizes = history.plays_per_container(hist_df, track_container_id)
    sizes = sizes.set_index(track_container_id)

    for track in tracks:
        collaborators = track.get_artists()
        for collaborator in collaborators:
            if collaborator.get_id() != artist_id:
                play_count = 0
                if track.get_uri() in sizes.index:
                    play_count = sizes.loc[track.get_uri()].item()

                row_data = [
                    collaborator.get_id(),
                    collaborator.get_name(),
                    track.get_id(),
                    track.get_name(),
                    play_count,
                ]

                rows.append(row_data)

    df = pd.DataFrame(rows)

    if not df.empty:
        df.columns = [
            "collaborator_id",
            "collaborator_name",
            "track_id",
            "track_name",
            "play_count",
        ]
        df["artist_id"] = artist_id
        df["artist_name"] = artist_name
        df = df.drop_duplicates()

    return df


def make_artist_df(artists: list[str], token: str) -> pd.DataFrame:
    """
    Takes in a list of artist IDs as strings and a Spotify API token as a
    string and returns a pandas DataFrame containing the artists'
    collaborations.

    Contains the columns collaborator_id, collaborator_name, track_id,
    track_name, play_count, artist_id, and artist_name.
    """

    df = pd.DataFrame()
    for artist in artists:
        collabs = make_collaboration_df(artist, token)
        df = pd.concat([df, collabs], ignore_index=True)

    return df
