

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
            video_id = item['snippet']['resourceId']['videoId']
            video_ids.append(video_id)

        try:
            next_page_token = response['nextPageToken']  # Grabs next page token
        except KeyError:
            next_page_token = ''

        # current_page = 1

        # Retrieve data while the next page is available
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
                video_id = item['snippet']['resourceId']['videoId']
                video_ids.append(video_id)

            # print(f'Current Page: {current_page}')  # prints current page
            # current_page += 1

            # Add items to playlist_items that are retrieved from next page
            # playlist_items.extend(response['items'])
            next_page_token = response.get('nextPageToken')

        print(f'Total Videos found: {len(video_ids)}')

    # If KeyError occurs, prints out the total videos found and pass the error
    except KeyError as err:
        # If KeyError is for next page than continue the script
        if err == 'nextPageToken':
            print(f'Total Videos found: {len(video_ids)}')
            pass
        else:
            raise

    # videos_id = [item['snippet']['resourceId']['videoId'] for item in
    #              playlist_items]  # Holds all available videos id's

    return video_ids

    # videos_info = []  # Holds info about all available videos
    #
    # # Loop through all videos id's and retrieve info
    # for batch_num in range(0, len(videos_id), 50):
    #     # Create batches of videos to request data
    #     videos_batch = videos_id[batch_num: batch_num + 50]  # Batch Size: 50
    #
    #     # Send request to retrieve video's details
    #     response_videos = service.videos().list(
    #         # video details to be retrieved for each video
    #         part='contentDetails,snippet,statistics',
    #         id=videos_batch,
    #         maxResults=50
    #     ).execute()
    #     # batch items received from videos response
    #     batch_items = response_videos['items']
    #     # Adding batch items to videos_info list
    #     videos_info.extend(batch_items)
    #
    # if for_sort_by:
    #     videos_id_in_playlist = [item['id'] for item in playlist_items]
    #     return videos_id_in_playlist, videos_info
    #
    # return videos_info
