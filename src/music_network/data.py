"""
Jack K
This module implements class frameworks for Spotify data.
"""


class Artist:
    def __init__(self, artist_id) -> None:
        self._name: str = ""
        self._id = artist_id
        self._picture_url = ""

        self.albums: list[Album] = []

    def __eq__(self, value) -> bool:
        return self._id == value.id

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def get_picture_url(self) -> str:
        return self._picture_url

    def set_picture_url(self, url: str) -> None:
        self._picture_url = url

    def get_collaborators(self) -> set[Artist]:
        collaborators: set[Artist] = set()

        for album in self.albums:
            for artist in album.get_artists_in_album():
                if artist != self:
                    collaborators.add(artist)

        return collaborators

    def get_average_in_range(self, start, end):
        pass

    def add_album(self, album: Album):
        self.albums.append(album)


class Album:
    def __init__(self, album_id) -> None:
        self._id = album_id

        self._name = ""
        self._cover_url = ""
        self._type = ""

        self._tracks: list[Track]

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def get_type(self) -> str:
        return self._type

    def set_type(self, album_type: str) -> None:
        self._type = album_type

    def get_picture_url(self) -> str:
        return self._picture_url

    def set_picture_url(self, url: str) -> None:
        self._picture_url = url

    def add_track(self, track: Track) -> None:
        self._tracks.append(track)

    def get_tracks(self) -> list[Track]:
        return self._tracks

    def get_artists_in_album(self) -> list[Artist]:
        result: list[Artist] = []

        for track in self._tracks:
            artists = track.get_artists()

            for artist in artists:
                if artist not in result:
                    result.append(artist)

        return result


class Track:
    def __init__(self, track_id: str) -> None:
        self._id = track_id
        self._name = ""
        self._uri = ""

        self._album: Album
        self._artists: list[Artist] = []

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def get_uri(self) -> str:
        return self._uri

    def set_uri(self, uri: str) -> None:
        self._uri = uri

    def get_album(self) -> Album:
        return self._album

    def set_album(self, album: Album) -> None:
        self._album = album

    def add_artist(self, artist: Artist):
        self._artists.append(artist)

    def get_artists(self) -> list[Artist]:
        return self._artists

    def is_artist_id_in_track(self, artist_id) -> bool:
        for artist in self._artists:
            if artist_id == artist.get_id():
                return True
        return False

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name
