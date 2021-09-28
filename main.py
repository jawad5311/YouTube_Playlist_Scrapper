
from googleapiclient.discovery import build
import re

import os
import dotenv

dotenv.load_dotenv()


# Creating YouTube class to communicate with YouTube API
class YouTube:
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
        Retrieve channel's all videos information.

        Parameters:
            service: Instance of Create_Service()
                service object created using construct_service()
        """
        request = service.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_Id,
            maxResults=10
        )

        response = request.execute()

        playlist_items = response['items']
        nextPageToken = response['nextPageToken']

        current_page = 1

        while nextPageToken:
            request = service.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_Id,
                maxResults=10,
                pageToken=nextPageToken
            )

            response = request.execute()

            print(f'Current Page: {current_page}')
            current_page += 1

            playlist_items.extend(response['items'])
            nextPageToken = response.get('nextPageToken')

        videos_id = []

        for video_id in playlist_items:
            try:
                id = video_id['snippet']['resourceId']['videoId']
                videos_id.append(id)

            except KeyError:
                id = video_id['contentDetails']['videoId']
                videos_id.append(id)

        videos_info = []

        for batch_num in range(0, len(videos_id), 10):
            videos_batch = videos_id[batch_num: batch_num + 10]

            response_videos = service.videos().list(
                part='contentDetails,snippet,statistics',
                id=videos_batch,
                maxResults=10
            ).execute()

            batch_items = response_videos['items']

            videos_info.extend(batch_items)

        return videos_info

    @staticmethod
    def convert_duration(duration: str) -> int:
        h = int(re.search('\d+H', duration)[0][:-1]) * 60**2 if re.search('\d+H', duration) else 0
        m = int(re.search('\d+M', duration)[0][:-1]) * 60 if re.search('\d+M', duration) else 0
        s = int(re.search('\d+S', duration)[0][:-1]) if re.search('\d+S', duration) else 0
        return h + m + s


if __name__ == '__main__':
    API_KEY = os.environ.get('API_KEY')
    yt = YouTube(API_KEY)
    service = yt.construct_service()
    playlist_id = yt.upload_response(service, 'UCSJBJ3sP5GRUJMON12v28ew')

    videos = yt.get_playlist_items(service, playlist_id)

