import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

import data
import api
import history

def make_collaboration_df(artist_id: str, token: str):
    artist_json = api.get_artist_from_id(artist_id, token)
    if artist_json:     
        artist_name = artist_json['name']
    else:
        return pd.DataFrame()

    #Get albums
    albums: list[data.Album] = api.get_albums_from_artist_id(artist_id, token)

    #Get tracks
    tracks: list[data.Track] = []
    for album in albums:
        new_tracks = api.get_album_tracks(album, token)
        for new_track in new_tracks:
            track_artists = new_track.get_artists()
            if(len(track_artists) > 1 and new_track.is_artist_id_in_track(artist_id)):
                tracks.append(new_track)

    rows = []

    for track in tracks:
            collaborators = track.get_artists()
            for collaborator in collaborators:
                if collaborator.get_id() != artist_id:
                    rows.append(
                        [collaborator.get_id(), collaborator.get_name(), track.get_name()]
                    )

    df = pd.DataFrame(rows)

    if df.empty != True:
        df.columns = ['collaborator_id', 'collaborator_name', 'track_name']
        df['artist_id'] = artist_id
        df['artist_name'] = artist_name

    return df

def make_collaboration_network(artist_id: str, token: str) -> nx.Graph:
    if token is None:
        return nx.empty_graph()

    print(f"Making network for {artist_id}")

    df = make_collaboration_df(artist_id, token)
    G = nx.from_pandas_edgelist(df, source='artist_name', target="collaborator_name")

    return G

def add_history_to_graph(G):
    df = history.load_history()

    sizes = history.plays_per_container(df, "master_metadata_album_artist_name")

    past_artists = df["master_metadata_album_artist_name"].unique()
    sizes = sizes.set_index("master_metadata_album_artist_name")

    for artist in G.nodes():
        if artist in past_artists:
            G.nodes[artist]["value"] = int(sizes.loc[artist, "size"])
        else:
            G.nodes[artist]["value"] = 0


def layout_to_ply(G: nx.Graph, pos:dict, filename:str = "network"):
    """
    Takes in a NetworkX graph G and 3D layout pos, and exports a 3D PLY file
    with an optional filename. The exported file contains verts representing 
    nodes, along with edges representing network edges. 
    """
    keys = list(pos.keys())

    header = [
        "ply",
        "format ascii 1.0",
        f"element vertex {len(keys)}",
        "property float x",
        "property float y",
        "property float z",
        "property float size",
        f"element edge {len(G.edges)}",
        "property int vertex1",
        "property int vertex2",
        "end_header"
    ]
    
    with open(f"{filename}.ply", "w+") as f:
        for line in header:
            f.write(line + '\n')
        for artist in keys:
            position = pos[artist]
            f.write(f"{position[0]} {position[1]} {position[2]} {G.nodes[artist]["value"]}\n")

        for edge in G.edges:
            v1 = keys.index(edge[0])
            v2 = keys.index(edge[1])
            f.write(f"{v1} {v2}\n")

    with open("indexes.csv", "w+") as f:
        for artist in keys:
            f.write(artist + "\n")


if __name__ == "__main__":
    token = api.authorize_client_credentials_flow()

    if token:
        artists = [
            "3dz0NnIZhtKKeXZxLOxCam", # Porter Robinson
            "4pb4rqWSoGUgxm63xmJ8xc", # Madeon
            "4zVCMnjw54nkhGHU4e1Pav", # isoXO
            "1SlTeYo2NYg93bGqlQYkwE", # Wavedash
            "6O4EGCCb6DoIiR6B1QCQgp", # Toro Y Moi
            "07UJz804RJxqNvxFXC3h9H", # Sam Gelliatry
            "7t8sK02zmZ9f6e6eJA9oSJ", # James Ivy
            "1t20wYnTiAT0Bs7H1hv9Wt", # EDEN
            "7HfUJxeVTgrvhk0eWHFzV7", # underscores
            "2HkSsS8O2U2gPhnCGVN5vn", # Between Friends
            "0fGcIStdT1OpFFhOC7Wp36", # Teezo Touchdown
            "2mQLwfvZtvtTbipKn3xHmK", # Erick the Architect
            "4QM5QCHicznALtX885CnZC", # Slayyyter
            "21mKp7DqtSNHhCAU2ugvUw", # ODESZA
            "7wg1qvie3KqDNQbAkTdbX0", # Louis the Child
            "3gIRvgZssIb9aiirIg0nI3", # Jeremy Zucker
            "2qxJFvFYMEDqd7ui6kSAcq", # Zedd
            "4oLeXFyACqeem2VImYeBFe", # Fred.. again,
            "4tZwfgrHOc3mvqYlEYSvVi", # Daft Punk
            "2NFrAuh8RQdQoS7iYFbckw", # The Midnight
            "3MekbRujJg5VZThubOlrkR", # Ninajirachi
            "49tQo2QULno7gxHutgccqF", # LANY
            "3mIj9lX2MWuHmhNCA7LSCW", # The 1975
            "1N9JxmOPJqhMCw219uoEi8", # Atlas in Motion
            "6R1kfr0GIWnwxY4zW11Vag", # Frost Children
        ]

        G = nx.empty_graph()
        for artist in artists:
            G = nx.compose(G, make_collaboration_network(artist, token))

        if(len(G) < 1):
            print("Recieved empty graph!")

        add_history_to_graph(G=G)

        pos = nx.spring_layout(G, dim=3, method="energy")
        layout_to_ply(G, pos, "export/new_network")

        net = Network(notebook=False, height="1500px", select_menu=True)
        net.from_nx(G)
    
        net.save_graph("nx.html")