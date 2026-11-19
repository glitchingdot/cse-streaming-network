import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

from pyvis.network import Network

import data
import api
import history


def make_collaboration_df(artist_id: str, token: str):
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

    Contains
    """

    df = pd.DataFrame()
    for artist in artists:
        collabs = make_collaboration_df(artist, token)
        df = pd.concat([df, collabs], ignore_index=True)

    return df


def node_attributes_from_history(G: nx.Graph) -> None:
    """
    Adds attributes to nodes in G from stored Spotify streaming history.
    If the artist has been listened to, their stream count is stored as
    a node's value. If not, their value is set to 0 and color is set to
    red.
    """
    df = history.load_history("Spotify Extended Streaming History")

    artist_container_name = "master_metadata_album_artist_name"

    sizes = history.plays_per_container(df, artist_container_name)

    past_artists = df[artist_container_name].unique()
    sizes = sizes.set_index(artist_container_name)

    for artist in G.nodes():
        if artist in past_artists:
            G.nodes[artist]["value"] = int(sizes.loc[artist, "size"])
        else:
            # Have not steamed this artists' primary songs before
            G.nodes[artist]["value"] = 0
            G.nodes[artist]["color"] = "red"


def remove_leaf_nodes(G: nx.Graph):
    """
    Takes in a graph G and removes any leaf nodes. Leaf nodes are nodes
    with only one collaborative partner.
    """
    G.remove_nodes_from(
        [n for n in G.nodes() if len(list(G.neighbors(n))) == 1]
    )


def make_pruned_network(df: pd.DataFrame, filepath: str):
    """
    Takes in a collaboration DataFrame and filepath and saves a
    pyvis interactive network visualization to the filepath. The
    generated network is pruned of leaf nodes. Leaf nodes are nodes
    with only one collaborative partner.
    """
    df = df.rename(columns={"track_name": "title", "play_count": "value"})

    G = nx.from_pandas_edgelist(
        df,
        source="artist_name",
        target="collaborator_name",
        edge_key="track_id",
        edge_attr=["title", "value"],
    )

    if len(G) < 1:
        print("Recieved empty graph!")

    remove_leaf_nodes(G=G)

    net = Network(notebook=False, height="1500px", select_menu=True)
    net.from_nx(G)

    print(f"Saved graph to {filepath}")
    net.save_graph(filepath)


def visualize_collaboration_counts(df: pd.DataFrame):
    partners = df.groupby(
        ["artist_name", "collaborator_name"], as_index=False
    ).size()

    partners["name"] = (
        partners["artist_name"]
        + "&"
        + partners["collaborator_name"]
    )
    partners["name"] = partners["name"].str.replace("$", "S", regex=False)
    partners = partners.sort_values("size", ascending=False)
    partners = partners.head(20)

    sns.catplot(partners, x="size", y="name", kind="bar")
    plt.show()


if __name__ == "__main__":
    token = api.authorize_client_credentials_flow()

    if token:
        artists = [
            "3dz0NnIZhtKKeXZxLOxCam",  # Porter Robinson
            "4pb4rqWSoGUgxm63xmJ8xc",  # Madeon
            "4zVCMnjw54nkhGHU4e1Pav",  # isoXO
            "1SlTeYo2NYg93bGqlQYkwE",  # Wavedash
            "6O4EGCCb6DoIiR6B1QCQgp",  # Toro Y Moi
            "07UJz804RJxqNvxFXC3h9H",  # Sam Gelliatry
            "7t8sK02zmZ9f6e6eJA9oSJ",  # James Ivy
            # "1t20wYnTiAT0Bs7H1hv9Wt", # EDEN
            "7HfUJxeVTgrvhk0eWHFzV7",  # underscores
            "2HkSsS8O2U2gPhnCGVN5vn",  # Between Friends
            "0fGcIStdT1OpFFhOC7Wp36",  # Teezo Touchdown
            "2mQLwfvZtvtTbipKn3xHmK",  # Erick the Architect
            "4QM5QCHicznALtX885CnZC",  # Slayyyter
            "21mKp7DqtSNHhCAU2ugvUw",  # ODESZA
            "7wg1qvie3KqDNQbAkTdbX0",  # Louis the Child
            "3gIRvgZssIb9aiirIg0nI3",  # Jeremy Zucker
            "2qxJFvFYMEDqd7ui6kSAcq",  # Zedd
            "4oLeXFyACqeem2VImYeBFe",  # Fred.. again,
            "4tZwfgrHOc3mvqYlEYSvVi",  # Daft Punk
            "2NFrAuh8RQdQoS7iYFbckw",  # The Midnight
            # "3MekbRujJg5VZThubOlrkR", # Ninajirachi (RATE NOT IN CACHE)
            # "49tQo2QULno7gxHutgccqF", # LANY
            # "3mIj9lX2MWuHmhNCA7LSCW", # The 1975
            # "1N9JxmOPJqhMCw219uoEi8", # Atlas in Motion
            # "6R1kfr0GIWnwxY4zW11Vag", # Frost Children (RATE NOT IN CACHE)
        ]

        df = make_artist_df(artists, token)
        # make_pruned_network(df, "nx.html")
        visualize_collaboration_counts(df)
