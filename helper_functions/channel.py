

def get_channel_uploads_id(service, channel_id: str) -> str:
    """
        Parameters:
            channel_id: str
                YouTube channel's id
        Returns:
            str: playlist_id

        Retrieve channel uploads playlist id using YouTube channel id

    """

    request = service.channels().list(
        part='contentDetails',
        id=channel_id
    )

    response = request.execute()  # Send request and receive response

    # Extract playlist_id from the received response
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    return playlist_id




