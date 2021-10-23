import pandas as pd
import re

from googleapiclient.discovery import build
import google_auth_oauthlib.flow
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

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
        upload_response():
            Retrieve all uploaded videos playlist's ID
        get_playlist_items():
            Retrieve all videos information from playlist
        get_videos_data():
            Extract each video data form the list of videos data
        get_channel_ids():
            Extract channel ids based on search query
        filter_channel():
            Filter channels based on video count and subscriptions
        filter_active_channels():
            Filter active channels based on their recent activity
        extract_channel_data():
            Extract channel data from the filtered channel list
        create_csv():
            Creates a csv file in current working directory
        convert_duration_to_seconds():
            convert youtube duration format into seconds
    """

    def __init__(self, key):
        API_SERVICE = 'youtube'
        API_VERSION = 'v3'
        self.api_service = API_SERVICE
        self.api_version = API_VERSION

        self.key = key
        self.service = self.construct_service()

        client_secrets_file = "secret_files/secret_key.json"
        self.client_secrets_file = client_secrets_file

        channel_ids = []
        self.channel_ids = channel_ids

        filtered_channels = []
        self.filtered_channels = filtered_channels

    def construct_service(self):
        """
        Creates service object from build method
        """

        # API_SERVICE = 'youtube'
        # API_VERSION = 'v3'
        service = build(
            self.api_service,
            self.api_version,
            developerKey=self.key
        )
        return service

    def oauth_service(self, scopes):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, scopes)

        credentials = flow.run_console()

        youtube = build(
            self.api_service,
            self.api_version,
            credentials=credentials)
        return youtube

    def upload_response(self, channel_id: str) -> str:
        """
        Send request to retrieve uploaded videos response as playlist ID.

            Parameters:
                channel_id: str
                    Channel's id required for request
            Returns:
                str: playlist_id
        """
        request = self.service.channels().list(
            part='contentDetails',
            id=channel_id
        )

        response = request.execute()  # Send request and receive response

        # Extract playlist_id from the received response
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        return playlist_id

    def get_playlist_items(self,
                           playlist_Id: str,
                           for_sort_by: bool = False) -> list or tuple:
        """
        Retrieve all videos information from playlist and returns list of
        videos information or tuple of (videos_id_in_playlist, videos_info)
        if for_sort_by is True.

        Parameters:
            playlist_Id: str
                Id of the playlist from which to retrieve data
            for_sort_by: bool
                Default (False): If to use this data to set

        Returns:
            List containing videos info
            if for_sort_by is True:
                Returns tuple of (videos_id_for_playlist, videos_info)
        """

        playlist_items = []

        # Adding KeyError exception handling for channel less than 50 videos
        try:
            # Create request to retrieve playlist items
            request = self.service.playlistItems().list(
                part='snippet',
                playlistId=playlist_Id,
                maxResults=50  # Max results per request (maximum: 50)
            )

            response = request.execute()  # Send request and receive response

            items = response['items']  # Grabs only videos info from the response
            playlist_items.extend(items)
            try:
                nextPageToken = response['nextPageToken']  # Grabs next page token
            except KeyError:
                nextPageToken = ''

            current_page = 1

            # Retrieve data while the next page is available
            while nextPageToken:
                request = self.service.playlistItems().list(
                    part='snippet',
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

        videos_id = [item['snippet']['resourceId']['videoId'] for item in
                     playlist_items]  # Holds all available videos id's

        videos_info = []  # Holds info about all available videos

        # Loop through all videos id's and retrieve info
        for batch_num in range(0, len(videos_id), 50):
            # Create batches of videos to request data
            videos_batch = videos_id[batch_num: batch_num + 50]  # Batch Size: 50

            # Send request to retrieve video's details
            response_videos = self.service.videos().list(
                # video details to be retrieved for each video
                part='contentDetails,snippet,statistics',
                id=videos_batch,
                maxResults=50
            ).execute()
            # batch items received from videos response
            batch_items = response_videos['items']
            # Adding batch items to videos_info list
            videos_info.extend(batch_items)

        if for_sort_by:
            videos_id_in_playlist = [item['id'] for item in playlist_items]
            return videos_id_in_playlist, videos_info

        return videos_info

    @staticmethod
    def get_videos_data(data: list) -> pd.DataFrame:
        """
        Creates a pandas dataframe from the data

        Parameters:
            data: list
                Data requested using get_playlist_items()

        Returns:
            Pandas DataFrame
        """

        columns = ['video_urls', 'titles', 'dates', 'views', 'durations', 'likes', 'dislikes', 'comments']

        # Create empty list for each column
        for _ in columns:
            # globals() function converts string to variable name
            globals()[_] = []

        for item in data:
            title = item['snippet']['title']
            date = item['snippet']['publishedAt'][:10]
            view = item['statistics']['viewCount']
            duration = item['contentDetails']['duration']

            try:
                like = item['statistics']['likeCount']
            except KeyError:
                item['statistics']['likeCount'] = '0'
                like = item['statistics']['likeCount']

            try:
                dislike = item['statistics']['dislikeCount']
            except KeyError:
                item['statistics']['dislikeCount'] = '0'
                dislike = item['statistics']['dislikeCount']

            try:
                comment = item['statistics']['commentCount']
            except KeyError:
                item['statistics']['commentCount'] = '0'
                comment = item['statistics']['commentCount']

            video_url = item['id']
            video_url = f'https://www.youtube.com/watch?v={video_url}'

            duration = YouTube.convert_duration_to_seconds(duration)

            video_urls.append(video_url)
            titles.append(title)
            dates.append(date)
            views.append(view)
            durations.append(duration)
            likes.append(like)
            dislikes.append(dislike)
            comments.append(comment)

        data = pd.DataFrame({
            'video_URL': video_urls,
            'title': titles,
            'uploadDate': dates,
            'views': views,
            'duration': durations,
            'likes': likes,
            'disLikes': dislikes,
            'commentsCount': comments
        })

        return data

    def get_channels_id(self, query: str, no_of_channels: int = 300) -> None:
        """
            Extract channels id's based on search query and add them to
            `self.ids`

            Parameters:
                query: str
                    Search query for which the request is to be made
                no_of_channels: int (default : 300)
                    No of channels to scrapped. No. of channel id's you
                    will get back might be less as same channel id's are
                    filtered out.

            Returns: None
                Add items to `self.ids` list

        """

        print(f'Total Channels found: {len(self.channel_ids)}')
        prev_length = len(self.channel_ids)

        search_response = []  # Holds search response

        # Request search
        response = self.service.search().list(
            part='snippet',
            q=query,
            maxResults=50
        ).execute()

        search_response.extend(response['items'])  # Add returned items to list
        next_page_token = response['nextPageToken']  # Grabs nextpage token
        # print(f'Next Page token: {next_page_token}')

        # Display current page that is being scrapped on terminal
        current_page = 1
        print(f'Current Page: {current_page}')
        channel_range = 0

        # Request search for 5 times
        while next_page_token:
            response = self.service.search().list(
                part='snippet',
                q=query,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            search_response.extend(response['items'])
            try:
                next_page_token = response['nextPageToken']
            except KeyError:
                next_page_token = False
            # print(f'Next Page token: {next_page_token}')
            channel_range += 50
            if current_page % 2 == 0:
                print(f'Current Page: {current_page}')
            if channel_range > no_of_channels:
                break

        channels_ids = []  # Holds channels id's

        # Loop through each item in search response and grabs channel id
        for item in search_response:
            channel_id = item['snippet']['channelId']  # Channel id
            # Add channel to the list if it is not already added
            if channel_id not in self.channel_ids:
                self.channel_ids.append(channel_id)

        print()
        print(f'Unique channels in this run: {len(self.channel_ids) - prev_length}')
        print()
        print(f'Total Channels found: {len(self.channel_ids)}')

    def request_channels_data(self) -> list:
        channels_data = []  # Holds channels data
        batch_size = 50  # No. channels to request data in single request

        # Creates id batches to request data and store response in list
        for batch_num in range(0, len(self.channel_ids), batch_size):
            # Create batches
            batch = self.channel_ids[batch_num: batch_num + batch_size]
            batch = ','.join(batch)  # Join id's with comma

            # Request channel data using channel id
            channel_response = self.service.channels().list(
                part='snippet,statistics,contentDetails,brandingSettings',
                id=batch,
                maxResults=batch_size,
            ).execute()

            channel_items = channel_response['items']
            channels_data.extend(channel_items)

        print()
        print(f'Total channels data requested: {len(channels_data)}')
        return channels_data

    @staticmethod
    def filter_channels(data: list,
                        subs_min: int = 1000,
                        subs_max: int = 1000000,
                        min_vid_count: int = 5) -> list:
        """
            Filter channels based on no. of videos and subs count.

            Parameters:
                data: list,
                    containing channels data
                subs_min: int
                    Minimum number of subscribers a channel must have
                subs_max: int
                    Maximum number of subscribers a channel must have
                min_vid_count: int
                    Minimum number of videos a channel must have

            Returns:
                List containing filtered channels
        """
        filtered_channels = []

        # Filter channels and append them to list
        for item in data:
            subs_hidden = item['statistics']['hiddenSubscriberCount']
            # If subs are hidden then add subscribers count = 0
            if subs_hidden:
                item['statistics']['subscriberCount'] = '0'
            vid_count = item['statistics']['videoCount']
            if int(vid_count) > min_vid_count:
                subs = item['statistics']['subscriberCount']
                if subs == '0':
                    filtered_channels.append(item)
                if subs_min < int(subs) < subs_max:
                    filtered_channels.append(item)
                # else:
                #     # item['statistics']['subscriberCount'] = '0'
                #     filtered_channels.append(item)

        print(f'Filtered Channels: {len(filtered_channels)}')
        return filtered_channels  # Returns list of filtered channels

    def filter_active_channels(self, data: list, activity: int = 21) -> list:
        """
            Filter channels based on their recent activity

            Parameters:
                data: list
                    List of channels retrieved from filter_channels()
                activity: int
                    Last activity of channel in no. of days

            Returns:
                list -> List containing active channels
        """
        active_channels = []  # Holds active channels
        current_item = 1

        # Go through each item in data and retrieve playlist id
        # Send request and retrieve playlist information
        # Fetch last uploaded video and retrieve its published date
        # See if the video is uploaded within activity days
        for item in data:
            uploads = item['contentDetails']['relatedPlaylists']['uploads']
            response = self.service.playlistItems().list(
                part='contentDetails',
                playlistId=uploads,
                maxResults=1
            ).execute()

            # Grabs recent published video time
            vid_time = response['items'][0]['contentDetails']['videoPublishedAt'][:10]
            vid_time = datetime.strptime(vid_time, '%Y-%m-%d')
            # Increment recent video time by no. of days activity
            vid_new_time = vid_time + timedelta(days=activity)

            # Current local time
            current_time = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.strptime(current_time, '%Y-%m-%d')

            # Displays no. of channels that are being filtered
            current_item += 1
            if current_item % 50 == 0:
                print(f'No. of active channels filtered: {current_item}')

            # If recent uploaded video is within the given timeframe
            # then append this video to the list
            if vid_new_time >= current_time:
                active_channels.append(item)

        print(f'Active Channels: {len(active_channels)}')
        return active_channels

    @staticmethod
    def extract_channel_data(data: list) -> pd.DataFrame:
        """
        Extract channel information from the data

        Parameters:
            data: list
                Data containing channels raw information

        Returns:
            Pandas DataFrame
        """
        channel_info = []
        for item in data:
            channel_title = item['snippet']['title']  # Channel Title
            channel_date = item['snippet']['publishedAt'][:10]  # Channel created date
            # channel_date = datetime.strptime(channel_date, '%Y-%m-%d')
            try:
                country = item['snippet']['country']  # Creator country
            except KeyError:
                country = 'NaN'
            channel_id = item['id']  # Channel ID
            channel_url = f'www.youtube.com/channel/{channel_id}'  # Channel URL
            try:
                # Custom URL of channel if available
                custom_url = item['snippet']['customUrl']
                custom_url = f'www.youtube.com/c/{custom_url}'
            except KeyError:
                custom_url = 'NaN'

            try:
                subs = item['statistics']['subscriberCount']  # No. of subscribers]
            except KeyError:
                item['statistics']['subscriberCount'] = '0'
                subs = item['statistics']['subscriberCount']

            vid_count = item['statistics']['videoCount']  # Total no. videos
            view_count = item['statistics']['viewCount']  # Total no. views

            # Append each info as a dict item into the list
            channel_info.append({
                'custom_URL': custom_url,
                'channel_URL': channel_url,
                'Title': channel_title,
                'Subs': subs,
                'Country': country,
                'email': '',
                'Channel_created_on': channel_date,
                'Total_Videos': vid_count,
                'Total_Views': view_count,
            })

        print(f'Pandas DataFrame created successfully!')

        return pd.DataFrame(channel_info)

    @staticmethod
    def scrap_emails(data: pd.DataFrame):

        def add_data(
                data: str,
                data_frame: pd.DataFrame,
                col_name: str,
                index: int):
            try:
                data_frame[col_name][index] = data
            except KeyError:
                data_frame[col_name] = ''
                data_frame[col_name][index] = data

        def extract_emails(text):
            return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome('chrome_driver/chromedriver.exe',
                                  options=chrome_options)
        other_links = []

        for i in range(len(channel_data)):

            url = f'https://{data.channel_URL[i]}/about'
            driver.get(url)

            country = driver.find_element_by_xpath(
                '//*[@id="details-container"]/table/tbody/tr[2]/td[2]/yt-formatted-string').text
            if country:
                data['Country'][i] = country

            description = driver.find_elements_by_id('description')
            description = description[1].text

            if description:
                email = extract_emails(description)
                email = ','.join(email)

                if email:
                    try:
                        data['email'][i] = email
                    except KeyError:
                        data['email'] = ''
                        data['email'][i] = email

                else:

                    try:
                        mail_available = driver.find_element_by_xpath(
                            '//*[@id="details-container"]/table/tbody/tr[1]/td[2]/yt-formatted-string/a').text
                        if mail_available:
                            mail_available = 'available'
                    except NoSuchElementException:
                        mail_available = 'NA'

                    try:
                        data['email_available'][i] = mail_available
                    except KeyError:
                        data['email_available'] = ''
                        data['email_available'][i] = mail_available

            else:
                try:
                    mail_available = driver.find_element_by_xpath(
                        '//*[@id="details-container"]/table/tbody/tr[1]/td[2]/yt-formatted-string/a').text
                    if mail_available:
                        mail_available = 'available'
                except NoSuchElementException:
                    mail_available = 'NA'

                try:
                    data['email_available'][i] = mail_available
                except KeyError:
                    data['email_available'] = ''
                    data['email_available'][i] = mail_available

            links_list = driver.find_elements_by_xpath('//*[@id="link-list-container"]/a')
            for item in links_list:
                link_title = item.text
                link = item.get_attribute('href')
                q_start_index = link.find('&q=') + 3
                link = link[q_start_index:].replace('%3A', ':').replace('%2F', '/')
                if re.search('instagram.com', link):
                    link_title = 'Insta'
                    add_data(link, data, link_title, i)

                elif re.search('twitter.com', link):
                    link_title = 'Twitter'
                    add_data(link, data, link_title, i)

                elif re.search('linkedin.com', link):
                    link_title = 'Linkedin'
                    add_data(link, data, link_title, i)

                elif re.search('facebook.com', link):
                    link_title = 'Facebook'
                    add_data(link, data, link_title, i)

                elif re.search('discord', link):
                    link_title = 'Discord'
                    add_data(link, data, link_title, i)

                elif re.search('tiktok', link):
                    link_title = 'tiktok'
                    add_data(link, data, link_title, i)

                elif re.search('youtube.com', link):
                    pass

                else:
                    other_links.append(link)

            if not i == 0:
                if i % 10 == 0:
                    print(f'No. of channels scrapped: {i}')

        print(f'Total channels scrapped: {i}')
        return data

    @staticmethod
    def filter_channels_by_keyword(search_pattern: str, data):
        for channel in data:
            try:
                description = channel['brandingSettings']['channel']['description']
            except KeyError:
                description = 'NA'

            try:
                keywords = channel['brandingSettings']['channel']['keywords']
                keywords = keywords.split('"')
                keywords = [_.strip() for _ in [_.strip() for _ in keywords] if _]
            except KeyError:
                keywords = []

            channel['brandingSettings']['channel']['keywords'] = keywords

            if re.search(search_pattern, description.lower()):
                if channel not in self.filtered_channels:
                    self.filtered_channels.append(channel)
                pattern_match = True
            else:
                pattern_match = False

            if not pattern_match:
                for word in keywords:
                    if re.search(search_pattern, word):
                        if channel not in self.filtered_channels:
                            self.filtered_channels.append(channel)

    def sort_playlist_items(self,
                            playlist_Id,
                            sort_by: str,
                            videos_to_sort: int = 5,
                            ascending: bool = False):

        sort_by_params = ['title', 'uploadDate', 'views', 'likes', 'disLikes', 'duration', 'commentsCount']
        if sort_by not in sort_by_params:
            raise Exception(
                f"'{sort_by}' is not an acceptable keyword \n\n"
                f"Please choose one of the following acceptable keywords: \n\n"
                f"{', '.join(sort_by_params)}"
            )

        item_id_in_playlist, playlist_items = self.get_playlist_items(playlist_Id,
                                                                      for_sort_by=True)
        videos_data = self.get_videos_data(playlist_items)

        videos_data['item_id_in_playlist'] = item_id_in_playlist

        videos_data.sort_values(sort_by,
                                axis=0,
                                ascending=ascending,
                                ignore_index=True,
                                inplace=True)

        if videos_to_sort >= len(videos_data):
            videos_to_sort = len(videos_data)

        scope = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        youtube = self.oauth_service(scopes=scope)

        for i in range(videos_to_sort):
            video_id = videos_data.video_URL[i][-11:]
            video_id_in_playlist = videos_data.item_id_in_playlist[i]
            body = {
                "snippet": {
                    "playlistId": "PLyR_eqaLz2hmBPeDYO3pyXaqexCIV-PGp",
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    },
                    "position": i
                },
                "id": video_id_in_playlist
            }

            youtube.playlistItems().update(
                part='snippet',
                body=body
            ).execute()

        print(f'Total Videos Sorted: {videos_to_sort}')

    def retrieve_channel_comments(self,
                                  channel_id: str) -> list:

        comments_data = []

        response = self.service.commentThreads().list(
            part='id,snippet,replies',
            allThreadsRelatedToChannelId=channel_id,
            maxResults=100
        ).execute()

        comments_data.extend(response['items'])
        try:
            next_page_token = response['nextPageToken']
        except KeyError:
            next_page_token = False

        while next_page_token:
            response = self.service.commentThreads().list(
                part='id,snippet,replies',
                allThreadsRelatedToChannelId=channel_id,
                pageToken=next_page_token,
                maxResults=100
            ).execute()

            comments_data.extend(response['items'])

            try:
                next_page_token = response['nextPageToken']
            except KeyError:
                next_page_token = False

        return comments_data

    @staticmethod
    def extract_comments_data(comments_data):

        videos_url = []
        comments_id = []
        main_comments = []
        main_comments_authors = []
        main_comments_authors_url = []
        main_comments_published = []
        total_comment_replies = []

        for comment in comments_data:
            comment_id = comment['id']
            video_id = comment['snippet']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            main_comment = comment['snippet']['topLevelComment']['snippet']['textDisplay']
            main_comment_author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            main_comment_author_url = comment['snippet']['topLevelComment']['snippet']['authorChannelUrl']
            main_comment_published = comment['snippet']['topLevelComment']['snippet']['publishedAt']

            # main_comment_time = datetime.strptime(main_comment_published, '%Y-%m-%d')
            main_comment_replies = int(comment['snippet']['totalReplyCount'])

            videos_url.append(video_url)
            comments_id.append(comment_id)
            main_comments.append(main_comment)
            main_comments_authors.append(main_comment_author)
            main_comments_authors_url.append(main_comment_author_url)
            main_comments_published.append(main_comment_published)
            total_comment_replies.append(main_comment_replies)

            # if main_comment_replies:
            #     replies_data = comment['replies']['comments']
            #     for i in range(len(replies_data)):
            #         globals()[f'reply_id_{i}'] = replies_data[i]['id']

    @staticmethod
    def create_csv(data: pd.DataFrame, filename: str) -> None:
        """
            Create a csv file in the current working directory.

            Parameters:
                data: Pandas Dataframe
                filename: str
                    Name by which to file is to be saved.
                    Note: provide file name without .csv

            Returns:
                None -> Create a csv file at the current working directory
        """
        print(f'Creating .csv file with name: {filename}')
        data.to_csv(f'{filename}.csv',
                    index=False)
        print(f'csv file created at location: {os.getcwd()}\\{filename}.csv')

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

        h = int(re.search('\d+H', duration)[0][:-1]) * 60 ** 2 if re.search('\d+H', duration) else 0
        m = int(re.search('\d+M', duration)[0][:-1]) * 60 if re.search('\d+M', duration) else 0
        s = int(re.search('\d+S', duration)[0][:-1]) if re.search('\d+S', duration) else 0
        return h + m + s


if __name__ == '__main__':
    API_KEY = os.environ.get('API_KEY')

    yt = YouTube(API_KEY)
    yt.sort_playlist_items('PLyR_eqaLz2hmBPeDYO3pyXaqexCIV-PGp',
                           'likes')
