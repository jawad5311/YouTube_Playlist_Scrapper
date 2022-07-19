

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
        kind = item['id']['kind']
        if kind == 'youtube#channel':
            item_id = item['id']['channelId']
        elif kind == 'youtube#video':
            item_id = item['id']['videoId']
        elif kind == 'youtube#playlist':
            item_id = item['id']['playlistId']
        else:
            # Raise KeyError if no item kind found
            raise KeyError(kind)

        if item_id not in ids:
            ids.append(item_id)  # Appends IDs' to the list

    if len(search_type) == 22:
        print(f'{len(ids)} items found in the search')
    else:


    return ids
