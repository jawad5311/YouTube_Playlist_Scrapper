import pandas as pd
from googleapiclient.discovery import build
import re

import os
import dotenv

dotenv.load_dotenv()


# Creating YouTube class to communicate with YouTube API
class YouTube:
    """
    Communicate with YouTube API

    ...

    Attributes:
        key: str
            Api key used to create service and authenticate user

    Methods:
        construct_service():
            Construct service using API_KEY
        upload_response():
            Retrieve all uploaded videos playlist's ID
        get_playlist_items():
            Retrieve all videos information from playlist
    """
    def __init__(self, key, scopes: list = None):
        # self.secret_file = secret_file
        self.key = key
        self.scopes = scopes

    # def construct_service(self):
    #     """
    #         Responsible for creating service instance from 'google.Create_Service'
    #     """
    #     API_SERVICE = 'youtube'
    #     API_VERSION = 'v3'
    #     service = Create_Service(self.secret_file, API_SERVICE, API_VERSION, self.scopes)
    #     return service

    def construct_service(self):
        """
        Creates service object from build method
        """

        API_SERVICE = 'youtube'
        API_VERSION = 'v3'
        service = build(
            API_SERVICE,
            API_VERSION,
            developerKey=self.key
        )
        return service

    @staticmethod
    def upload_response(service, channel_id: str) -> str:
        """
        Send request to retrieve uploaded videos response as playlist ID.

            Parameters:
                service: Instance of Create_Service()
                    service object created using construct_service()
                channel_id: str
                    Channel's id required for request
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

    @staticmethod
    def get_playlist_items(service, playlist_Id: str):
        """
        Retrieve all videos information from playlist.

        Parameters:
            service: Instance of Create_Service()
                service object created using construct_service()
            playlist_Id: str
                Id of the playlist from which to retrieve data

        Returns:
            List: contains information of all videos
        """

        global playlist_items

        # Adding KeyError exception handling for channel less than 50 videos
        try:
            # Create request to retrieve playlist items
            request = service.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_Id,
                maxResults=50  # Max results per request (maximum: 50)
            )

            response = request.execute()  # Send request and receive response

            playlist_items = response['items']  # Grabs only videos info from the response
            nextPageToken = response['nextPageToken']  # Grabs next page token

            current_page = 1

            # Retrieve data while the next page is available
            while nextPageToken:
                request = service.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_Id,
                    maxResults=50,  # max results per request (maximum: 50)
                    pageToken=nextPageToken
                )

                response = request.execute()  # Send request

                print(f'Current Page: {current_page}')  # prints current page
                current_page += 1

                # Add items to playlist_items that are retrieved from next page
                playlist_items.extend(response['items'])
                nextPageToken = response.get('nextPageToken')

            print(f'Total Videos found: {len(playlist_items)}')

        # If KeyError occurs, prints out the total videos found and pass the error
        except KeyError:
            print(f'Total Videos found: {len(playlist_items)}')
            pass

        videos_id = []  # Holds all available videos id's

        # Go through playlist items list and retrieve all videos id's
        for video_id in playlist_items:
            try:
                id = video_id['snippet']['resourceId']['videoId']
                videos_id.append(id)

            except KeyError:
                id = video_id['contentDetails']['videoId']
                videos_id.append(id)

        videos_info = []  # Holds info about all available videos

        # Loop through all videos id's and retrieve info
        for batch_num in range(0, len(videos_id), 50):
            # Create batches of videos to request data
            videos_batch = videos_id[batch_num: batch_num + 50]  # Batch Size: 50

            # Send request to retrieve video's details
            response_videos = service.videos().list(
                # video details to be retrieved for each video
                part='contentDetails,snippet,statistics',
                id=videos_batch,
                maxResults=50
            ).execute()
            # batch items received from videos response
            batch_items = response_videos['items']
            # Adding batch items to videos_info list
            videos_info.extend(batch_items)

        return videos_info

    @staticmethod
    def convert_duration_to_seconds(duration: str) -> int:
        """
        Converts video duration to seconds

        Parameters:
            duration: str ->.
                time duration in format '00H00M00S'

        Returns:
            int: total number of seconds
        """

        h = int(re.search('\d+H', duration)[0][:-1]) * 60**2 if re.search('\d+H', duration) else 0
        m = int(re.search('\d+M', duration)[0][:-1]) * 60 if re.search('\d+M', duration) else 0
        s = int(re.search('\d+S', duration)[0][:-1]) if re.search('\d+S', duration) else 0
        return h + m + s

    @staticmethod
    def create_csv(data: list, file_name: str) -> None:

        titles, dates, views, durations = [], [], [], []

        for item in data:
            title = item['snippet']['title']
            date = item['snippet']['publishedAt'][:10]
            view = item['statistics']['viewCount']
            duration = item['contentDetails']['duration']
            duration = YouTube.convert_duration_to_seconds(duration)

            titles.append(title)
            dates.append(date)
            views.append(view)
            durations.append(duration)

        data = pd.DataFrame({
            'Title': titles,
            'Upload_Date': dates,
            'Views': views,
            'Duration': durations
        })

        data.to_csv(f'{file_name}.csv',
                    index=False)


if __name__ == '__main__':
    API_KEY = os.environ.get('API_KEY')
    channel_id = 'UC8wZnXYK_CGKlBcZp-GxYPA'
    yt = YouTube(API_KEY)
    service = yt.construct_service()
    playlist_id = yt.upload_response(service, channel_id)

    videos = yt.get_playlist_items(service, playlist_id)

    yt.create_csv(videos, 'NeuralNine.csv')

