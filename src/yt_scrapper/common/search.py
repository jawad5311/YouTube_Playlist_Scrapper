

from .grab import _grab_next_page_token
from .grab import _grab_search_result_kind
from .grab import _grab_videoId_from_search
from .grab import _grab_channelId_from_search
from .grab import _grab_playlistId_from_search


def search_by_keyword(service,
                      query: str,
                      search_type: str = 'video,channel,playlist'):
    """
    Search on YouTube for channels, videos, and playlists for the provided keyword and return their IDs'
    Args:
        service: YouTube Service Instance
        query: Search query | Your search keyword
        search_type: Specify your search type. Acceptable keywords are channel, video, playlist.

    Returns:
        List of your selected type IDs'
    """

    # Strip and lower the string
    search_type = search_type.strip().lower()
    if search_type not in 'video,channel,playlist':
        raise Exception(f'{search_type} is not an acceptable keyword. Acceptable keywords are: '
                        f'video, channel, playlist')

    response = service.search().list(
        q=query,
        part='snippet',
        type=search_type,
        maxResults=50
    ).execute()

    ids = []  # Holds IDs'

    items = response['items']
    for item in items:
        kind = _grab_search_result_kind(item)
        if kind == 'youtube#channel':
            item_id = _grab_channelId_from_search(item)
        elif kind == 'youtube#video':
            item_id = _grab_videoId_from_search(item)
        elif kind == 'youtube#playlist':
            item_id = _grab_playlistId_from_search(item)
        else:
            # Raise KeyError if no item kind found
            raise KeyError(kind)

        if item_id not in ids:
            ids.append(item_id)  # Appends IDs' to the list

    try:
        next_page_token = _grab_next_page_token(response)
    except KeyError:
        next_page_token = False

    while next_page_token:
        response = service.search().list(
            q=query,
            part='snippet',
            type=search_type,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        items = response['items']
        for item in items:
            kind = _grab_search_result_kind(item)
            if kind == 'youtube#channel':
                item_id = _grab_channelId_from_search(item)
            elif kind == 'youtube#video':
                item_id = _grab_videoId_from_search(item)
            elif kind == 'youtube#playlist':
                item_id = _grab_playlistId_from_search(item)
            else:
                # Raise KeyError if no item kind found
                raise KeyError(kind)

            if item_id not in ids:
                ids.append(item_id)  # Appends IDs' to the list

        try:
            next_page_token = _grab_next_page_token(response)
        except KeyError:
            next_page_token = False

    if len(search_type) == 22:
        print(f'{len(ids)} items found in the search')
    else:
        print(f'Total {search_type.capitalize()}\'s found: {len(ids)}')

    return ids
