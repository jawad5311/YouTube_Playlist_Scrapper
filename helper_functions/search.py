

def search(service,
           query: str,
           search_type: str = 'video,channel,playlist'):

    search_type = search_type.strip().lower()

    response = service.search().list(
        q=query,
        part='snippet',
        type=search_type,
        maxResults=50
    ).execute()

    ids = []

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
            raise KeyError(kind)

        ids.append(item_id)



