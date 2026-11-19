import pandas as pd
from pathlib import Path


def load_history(path: str) -> pd.DataFrame:
    folder = Path(path)

    json_files = list(folder.glob("Streaming_History_Audio*.json"))

    full_data = pd.DataFrame()

    for file in json_files:
        added_data = pd.read_json(file)
        full_data = pd.concat(
            [full_data, added_data], axis=0, ignore_index=True
        )

    full_data = full_data.dropna(subset="spotify_track_uri")

    return full_data


def plays_per_container(df: pd.DataFrame, group_filter: str) -> pd.DataFrame:
    sorted_sizes = df.groupby(group_filter, as_index=False).size()
    sorted_sizes = sorted_sizes.sort_values("size", ascending=False)

    return sorted_sizes
