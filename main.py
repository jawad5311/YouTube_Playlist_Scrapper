import pandas as pd
import re

from googleapiclient.discovery import build
from datetime import datetime, timedelta

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
    def __init__(self, key):
        # self.secret_file = secret_file
        self.key = key
        # self.scopes = scopes

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
    def get_playlist_items(service, playlist_Id: str) -> []:
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
        except KeyError as err:
            # If KeyError is for next page than continue the script
            if err == 'nextPageToken':
                print(f'Total Videos found: {len(playlist_items)}')
                pass
            else:
                raise

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
    def get_channel_ids(service, query: str) -> list:

        search_response = []

        response = service.search().list(
            part='snippet',
            q=query,
            maxResults=50
        ).execute()

        search_response.extend(response['items'])
        next_page_token = response['nextPageToken']
        print(f'Next Page token: {next_page_token}')

        for i in range(2):
            response = service.search().list(
                part='snippet',
                q=query,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            search_response.extend(response['items'])
            next_page_token = response['nextPageToken']
            print(f'Next Page token: {next_page_token}')

        print(f'search response len: {len(search_response)}')

        channels_ids = []

        for item in search_response:
            channel_id = item['snippet']['channelId']
            if channel_id not in channels_ids:
                channels_ids.append(channel_id)

        print(f'Unique channels id\'s: {len(channels_ids)}')

        return channels_ids

    @staticmethod
    def filter_channels(channels_ids: list) -> list:
        filtered_channels = []
        batch_size = 50

        for batch_num in range(0, len(channels_ids), batch_size):
            batch = channels_ids[batch_num: batch_num + batch_size]
            batch = ','.join(batch)

            channel_response = service.channels().list(
                part='snippet,statistics,contentDetails',
                id=batch,
                maxResults=batch_size,
            ).execute()

            for item in channel_response['items']:
                subs_hidden = item['statistics']['hiddenSubscriberCount']
                vid_count = item['statistics']['videoCount']
                if int(vid_count) > 20:
                    if not subs_hidden:
                        subs = item['statistics']['subscriberCount']
                        if 1000 < int(subs) < 100000:
                            filtered_channels.append(item)
                    else:
                        item['statistics']['subscriberCount'] = '0'
                        filtered_channels.append(item)

        return filtered_channels

    @staticmethod
    def filter_active_channels(service, channels: list, activity: int = 21) -> list:

        active_channels = []

        for item in channels:
            uploads = item['contentDetails']['relatedPlaylists']['uploads']
            response = service.playlistItems().list(
                part='contentDetails',
                playlistId=uploads,
                maxResults=1
            ).execute()

            vid_time = response['items'][0]['contentDetails']['videoPublishedAt'][:10]
            vid_time = datetime.strptime(vid_time, '%Y-%m-%d')
            vid_new_time = vid_time + timedelta(days=activity)

            current_time = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.strptime(current_time, '%Y-%m-%d')

            if vid_new_time >= current_time:
                active_channels.append(item)

        return active_channels


        # print(f'all channel ids in single string: {channels_ids}')

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
        """
        Creates a csv file of required data.

        Parameters:
            data: list
                Data requested using get_playlist_items()
            file_name: str
                Filename for the csv file
                Only provide filename without file format

        Returns:
            None: Saves a .csv file in the current directory
        """

        columns = ['titles', 'dates', 'views', 'durations', 'likes', 'dislikes', 'comments']

        # Create empty list for each column
        for _ in columns:
            # globals() function converts string to variable name
            globals()[_] = []

        for item in data:
            title = item['snippet']['title']
            date = item['snippet']['publishedAt'][:10]
            view = item['statistics']['viewCount']
            duration = item['contentDetails']['duration']
            like = item['statistics']['likeCount']
            dislike = item['statistics']['dislikeCount']
            comment = item['statistics']['commentCount']
            duration = YouTube.convert_duration_to_seconds(duration)

            titles.append(title)
            dates.append(date)
            views.append(view)
            durations.append(duration)
            likes.append(like)
            dislikes.append(dislike)
            comments.append(comment)

        data = pd.DataFrame({
            'Title': titles,
            'Upload_Date': dates,
            'Views': views,
            'Duration': durations,
            'Likes': likes,
            'DisLikes': dislikes,
            'Comments_Count': comments
        })

        data.to_csv(f'{file_name}.csv',
                    index=False)


if __name__ == '__main__':
    API_KEY = os.environ.get('API_KEY')

    yt = YouTube(API_KEY)
    service = yt.construct_service()

    # playlist_id = yt.upload_response(service, channel_id)
    # videos = yt.get_playlist_items(service, playlist_id)
    # yt.create_csv(videos, 'Brian_Design')

    yt.get_channel_list(service, 'how to')

