

from .grab import _grab_next_page_token
from .grab import _grab_video_id_from_snippet
from .grab import _grab_video_date_from_contentDetails
from .grab import _grab_next_page_token
from .grab import _grab_next_page_token
from .grab import _grab_next_page_token


def get_videos_id(
        service,
        playlist_id: str) -> list or tuple:
    """
    Parameters:
        service: YouTube service instance
        playlist_id: Playlist id of YouTube channel

    Returns:
        List of playlist videos ids

    Retrieve all videos Id's from playlist.
    """

    video_ids = []

    # Adding KeyError exception handling for channel less than 50 videos
    try:
        # Create request to retrieve playlist items
        request = service.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50  # Max results per request (maximum: 50)
        )

        response = request.execute()  # Send request and receive response

        items = response['items']  # Grabs only videos info from the response

        for item in items:
            video_id = _grab_video_id_from_snippet(item)
            video_ids.append(video_id)

        try:
            next_page_token = _grab_next_page_token(response)  # Grabs next page token
        except KeyError:
            next_page_token = ''

        while next_page_token:
            request = service.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,  # max results per request (maximum: 50)
                pageToken=next_page_token
            )

            response = request.execute()  # Send request

            items = response['items']  # Grabs only videos info from the response

            for item in items:
                video_id = _grab_video_id_from_snippet(item)
                video_ids.append(video_id)

            next_page_token = _grab_next_page_token(response)

        print(f'Total Videos found: {len(video_ids)}')

    # If KeyError occurs, prints out the total videos found and pass the error
    except KeyError as err:
        # If KeyError is for next page than continue the script
        if err == 'nextPageToken':
            print(f'Total Videos found: {len(video_ids)}')
            pass
        else:
            raise

    return video_ids

