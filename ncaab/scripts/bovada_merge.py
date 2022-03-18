import os
import pandas as pd

if __name__ == "__main__":
    data_folder = os.path.dirname(__file__)
    data_folder = os.path.dirname(data_folder)
    data_folder = os.path.join(data_folder, "data", "bovada")
    df_next = pd.read_csv(os.path.join(data_folder, "next_events.csv"), index_col=0)
    df_last = pd.read_csv(os.path.join(data_folder, "last_events.csv"), index_col=0)
