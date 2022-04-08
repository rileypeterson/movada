if __name__ == "__main__":
    force = False
    if force:
        # Combine with past data
        pass
    else:
        df = pd.read_csv(".../dataset.csv")
        df_new = pd.read_csv("ncaab/data/odds/bovada/last_events.csv")
        # Find ones not in dataset
        # Only run to_bovada steps on those
        subprocess("python to_bovada")
        # Add output data to dataset by merging them together
        pass
