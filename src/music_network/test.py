import history
import collaboration

if __name__ == "__main__":
    # History Test
    df = history.load_history("Spotify Extended Streaming History")
    plays = history.plays_per_container(
        df, "master_metadata_album_artist_name"
    )
    plays = plays.reset_index(drop=True)

    # EDEN top artist?
    assert plays.loc[0, "master_metadata_album_artist_name"] == "EDEN"

    # API Test
    porter_robinson = "3dz0NnIZhtKKeXZxLOxCam"

    porter_collab = collaboration.make_collaboration_df(porter_robinson, "")

    # No self collaborations in the dataset?
    assert porter_robinson not in porter_collab["collaborator_id"]

    # Does ID exist in dataframe?
    ppg_spotify_id = "323YaufZaHurr9qFY93kr7"
    assert ppg_spotify_id in porter_collab["track_id"].values

    ppg_remix = porter_collab[porter_collab["track_id"] == ppg_spotify_id]
    ppg_remix = ppg_remix.reset_index()

    # Name match?
    expected = "Perfect Pinterest Garden - Ninajirachi & underscores Remix"
    assert ppg_remix["track_name"].loc[0] == expected

    # 2 collaborators (Ninajirachi & underscores)
    assert len(ppg_remix) == 2
