"""
Jack K
This module implements API calls and authentication with Spotify's API
"""

import requests
import os
import base64
import urllib.parse

from dotenv import load_dotenv

import data
import cache


def format_client_information():
    """
    Imports and formats environment variables for use in authentication
    with Spotify's API.
    """
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    unformatted_information = f"{client_id}:{client_secret}"
    as_bytes = unformatted_information.encode("ascii")

    as_base64_bytes = base64.b64encode(as_bytes)
    base64_string = as_base64_bytes.decode("ascii")

    result = f"Basic {base64_string}"

    return result


def authorize_client_credentials_flow() -> str | None:
    """
    Authorizes with Spotify's API. Returns
    an access token to provide with future
    calls.
    """
    headers = {
        "Authorization": format_client_information(),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(
        "https://accounts.spotify.com/api/token", headers=headers, data=data
    )

    print("Authorizing...")

    if response.status_code == 200:
        print("Authorized!")
        return response.json()["access_token"]
    else:
        return None


def get_artist_from_id(artist_id: str, token: str):
    """
    Takes in an artist id and returns an artist's API JSON either from
    the Spotify API or from cached files. Requires an authentication token as
    a string.
    """
    return cache.make_cached_call(
        "https://api.spotify.com/v1/artists/{}", artist_id, token
    )


def get_track_from_id(track_id: str, token):
    """
    Takes in an album id and returns the album's API JSON either from
    the Spotify API or from cached files. Requires an authentication token as
    a string.
    """
    return cache.make_cached_call(
        "https://api.spotify.com/v1/tracks/{}", track_id, token
    )


def get_albums_from_artist_id(
    artist_id: str, token: str, offset: int = 0, albums: list[data.Album] = []
):
    """
    Gets all Albums owned by a given artist_id either from the API or local
    cache. Returns a list of Albums containing the id and name of each album
    owned by the artist. Requires an authentication token as a string.
    """

    url = "https://api.spotify.com/v1/artists/{}/albums"

    params = {
        "include_groups": "album,single,appears_on",
        "limit": 10,
        "offset": offset,
    }

    resp_json = cache.make_cached_call(url, artist_id, token, params=params)

    items = resp_json["items"]
    for item in items:
        if (
            item["album_type"] != "compilation"
            and item["artists"][0]["name"] != "Various Artists"
        ):
            new_album = data.Album(item["id"])
            new_album.set_name(item["name"])
            albums.append(new_album)

    if resp_json["next"]:
        parsed_url = urllib.parse.urlparse(resp_json["next"])
        parsed_queries = urllib.parse.parse_qs(parsed_url.query)

        # This version is correct. It's being made incorrect below to
        # maintain access to cached values for analysis until
        # the rate limit is lifted
        new_offset = int(parsed_queries["offset"][0])

        new_offset = parsed_queries["offset"]
        get_albums_from_artist_id(
            artist_id, token, offset=new_offset, albums=albums
        )

    return albums


def get_album_tracks(
    album: data.Album,
    token: str,
    offset: int = 0,
    tracks: list[data.Track] = [],
):
    """
    Gets all tracks owned by a given Album object either from the API or local
    cache. Returns a list of Tracks. Requires an authentication token as
    a string.
    """

    url = "https://api.spotify.com/v1/albums/{}/tracks"
    album_id = album.get_id()

    params = {
        "limit": 50,
        "offset": offset,
    }

    resp_json = cache.make_cached_call(url, album_id, token, params=params)

    items = resp_json["items"]
    for item in items:
        new_track = data.Track(item["id"])
        new_track.set_name(item["name"])
        new_track.set_uri(item["uri"])

        for artist in item["artists"]:
            new_artist = data.Artist(artist["id"])
            new_artist.set_name(artist["name"])

            new_track.add_artist(new_artist)

        tracks.append(new_track)

    if resp_json["next"]:
        parsed_url = urllib.parse.urlparse(resp_json["next"])
        parsed_queries = urllib.parse.parse_qs(parsed_url.query)

        # This version is correct. It's being made incorrect below to
        # maintain access to cached values for analysis until
        # the rate limit is lifted
        new_offset = int(parsed_queries["offset"][0])

        new_offset = parsed_queries["offset"]

        get_album_tracks(album, token, offset=new_offset, tracks=tracks)

    return tracks
