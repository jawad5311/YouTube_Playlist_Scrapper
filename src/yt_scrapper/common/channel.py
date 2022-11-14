
import requests

import pandas as pd
import datetime as dt

from bs4 import BeautifulSoup

from .grab import _grab_channel_id
from .grab import _grab_channel_url
from .grab import _channel_subs_hidden
from .grab import _grab_channel_title_from_snippet
from .grab import _grab_channel_country_from_snippet
from .grab import _grab_channel_custom_url_from_snippet
from .grab import _grab_channel_subs_count_from_statistics
from .grab import _grab_channel_view_count_from_statistics
from .grab import _grab_video_duration_from_contentDetails
from .grab import _grab_channel_video_count_from_statistics
from .grab import _grab_channel_published_date_from_snippet
from .grab import _grab_channel_playlist_id_from_contentDetails


def get_channel_uploads_id(service, channel_id: str) -> str:
    """
    Retrieve channel uploads playlist id using YouTube channel id

    Parameters:
        service: YouTube Service Instance
        channel_id: YouTube channel's id
    Returns:
        str: playlist_id
    """

    request = service.channels().list(
        part='contentDetails',
        id=channel_id
    )

    response = request.execute()  # Send request and receive response

    # Extract playlist_id from the received response
    playlist_id = _grab_channel_playlist_id_from_contentDetails(response['items'][0])

    return playlist_id


def request_channels_data(service, channels_ids: []) -> list:
    """
    Request channel data using channel id and return list containing channel data
    Args:
        service: YouTube Service Instance
        channels_ids: list containing YouTube channels IDs'

    Returns:
        List containing channels data
    """
    channels_data = []  # Holds channels data

    # Creates id batches to request data and store response in list
    for batch_range in range(0, len(channels_ids), 50):
        # Create batches
        batch = channels_ids[batch_range: batch_range + 50]

        # Request channel data using channel id
        response = service.channels().list(
            part='snippet,statistics,contentDetails,brandingSettings',
            id=batch,
            maxResults=50,
        ).execute()

        channels_data.extend(response['items'])

    print(f'Total channels data received: {len(channels_data)}')

    return channels_data


def extract_channel_data(data: list) -> pd.DataFrame:
    """
    Extract channel information from the YouTube API response

    Parameters:
        data: List containing channels raw data received from YouTube API response

    Returns:
        Pandas DataFrame
    """

    channel_info = []  # Holds channel info
    for item in data:
        channel_title = _grab_channel_title_from_snippet(item)  # Channel Title
        channel_date = _grab_channel_published_date_from_snippet(item)  # Channel created date
        channel_date = dt.datetime.strptime(channel_date, '%Y-%m-%d')
        country = _grab_channel_country_from_snippet(item)  # Channel's Country
        channel_id = _grab_channel_id(item)  # Channel ID
        channel_url = _grab_channel_url(item)  # Channel URL
        custom_url = _grab_channel_custom_url_from_snippet(item)
        subs = _grab_channel_subs_count_from_statistics(item)
        vid_count = _grab_channel_video_count_from_statistics(item)  # Total no. videos
        view_count = _grab_channel_view_count_from_statistics(item)  # Total no. views

        # Append each info as a dict item into the list
        channel_info.append({
            'custom_URL': custom_url,
            'channel_URL': channel_url,
            'Title': channel_title,
            'Subs': subs,
            'Country': country,
            'email': '',
            'Channel_created_on': channel_date,
            'Total_Videos': vid_count,
            'Total_Views': view_count,
        })

    return pd.DataFrame(channel_info)


def filter_channels_by_criteria(data: list,
                                subs_min: int = 0,
                                subs_max: int = 1000000000,
                                min_vid_count: int = 0) -> list:
    """
        Filter channels based on no. of videos and subs count.

        Parameters:
            data: list,
                containing channels data
            subs_min: int
                Minimum number of subscribers a channel must have
            subs_max: int
                Maximum number of subscribers a channel must have
            min_vid_count: int
                Minimum number of videos a channel must have

        Returns:
            List containing filtered channels
    """
    filtered_channels = []

    # Filter channels and append them to list
    for item in data:

        # Check if subs are hidden and if hidden then add sub count '0'
        subs_hidden = _channel_subs_hidden(item)
        if subs_hidden:
            # set the channel subs count to 0
            item['statistics']['subscriberCount'] = '0'

        # Get channel's uploaded videos count
        vid_count = _grab_channel_video_count_from_statistics(item)
        if int(vid_count) > min_vid_count:
            subs = _grab_channel_subs_count_from_statistics(item)
            if item not in filtered_channels:
                if subs_hidden or subs_min < int(subs) < subs_max:
                    filtered_channels.append(item)

    print(f'Channels Dropped: {len(data) - len(filtered_channels)}')
    print(f'Channels Filtered: {len(filtered_channels)}')

    return filtered_channels  # Returns list of filtered channels


def filter_active_channels(service, data: list, activity: int = 21) -> list:
    """
        Filter channels based on their recent activity in no. of days

        Parameters:
            service: YouTube Service Instance
            data: List of channels data retrieved from YouTube API response
            activity: int -> Last activity of channel in no. of days

        Returns:
            List containing active channels
    """

    active_channels = []  # Holds active channels

    # Activity time from today
    activity_time = dt.datetime.now() - dt.timedelta(days=activity)

    for item in data:
        uploads = _grab_channel_playlist_id_from_contentDetails(item)
        response = service.playlistItems().list(
            part='contentDetails',
            playlistId=uploads,
            maxResults=1
        ).execute()

        # Grabs recent published video time
        vid_time = _grab_video_duration_from_contentDetails(response['items'][0])
        vid_time = dt.datetime.strptime(vid_time, '%Y-%m-%d')

        if vid_time >= activity_time:
            active_channels.append(item)

    print(f'In-active Channels Dropped: {len(data) - len(active_channels)}')
    print(f'Active Channels: {len(active_channels)}')

    return active_channels


def get_channel_id(channel_link: str) -> str:
    """
    Returns YouTube channel id from the channel link.

    Args:
        channel_link: YouTube channel url

    Returns:
        str: Channel ID
    """
    req = requests.get(channel_link)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup.find_all('meta', itemprop='channelId')[0]['content']


