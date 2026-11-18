import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from typing import Literal

def load_history() -> pd.DataFrame:
    folder = Path("Spotify Extended Streaming History")

    json_files = list(folder.glob("Streaming_History_Audio*.json"))

    full_data = pd.DataFrame()

    for file in json_files:
        added_data = pd.read_json(file)
        full_data = pd.concat([full_data, added_data], axis=0, ignore_index=True)

    return full_data

def plays_per_container(df: pd.DataFrame, group_filter: str) -> pd.DataFrame:
    sorted_sizes = df.groupby(group_filter, as_index=False).size()
    sorted_sizes = sorted_sizes.sort_values("size", ascending=False)

    return sorted_sizes

def visualize_top_container(df: pd.DataFrame, container: Literal["artist", "album", "track"], count: int):
    group_filter = "master_metadata_"

    if container == "artist":
        group_filter += "album_artist_name"
    elif container == "album":
        group_filter += "album_album_name"
    else:
        group_filter += "track_name"

    
    limited = plays_per_container(df, group_filter).head(count)

    sns.set_theme()

    g = sns.catplot(data=limited.head(count), kind="bar", x='size', y=group_filter)

    g.set_axis_labels(y_var=container)
    g.tight_layout()

    plt.show()

if __name__ == "__main__":
    history = load_history()

    print(history.head(1))

    visualize_top_container(history, "artist", 50)