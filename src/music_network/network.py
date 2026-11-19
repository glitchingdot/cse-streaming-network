import pandas as pd
import networkx as nx
from pyvis.network import Network

import history


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
