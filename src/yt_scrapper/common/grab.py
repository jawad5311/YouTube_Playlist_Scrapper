def _grab_channel_playlist_id_from_contentDetails(item) -> str:
    """
    Grab channel all uploads playlist id from channel response 'contentDetails'
    """
    return item['contentDetails']['relatedPlaylists']['uploads']


def _grab_channel_title_from_snippet(item) -> str:
    """
    Grabs channel title from channel response 'snippet'
    """
    return item['snippet']['title']


def _grab_channel_published_date_from_snippet(item) -> str:
    """
    Grabs channel published date from channel response 'snippet'
    """
    return item['snippet']['publishedAt'][:10]


def _grab_channel_country_from_snippet(item) -> str:
    """
    Grabs channel's country from channel response 'snippet'.
    If no country founds then returns NaN.
    """
    try:
        country = item['snippet']['country']  # Creator country
    except KeyError:
        country = 'NaN'

    return country


def _grab_channel_id(item) -> str:
    """
    Grabs channel id from channel response
    """
    return item['id']


def _grab_channel_url(item) -> str:
    """
    Grabs channel id from channel response and create channel link
    """
    channel_id = item['id']  # Channel ID
    return f'www.youtube.com/channel/{channel_id}'


def _grab_channel_custom_url_from_snippet(item) -> str:
    """
    Grabs channel custom name from channel response 'snippet' and create custom link. If no custom url found then
    returns NaN.
    """
    try:
        # Custom URL of channel if available
        custom_url = item['snippet']['customUrl']
        custom_url = f'www.youtube.com/c/{custom_url}'
    except KeyError:
        custom_url = 'NaN'

    return custom_url


def _grab_channel_subs_count_from_statistics(item) -> str:
    """
    Grabs channel's subscribers count from channel response 'statistics'. If channel subs are hidden then return 0.
    """
    try:
        subs = item['statistics']['subscriberCount']  # No. of subscribers]
    except KeyError:
        subs = '0'

    return subs


def _grab_channel_video_count_from_statistics(item) -> str:
    """
    Grabs channel total uploaded video count from channel response 'statistics'
    """
    return item['statistics']['videoCount']


def _grab_channel_view_count_from_statistics(item) -> str:
    """
    Grab channel total views count from channel response 'statistics'
    """
    return item['statistics']['viewCount']


def _channel_subs_hidden(item) -> bool:
    """
    Checks if the channel's subscriber count is hidden or not from channel response 'statistics'

    Returns:
            True if hidden, else False.
    """
    return item['statistics']['hiddenSubscriberCount']


def _grab_video_duration_from_contentDetails(item) -> str:
    """
    Grabs video duration from the playlistItems response 'contentDetails'
    """
    return item['contentDetails']['videoPublishedAt'][:10]

















