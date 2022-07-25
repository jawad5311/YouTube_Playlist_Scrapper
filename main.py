# Built-in Modules import
import os
from datetime import datetime, timedelta

# Installed Modules import
import pandas as pd
import dotenv

# Google API imports
from googleapiclient.discovery import build
import google_auth_oauthlib.flow

# Selenium imports
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException


# Project files import
from helper_functions import channel, video, playlist, search, helper_funcs


dotenv.load_dotenv()  # Loads .env file


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

    def extract_channel_videos(self,
                               channel_id: str,
                               filename: str):
        """
        Args:
            channel_id: ID of the YouTube Channel
            filename: Name of output file without extension

        Returns:
            Return CSV file containing channel all videos data

        Extract channel videos data using YouTube Channel ID and creates
        a CSV file in the current working directory
        """

        # Retrieve channel uploads ID
        channel_uploads_id = channel.get_channel_uploads_id(self.service, channel_id)

        # Retrieve Videos ID's based using channel upload playlist ID
        videos_ids = playlist.get_videos_id(self.service, channel_uploads_id)

        # Retrieve Videos Data
        videos_data = video.extract_videos_data(self.service, videos_ids)

        # Creates a CSV file in the current working directory
        helper_funcs.create_csv(videos_data, filename)

    def extract_videos_from_playlist(self,
                                     youtube_playlist: str,
                                     filename: str):
        """
        Args:
            youtube_playlist: YouTube playlist ID or playlist URL
            filename: Name of the output file without extension

        Returns:
            Creates a .csv file in the current working directory

        Extract all videos' information that are present in the playlist
        """

        # Grabs playlist id
        playlist_id = helper_funcs.extract_playlist_id(youtube_playlist)

        # Grabs videos ID's from playlist
        videos_ids = playlist.get_videos_id(self.service, playlist_id)

        # Retrieve videos data
        videos_data = video.extract_videos_data(self.service, videos_ids)

        # Creates a CSV file in the current working directory
        helper_funcs.create_csv(videos_data, filename)

    def extract_channels_by_keyword(self,
                                    search_query: str,
                                    filename: str = '',
                                    filter_channels: bool = False,
                                    subs_min: int = 0,
                                    subs_max: int = 1000000000,
                                    vid_count: int = 0,
                                    last_activity: int = 3650):
        """
        Search for channels by keyword and return data in .csv file

        Args:
            search_query: Your search keyword
            filename: File name to be saved with
            filter_channels: Filter channels based on criteria.
                If True, set values for (subs_min, subs_max, min_vid_count, last_activity)
            subs_min: Minimum number of subscribers a channel must have
            subs_max: Maximum number of subscribers a channel have
            vid_count: Minimum number of videos a channel must have
            last_activity: Last activity by channel in no. of days

        Returns:
            .csv file of all channels related to keyword
        """

        if not filename:
            filename = search_query.strip().lower()

        # Grabs channels id
        channel_ids = search.search_by_keyword(self.service, search_query, 'channel')

        # Request & extract channels' data
        channel_data = channel.request_channels_data(self.service, channel_ids)

        if filter_channels:
            channel.filter_channels_by_criteria(channel_data, subs_min, subs_max, vid_count)
            
        channel_data = channel.extract_channel_data(channel_data)

        # Creates a .csv file in the /data of current working directory
        helper_funcs.create_csv(channel_data, filename)

    # def extract_channels_by_criteria(self):
    #
    #     return

    def extract_videos_by_keyword(self,
                                  search_query: str,
                                  filename: str = ''):
        """
        Extract YouTube videos data by keyword and creates a .csv file
        Args:
            search_query: Your search keyword
            filename: Filename to be saved with

        Returns:
            .csv file at /data in the current working directory
        """

        if not filename:
            filename = search_query.strip().lower()

        # Grabs videos id's
        videos_ids = search.search_by_keyword(self.service, search_query, 'video')

        # Videos data
        videos_data = video.extract_videos_data(self.service, videos_ids)

        # Create .csv file at /data of current working directory
        helper_funcs.create_csv(videos_data, filename)


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

    def scrap_emails(self, data: pd.DataFrame):

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
                    self.add_data_to_dict(link, data, link_title, i)

                elif re.search('twitter.com', link):
                    link_title = 'Twitter'
                    self.add_data_to_dict(link, data, link_title, i)

                elif re.search('linkedin.com', link):
                    link_title = 'Linkedin'
                    self.add_data_to_dict(link, data, link_title, i)

                elif re.search('facebook.com', link):
                    link_title = 'Facebook'
                    self.add_data_to_dict(link, data, link_title, i)

                elif re.search('discord', link):
                    link_title = 'Discord'
                    self.add_data_to_dict(link, data, link_title, i)

                elif re.search('tiktok', link):
                    link_title = 'tiktok'
                    self.add_data_to_dict(link, data, link_title, i)

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
            order='relevance',
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

    def extract_comments_data(self, comments_data):

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

        comments_df = pd.DataFrame({
            'video_url': videos_url,
            'comment_id': comments_id,
            'comment_text': main_comments,
            'comment_date': main_comments_published,
            'comment_author': main_comments_authors,
            'comment_author_channel': main_comments_authors_url,
            'comment_replies': total_comment_replies,
        })

        comment_index = 0

        for comment in comments_data:
            comment_replies = int(comment['snippet']['totalReplyCount'])

            if comment_replies:
                replies_data = comment['replies']['comments']

                for i in range(len(replies_data)):
                    reply_id = replies_data[i]['id']
                    reply_text = replies_data[i]['snippet']['textDisplay']
                    reply_author = replies_data[i]['snippet']['authorDisplayName']
                    reply_channel = replies_data[i]['snippet']['authorChannelUrl']
                    reply_likes = replies_data[i]['snippet']['likeCount']
                    reply_added = replies_data[i]['snippet']['publishedAt']

                    self.add_data_to_dict(reply_id, comments_df, f'reply_id_{i}', comment_index)
                    self.add_data_to_dict(reply_text, comments_df, f'reply_text_{i}', comment_index)
                    self.add_data_to_dict(reply_author, comments_df, f'reply_author_{i}', comment_index)
                    self.add_data_to_dict(reply_channel, comments_df, f'reply_channel_{i}', comment_index)
                    self.add_data_to_dict(reply_likes, comments_df, f'reply_likes_{i}', comment_index)
                    self.add_data_to_dict(reply_added, comments_df, f'reply_added_{i}', comment_index)

            comment_index += 1

        return comments_df


if __name__ == '__main__':
    API_KEY = os.environ.get('API_KEY')

    yt = YouTube(API_KEY)
    # yt.sort_playlist_items('PLyR_eqaLz2hmBPeDYO3pyXaqexCIV-PGp',
    #                        'likes')

    # yt.extract_channel_videos('UCwKKyoOAhd7EE9pALtXoz_A', 'test_data')

    # yt.extract_videos_from_playlist(
    #     'https://www.youtube.com/playlist?list=PLs3IFJPw3G9KL3huzPS7g-0PCbS7Auc7I',
    #     'tkinter_tutorials'
    # )

    # yt.extract_channels_by_keyword('python')

    yt.extract_videos_by_keyword('youtube data api v3')
