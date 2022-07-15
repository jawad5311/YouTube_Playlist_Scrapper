import re
import os
import pandas as pd


def convert_duration_to_seconds(duration: str) -> int:
    """
    Converts video duration to seconds

    Parameters:
        duration: str ->.
            time duration in format '00H00M00S'

    Returns:
        int: total number of seconds
    """

    h = int(re.search('\d+H', duration)[0][:-1]) * 60 ** 2 if re.search('\d+H', duration) else 0
    m = int(re.search('\d+M', duration)[0][:-1]) * 60 if re.search('\d+M', duration) else 0
    s = int(re.search('\d+S', duration)[0][:-1]) if re.search('\d+S', duration) else 0
    return h + m + s


def create_csv(data: pd.DataFrame, filename: str) -> None:
    """
        Create a csv file in the current working directory.

        Parameters:
            data: Pandas Dataframe
            filename: str
                Name by which to file is to be saved.
                Note: provide file name without .csv

        Returns:
            Create a csv file at the current working directory
    """
    print(f'Creating .csv file with name: {filename}')
    data.to_csv(f'{filename}.csv',
                index=False)
    print(f'csv file created at: {os.getcwd()}\\{filename}.csv')


def add_data_to_dataframe(
        data: str,
        data_frame: pd.DataFrame,
        col_name: str,
        index: int):
    """
    Args:
        data: Data that is needed to add to the dict
        data_frame: Pandas dataframe in which the data needs to add
        col_name: Column name in dataframe
        index: Index at which data needs to be added

    Returns:
        Modifies existing dataframe

    Use to add data to pandas dataframe with KeyError exception handling
    """
    try:
        data_frame[col_name][index] = data
    except KeyError:
        data_frame[col_name] = ''
        data_frame[col_name][index] = data


def extract_playlist_id(url):
    """
    Args:
        url: YouTube playlist url

    Returns:
        YouTube Playlist ID

    Extracts YouTube playlist ID from the playlist url...
    """
    url = url.replace('/', '')
    if len(url) != 34:
        # grabs playlist ID in the url
        url = re.search(
            '(?<=list=)[a-zA-z0-9-_]+',  # re pattern to extract playlist ID
            url
        )[0]

    return url
