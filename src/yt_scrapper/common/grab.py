

"""Channel related functionality"""
"""
    The following section contains functions that are related to YouTube Service response 'channels'
"""


def _grab_channel_playlist_id_from_contentDetails(item) -> str:
    """
    Grab channel all uploads playlist id from response 'channels.contentDetails'
    """
    return item['contentDetails']['relatedPlaylists']['uploads']


def _grab_channel_title_from_snippet(item) -> str:
    """
    Grabs channel title from response 'channels.snippet'
    """
    return item['snippet']['title']


def _grab_channel_published_date_from_snippet(item) -> str:
    """
    Grabs channel published date from response 'channels.snippet'
    """
    return item['snippet']['publishedAt'][:10]


def _grab_channel_country_from_snippet(item) -> str:
    """
    Grabs channel's country from response 'channels.snippet'.
    If no country founds then returns NaN.
    """
    try:
        country = item['snippet']['country']  # Creator country
    except KeyError:
        country = 'NaN'

    return country


def _grab_channel_id(item) -> str:
    """
    Grabs channel id from response 'channel'
    """
    return item['id']


def _grab_channel_url(item) -> str:
    """
    Grabs channel id from response 'channels' and create channel link
    """
    channel_id = item['id']  # Channel ID
    return f'www.youtube.com/channel/{channel_id}'


def _grab_channel_custom_url_from_snippet(item) -> str:
    """
    Grabs channel custom name from response 'channels.snippet' and create custom link. If no custom url found then
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
    Grabs channel's subscribers count from response 'channels.statistics'. If channel subs are hidden then return 0.
    """
    try:
        subs = item['statistics']['subscriberCount']  # No. of subscribers]
    except KeyError:
        subs = '0'

    return subs


def _grab_channel_video_count_from_statistics(item) -> str:
    """
    Grabs channel total uploaded video count from response 'channels.statistics'
    """
    return item['statistics']['videoCount']


def _grab_channel_view_count_from_statistics(item) -> str:
    """
    Grab channel total views count from response 'channels.statistics'
    """
    return item['statistics']['viewCount']


def _channel_subs_hidden(item) -> bool:
    """
    Checks if the channel's subscriber count is hidden or not from response 'channels.statistics'

    Returns:
            True if hidden, else False.
    """
    return item['statistics']['hiddenSubscriberCount']


"""Video related functionality"""
"""
    The following section contains functions that are related to YouTube Service response 'videos'
"""

def _grab_video_id(item):
    """
    Grabs video id from the response 'videos'
    """
    return item['id']


def _create_video_url(item) -> str:
    """
    Grabs video id from response 'videos' and create video url
    """
    return f"https://www.youtube.com/watch?v={item['id']}"


def _grab_video_title_from_snippet(item) -> str:
    """
    Grabs video title from response 'videos.snippet'
    """
    return item['snippet']['title']


def _grab_video_upload_date_from_snippet(item) -> str:
    """
    Grabs video upload date from response 'videos.snippet'
    """
    return item['snippet']['publishedAt'][:10]


def _grab_video_views_from_statistics(item) -> str:
    """
    Grab video views from the response 'videos.statistics'
    """
    return item['statistics']['viewCount']


def _grab_video_duration_from_contentDetails(item) -> str:
    """
    Grab video duration from the response 'videos.contentDetails'
    """
    return item['contentDetails']['duration']


def _grab_video_likes_from_statistics(item) -> str:
    """
    Grab video likes from the response 'videos.statistics'. If likes hidden then return NaN.
    """
    try:
        likes = item['statistics']['likeCount']
    except KeyError:
        likes = 'NaN'

    return likes


def _grab_video_comment_count_from_statistics(item) -> str:
    """
    Grab no. of comments on a video from response 'videos.statistics'
    """
    try:
        comments = item['statistics']['commentCount']
    except KeyError:
        comments = '0'


"""Playlist related functionality"""
"""
    The following section contains functions that are related to YouTube Service response 'playlistItems'
"""


def _grab_video_id_from_snippet(item) -> str:
    """
    Grab video id from response 'playlistItems.snippet'
    """
    return item['snippet']['resourceId']['videoId']


def _grab_video_date_from_contentDetails(item) -> str:
    """
    Grabs video duration from the response 'playlistItems.contentDetails'
    """
    return item['contentDetails']['videoPublishedAt'][:10]







def _grab_next_page_token(response) -> str:
    """
    Grab next token from the YouTube Service response
    """
    try:
        next_page_token = response['nextPageToken']  # Grabs next page token
    except KeyError:
        next_page_token = ''

    return next_page_token









