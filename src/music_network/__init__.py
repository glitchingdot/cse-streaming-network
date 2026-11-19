import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import collaboration
import api

sns.set_theme()


def visualize_collaboration_counts(df: pd.DataFrame):
    partners = df.groupby(
        ["artist_name", "collaborator_name"], as_index=False
    ).size()

    partners["name"] = (
        partners["artist_name"] + " & " + partners["collaborator_name"]
    )
    partners["name"] = partners["name"].str.replace("$", "S", regex=False)
    partners = partners.sort_values("size", ascending=False)
    partners = partners.head(20)

    g = sns.catplot(
        partners, x="size", y="name", kind="bar", hue="artist_name"
    )

    g.figure.suptitle("Top 20 Most Common Artist Pairs")
    g.legend.set_title("Primary Artist")
    g.set_axis_labels("Songs Released Together", "Artist Names")

    plt.tight_layout()
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

        df = collaboration.make_artist_df(artists, token)
        # make_pruned_network(df, "nx.html")
        visualize_collaboration_counts(df)
