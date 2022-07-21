
import pandas as pd
import datetime as dt


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
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

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
        channel_title = item['snippet']['title']  # Channel Title
        channel_date = item['snippet']['publishedAt'][:10]  # Channel created date
        channel_date = dt.datetime.strptime(channel_date, '%Y-%m-%d')
        try:
            country = item['snippet']['country']  # Creator country
        except KeyError:
            country = 'NaN'
        channel_id = item['id']  # Channel ID
        channel_url = f'www.youtube.com/channel/{channel_id}'  # Channel URL
        try:
            # Custom URL of channel if available
            custom_url = item['snippet']['customUrl']
            custom_url = f'www.youtube.com/c/{custom_url}'
        except KeyError:
            custom_url = 'NaN'

        try:
            subs = item['statistics']['subscriberCount']  # No. of subscribers]
        except KeyError:
            item['statistics']['subscriberCount'] = '0'
            subs = item['statistics']['subscriberCount']

        vid_count = item['statistics']['videoCount']  # Total no. videos
        view_count = item['statistics']['viewCount']  # Total no. views

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


def filter_channels(data: list,
                    subs_min: int = 0,
                    subs_max: int = 1000000000,
                    min_vid_count: int = 0,
                    last_activity: int = 3650) -> list:
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
        subs_hidden = item['statistics']['hiddenSubscriberCount']
        vid_count = item['statistics']['videoCount']

        # If subs are hidden then add subscribers count = 0
        if subs_hidden:
            item['statistics']['subscriberCount'] = 'hidden'
        if int(vid_count) > min_vid_count:
            subs = item['statistics']['subscriberCount']
            if subs == '0':
                filtered_channels.append(item)
            if subs_min < int(subs) < subs_max:
                filtered_channels.append(item)

    print(f'Filtered Channels: {len(filtered_channels)}')
    return filtered_channels  # Returns list of filtered channels

