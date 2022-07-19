

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


